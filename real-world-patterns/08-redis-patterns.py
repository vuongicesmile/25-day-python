"""
Pattern 08: Redis Patterns — Cache, Pub/Sub, Slot Isolation

Redis trong production: không chỉ là cache.
vuonglearning dùng Redis cho: user cache, rate limiting, pub/sub events,
model config snapshot, và cross-pod stream coordination.

Interview: "How do you use Redis beyond simple caching?"
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import redis.asyncio as aioredis


# ── Pattern 1: Redis Slot Isolation ──────────────────────────
"""
Multi-service Redis: dùng database slots để tách data.
Redis có 16 slots mặc định (0-15).

VD từ vuonglearning:
- Slot 0: ilmuchat-api (user cache, rate limiting)
- Slot 1: ai-service (generation state)
- Slot 2: centralized config (shared across services)
- Slot 3: ops portal (sessions, admin state)

Tại sao không dùng 1 slot?
- Key collision giữa services
- Flush db/FLUSHDB xóa của service khác
- Monitoring: xem memory per service dễ hơn
"""

def get_redis_for_service(service: str) -> aioredis.Redis:
    """Mỗi service dùng slot riêng."""
    slot_map = {
        "api": 0,
        "ai": 1,
        "config": 2,
        "ops": 3,
    }
    slot = slot_map.get(service, 0)
    return aioredis.from_url(
        f"redis://localhost:6379/{slot}",
        decode_responses=True,
    )

# Production: key prefix cho multi-tenant (preview environments)
def make_key(key: str, prefix: str = "") -> str:
    """
    Thêm prefix để preview environments không conflict.
    preview-alice:user:123 vs user:123 (production)
    """
    return f"{prefix}:{key}" if prefix else key


# ── Pattern 2: Cache-Aside Pattern ───────────────────────────
"""
Phổ biến nhất. Application tự quản lý cache:
1. Check cache
2. Cache miss → query DB → store in cache
3. Cache hit → return cached value
"""

class UserCache:
    def __init__(self, redis: aioredis.Redis, ttl: int = 60):
        self.redis = redis
        self.ttl = ttl

    def _key(self, user_id: str) -> str:
        return f"user:{user_id}"

    async def get(self, user_id: str) -> dict | None:
        data = await self.redis.get(self._key(user_id))
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            # Corrupted cache → treat as miss
            await self.redis.delete(self._key(user_id))
            return None

    async def set(self, user_id: str, user_data: dict) -> None:
        """Best-effort cache — lỗi không block main flow."""
        try:
            await self.redis.setex(
                self._key(user_id),
                self.ttl,
                json.dumps(user_data, default=str),  # default=str cho UUID, datetime
            )
        except Exception:
            pass  # Cache failure is non-critical

    async def invalidate(self, user_id: str) -> None:
        await self.redis.delete(self._key(user_id))

    async def invalidate_pattern(self, pattern: str) -> None:
        """Xóa nhiều keys match pattern (chỉ dùng development!)"""
        # SCAN thay vì KEYS để không block Redis
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break


# ── Pattern 3: Rate Limiting ──────────────────────────────────
"""
Sliding window rate limiting với Redis.
Tốt hơn fixed window (không có burst issues).
"""

class SlidingWindowRateLimiter:
    """
    Mỗi request:
    1. Thêm timestamp hiện tại vào sorted set
    2. Xóa entries cũ hơn window
    3. Đếm entries còn lại
    4. Allow/deny dựa trên count
    """

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def is_allowed(
        self,
        key: str,          # VD: "ratelimit:email:test@example.com"
        limit: int,        # Số requests tối đa
        window_seconds: int,  # Trong bao nhiêu giây
    ) -> tuple[bool, dict]:
        now = time.time()
        window_start = now - window_seconds

        # Atomic Lua script (Redis single-threaded → no race conditions)
        script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)
        
        -- Count current entries
        local count = redis.call('ZCARD', key)
        
        if count < limit then
            -- Add current request
            redis.call('ZADD', key, now, now .. math.random())
            redis.call('EXPIRE', key, window_seconds)
            return {1, count + 1}  -- allowed, new count
        else
            return {0, count}  -- denied, current count
        end
        """

        result = await self.redis.eval(
            script,
            1,                    # Number of keys
            key,                  # KEYS[1]
            now,                  # ARGV[1]
            window_start,         # ARGV[2]
            limit,                # ARGV[3]
            window_seconds,       # ARGV[4]
        )

        allowed = bool(result[0])
        current_count = int(result[1])

        return allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "window_seconds": window_seconds,
        }


# ── Pattern 4: Pub/Sub cho Cross-Pod Events ──────────────────
"""
Khi chạy nhiều pods (K8s), cần broadcast events.
VD: User bị ban trên pod 1 → invalidate cache trên pod 2, 3, 4
"""

class EventBroadcaster:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self._channel = "app:events"

    async def publish(self, event_type: str, data: dict) -> None:
        message = json.dumps({"type": event_type, **data})
        await self.redis.publish(self._channel, message)

    async def subscribe(self, handlers: dict[str, Any]) -> None:
        """
        Listen cho events và dispatch tới handlers.
        Chạy trong background task.
        """
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self._channel)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                event = json.loads(message["data"])
                event_type = event.get("type")
                handler = handlers.get(event_type)
                if handler:
                    await handler(event)
            except Exception as e:
                logger.error("event.handler_error", extra={"error": str(e)})


# Ví dụ dùng:
broadcaster = EventBroadcaster(get_redis())

# Pod 1 - khi ban user:
await broadcaster.publish("user.banned", {"user_id": str(user.id)})

# Pod 2, 3, 4 - receive event và invalidate cache:
async def on_user_banned(event: dict) -> None:
    user_id = event["user_id"]
    await user_cache.invalidate(user_id)
    logger.info("cache.invalidated", extra={"user_id": user_id})

await broadcaster.subscribe({
    "user.banned": on_user_banned,
    "config.updated": on_config_updated,
})


# ── Pattern 5: Distributed Lock ──────────────────────────────
"""
Ngăn chặn race condition khi nhiều pods chạy cùng lúc.
VD: Memory synthesis chỉ chạy 1 lần cho mỗi user.
"""
import contextlib

@contextlib.asynccontextmanager
async def distributed_lock(
    redis: aioredis.Redis,
    key: str,
    timeout_seconds: int = 60,
):
    """
    Acquire lock, yield, release lock.
    Tự release sau timeout_seconds (tránh deadlock).
    """
    lock_key = f"lock:{key}"
    acquired = await redis.set(
        lock_key,
        "1",
        ex=timeout_seconds,
        nx=True,  # Only set if Not eXists
    )

    if not acquired:
        raise RuntimeError(f"Could not acquire lock: {lock_key}")

    try:
        yield
    finally:
        await redis.delete(lock_key)


# Dùng:
async def synthesize_memories(user_id: str) -> None:
    try:
        async with distributed_lock(redis, f"synthesis:{user_id}", timeout_seconds=120):
            # Chỉ 1 pod có thể chạy synthesis cho mỗi user
            await _do_synthesis(user_id)
    except RuntimeError:
        logger.info("synthesis.already_running", extra={"user_id": user_id})


# ── Key Interview Points ──────────────────────────────────────
"""
1. "Redis KEYS vs SCAN?"
   - KEYS: O(N), block Redis trong khi scan → không dùng production
   - SCAN: iterative cursor, non-blocking → always prefer

2. "Lua scripts trong Redis tại sao?"
   - Redis single-threaded: Lua script chạy atomically
   - Không cần Redis transactions (MULTI/EXEC)
   - Rate limiting cần atomic: check-then-set không thể bị interrupt
   - Alternative: WATCH + MULTI/EXEC (phức tạp hơn)

3. "Redis Pub/Sub vs Redis Streams?"
   - Pub/Sub: fire-and-forget, subscribers phải online để nhận
   - Streams: persistent, consumers có thể "replay" messages
   - Dùng Pub/Sub cho real-time notifications (cache invalidation)
   - Dùng Streams cho SSE resume (chunks cần persist ngắn hạn)

4. "Distributed lock với Redis?"
   - SET key value EX timeout NX (atomic SET if Not eXists)
   - EX = expire time (tránh deadlock nếu pod crash)
   - nx=True = chỉ set nếu key chưa tồn tại
   - Redlock algorithm cho multi-node Redis cluster

5. "Slot isolation vs key prefix?"
   - Slots: cứng, FLUSHDB chỉ flush slot đó
   - Key prefix: mềm, dễ implement, nhưng FLUSHDB xóa tất cả
   - Production multi-tenant: key prefix (preview-env:...)
   - Production multi-service: slots (giữa services)
"""
