"""
Pattern 07: Security Patterns — Auth, BOLA, Token Lifecycle

Security patterns từ production AI SaaS.
Những lỗi hay gặp nhất trong technical interviews và real code.

Interview: "How do you prevent BOLA/IDOR in a REST API?"
"""
from __future__ import annotations


# ── Pattern 1: Ownership-Scoped Queries (BOLA Prevention) ────
"""
BOLA = Broken Object Level Authorization
IDOR = Insecure Direct Object Reference

Ví dụ lỗi:
GET /api/chats/123 → trả về chat của user khác nếu đoán đúng ID!
"""

# ❌ SAI: Chỉ check ID, không check ownership
async def bad_get_chat(chat_id: str, db: AsyncSession) -> Chat:
    chat = await db.execute(select(Chat).where(Chat.id == chat_id))
    return chat.scalar_one_or_none()
    # Bất kỳ user nào cũng có thể truy cập bất kỳ chat!

# ✅ ĐÚNG: Luôn filter theo user_id
async def get_chat_for_user(
    chat_id: str,
    user_id: str,  # MUST pass user context
    db: AsyncSession,
) -> Chat:
    result = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == user_id,  # ← Ownership check trong query
        )
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise NotFoundError("Chat", chat_id)  # 404, không 403 (anti-enumeration)
    return chat

# ✅ Hoặc: 2-step với explicit ownership check
async def get_chat_with_auth(chat_id: str, user: User, db: AsyncSession) -> Chat:
    chat = await repo.get_by_id(chat_id, db)
    if not chat:
        raise NotFoundError("Chat", chat_id)
    if str(chat.user_id) != str(user.id):
        raise NotFoundError("Chat", chat_id)  # 404, không 403!
        # QUAN TRỌNG: Trả về 404 thay vì 403
        # 403 confirm resource tồn tại → attacker biết ID hợp lệ
    return chat


# ── Pattern 2: Token Type Validation ─────────────────────────
"""
JWT có nhiều loại token với lifetime khác nhau:
- access token: 15 phút, dùng cho API calls
- refresh token: 30 ngày, chỉ dùng để lấy access token mới

Không validate token type → attacker dùng refresh token (longer-lived) 
như access token → serious security issue!
"""
import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(user_id: str, secret: str) -> str:
    payload = {
        "sub": user_id,
        "type": "access",           # ← Token type label
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def create_refresh_token(user_id: str, secret: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",          # ← Different type
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def validate_access_token(token: str, secret: str) -> dict | None:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        # PHẢI check token type
        if payload.get("type") != "access":
            return None  # Reject refresh tokens dùng như access
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ── Pattern 3: Refresh Token Lifecycle ───────────────────────
"""
Refresh token phải:
1. Stored hashed (SHA-256) trong DB — không store plaintext
2. httpOnly cookie — JavaScript không đọc được
3. Revoked khi: password change, logout, account deletion
4. NOT rotated (trade-off: simpler, tối đa 30 ngày exposure nếu bị leak)
"""
import hashlib
import secrets

def hash_token(token: str) -> str:
    """SHA-256 hash — không reversible, đủ cho lookup."""
    return hashlib.sha256(token.encode()).hexdigest()

async def create_session(user: User, db: AsyncSession) -> tuple[str, str]:
    """Tạo access + refresh token, lưu refresh hash vào DB."""
    access_token = create_access_token(str(user.id), settings.jwt_secret)
    refresh_token = secrets.token_urlsafe(64)  # Random, không phải JWT
    
    # Lưu hash, không phải plaintext
    session = UserSession(
        user_id=user.id,
        token_hash=hash_token(refresh_token),  # ← Hash only
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(session)
    await db.commit()
    
    return access_token, refresh_token

async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession,
) -> str | None:
    """Validate refresh token, return new access token."""
    token_hash = hash_token(refresh_token)
    
    result = await db.execute(
        select(UserSession)
        .where(
            UserSession.token_hash == token_hash,
            UserSession.expires_at > datetime.now(timezone.utc),
            UserSession.revoked_at == None,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        return None
    
    # Load user và check status
    user = await get_user_by_id(session.user_id, db)
    if not user or user.status != "active":
        return None
    
    return create_access_token(str(user.id), settings.jwt_secret)

async def revoke_all_sessions(user_id: str, db: AsyncSession) -> None:
    """Revoke tất cả refresh tokens — gọi khi đổi password, bị hack."""
    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked_at == None,
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await db.commit()
    await invalidate_user_cache(user_id)  # Clear Redis cache ngay


# ── Pattern 4: Anti-Enumeration ──────────────────────────────
"""
Không confirm resource tồn tại hay không với unauthorized users.

SAI:
GET /users/999 → 404 (user không tồn tại)
GET /users/1   → 403 (user tồn tại nhưng không có quyền)
→ Attacker biết user ID 1 là valid!

ĐÚNG: Luôn trả về 404 cho cả 2 trường hợp.
"""
import asyncio
import random

async def forgot_password(email: str, db: AsyncSession) -> None:
    """
    Reset password — không confirm email tồn tại hay không.
    Luôn return 204 No Content.
    """
    user = await get_user_by_email(email, db)
    
    if user:
        # Chỉ gửi email nếu tồn tại
        await send_reset_email(user)
    else:
        # Delay ngẫu nhiên để tránh timing attack
        # (attacker đo response time để biết email có tồn tại không)
        await asyncio.sleep(random.uniform(0.2, 0.7))
    
    # Luôn return 204, không cho biết email có tồn tại không
    return  # HTTP 204 No Content


# ── Pattern 5: Bcrypt 72-byte Truncation ─────────────────────
"""
Bcrypt silently truncates passwords tại 72 bytes.
"password123" == "password123" + "extra_chars" khi hash!

bcrypt 4.x: silent truncation
bcrypt 5.x: ValueError nếu input > 72 bytes

Production fix: pre-truncate + SHA-256 hash trước khi bcrypt.
"""
import bcrypt

def hash_password(password: str) -> str:
    """
    Safe password hashing:
    1. Encode to UTF-8
    2. Truncate tại 72 bytes (bcrypt limit)
    3. Hash với bcrypt
    """
    password_bytes = password.encode("utf-8")
    # Truncate để consistent giữa bcrypt versions
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    salt = bcrypt.gensalt(rounds=12)  # Cost factor 12 = ~300ms
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    """Verify với same truncation logic."""
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))


# ── Key Interview Points ──────────────────────────────────────
"""
1. "BOLA vs IDOR — same thing?"
   - BOLA (OWASP API4) = API-specific term
   - IDOR = web app term
   - Cùng vulnerability: access other users' resources via their ID
   - Fix: always include user_id in database queries

2. "Why 404 instead of 403 for unauthorized resources?"
   - 403 confirms resource EXISTS → information disclosure
   - Attacker can enumerate valid IDs
   - 404 for both "not found" and "not authorized" → no info leak
   - Exception: authenticated admin APIs can return 403

3. "Why hash refresh tokens?"
   - DB breach → hashed tokens are useless (can't use SHA-256 hash as token)
   - Plaintext breach → attacker has all refresh tokens → can impersonate all users
   - SHA-256 (not bcrypt) because tokens are random enough — no rainbow tables needed

4. "Cost factor 12 in bcrypt?"
   - Higher = slower to brute force
   - 12 ≈ 300ms on modern hardware (acceptable UX)
   - 10 = too fast (brute force more feasible)
   - 14+ = too slow (user experience suffers)
   - Increase as hardware gets faster

5. "Timing attacks — what are they?"
   - Attacker measures response time to infer info
   - "email found" path: 300ms (bcrypt verify)
   - "email not found" path: 1ms (quick return)
   - Fix: add random delay on "not found" path to match timing
"""
