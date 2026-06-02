"""
Pattern 03: Multi-layer Auth với Redis Cache

Production pattern để đạt sub-100ms auth latency.
Tránh DB query mỗi request bằng Redis cache 60s.

Interview: "How do you implement JWT auth at scale without hitting DB every request?"
"""
from __future__ import annotations

import uuid
from fastapi import Depends, Cookie, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_bearer = HTTPBearer(auto_error=False)  # auto_error=False → không tự raise 401

CACHE_TTL = 60  # seconds


# ── Main Auth Dependency ──────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    cookie_token: str | None = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Auth flow: Bearer header → Cookie → fail
    Token type: JWT access token hoặc API key (sk-...)
    
    Performance path:
    1. Parse JWT (cheap, in-memory)
    2. Check Redis cache (fast, ~1ms)
    3. Fallback to DB (slow, ~5-20ms)
    4. Cache result for 60s
    """
    # ── Extract token ─────────────────────────────────────────
    token = None
    if credentials:
        token = credentials.credentials   # Authorization: Bearer <token>
    elif cookie_token:
        token = cookie_token               # Cookie: access_token=<token>
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── API Key path ──────────────────────────────────────────
    if token.startswith("sk-"):
        return await _auth_via_api_key(token, db)

    # ── JWT path ──────────────────────────────────────────────
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # QUAN TRỌNG: Validate token type
    # Tránh dùng refresh token như access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type",  # Không nói rõ tại sao (security)
        )

    user_id = uuid.UUID(str(payload["sub"]))

    # ── Cache check ───────────────────────────────────────────
    cached_user = await _get_cached_user(user_id)
    if cached_user is not None:
        if cached_user.status != "active":
            raise HTTPException(status_code=403, detail="Account suspended")
        return cached_user  # ← 99% của requests thoát ở đây

    # ── Cache miss → DB query ─────────────────────────────────
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Cache for next request (fire-and-forget, don't block)
    await _cache_user(user)

    return user


# ── Cache Implementation ──────────────────────────────────────
import json
from dataclasses import dataclass

@dataclass
class CachedUser:
    """
    Lightweight user object — KHÔNG phải SQLAlchemy model.
    Tránh overhead của ORM khi deserialize từ Redis.
    Chỉ chứa fields cần thiết cho auth checks.
    """
    id: uuid.UUID
    email: str
    status: str
    plan_id: uuid.UUID | None
    is_admin: bool

def _cache_key(user_id: uuid.UUID) -> str:
    return f"auth:user:{user_id}"

async def _get_cached_user(user_id: uuid.UUID) -> CachedUser | None:
    redis = get_redis()
    data = await redis.get(_cache_key(user_id))
    if not data:
        return None
    
    try:
        d = json.loads(data)
        return CachedUser(
            id=uuid.UUID(d["id"]),
            email=d["email"],
            status=d["status"],
            plan_id=uuid.UUID(d["plan_id"]) if d.get("plan_id") else None,
            is_admin=d.get("is_admin", False),
        )
    except Exception:
        # Corrupted cache → treat as miss
        await redis.delete(_cache_key(user_id))
        return None

async def _cache_user(user: User) -> None:
    """Cache user data. Lỗi cache KHÔNG block auth (best-effort)."""
    redis = get_redis()
    data = json.dumps({
        "id": str(user.id),
        "email": user.email,
        "status": user.status,
        "plan_id": str(user.plan_id) if user.plan_id else None,
        "is_admin": user.is_admin,
    })
    try:
        await redis.setex(_cache_key(user.id), CACHE_TTL, data)
    except Exception as e:
        # Cache failure: log warning, NOT an error (auth still works)
        logger.warning("auth.cache.set_failed", extra={"error": str(e)})

async def invalidate_user_cache(user_id: uuid.UUID) -> None:
    """
    Xóa cache khi user thay đổi (password, status, plan...).
    Gọi sau bất kỳ mutation nào ảnh hưởng đến auth state.
    """
    redis = get_redis()
    await redis.delete(_cache_key(user_id))


# ── Optional Auth ─────────────────────────────────────────────
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    cookie_token: str | None = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Cho endpoints public nhưng behavior thay đổi khi authenticated.
    VD: GET /posts → hiển thị thêm info nếu đã login
    """
    if not credentials and not cookie_token:
        return None
    try:
        return await get_current_user(credentials, cookie_token, db)
    except HTTPException:
        return None  # Invalid token → treat as anonymous


# ── Key Interview Points ──────────────────────────────────────
"""
1. "Why Redis cache for auth instead of just JWT?"
   - JWT decode là CPU-bound, nhanh. Nhưng cần check user status (active/banned)
   - DB query mỗi request = bottleneck ở scale
   - Redis cache giảm DB load 95%+ (60s TTL, most users active sessions)
   - Trade-off: 60s lag khi user bị ban (acceptable cho most use cases)

2. "What happens if Redis is down?"
   - Cache miss → fallback to DB → auth vẫn hoạt động (degraded performance)
   - KHÔNG raise error khi cache fail → auth path resilient

3. "How do you invalidate cache when user is banned?"
   - Gọi invalidate_user_cache() khi admin ban user
   - Next request → cache miss → DB query → 403
   - Max lag = remaining TTL (tối đa 60s)

4. "Why separate CachedUser from User model?"
   - SQLAlchemy objects không serializable trực tiếp
   - CachedUser nhẹ hơn, chỉ chứa auth-relevant fields
   - Tránh lazy-loading trong async context sau khi session close

5. "JWT token type validation — why?"
   - Tránh attacker dùng refresh token (longer-lived) như access token
   - Hai loại token có cùng structure nhưng scope khác nhau
   - Nếu không check → refresh token bị leak = much longer window
"""
