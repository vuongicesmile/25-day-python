"""
Pattern 02: FastAPI Lifespan Context Manager

Cách HIỆN ĐẠI để quản lý startup/shutdown (thay thế @app.on_event deprecated).
vuonglearning dùng pattern này để: init DB pool, Redis, HTTP client,
background tasks, và fail-fast startup checks.

Interview question: "How do you handle app startup/shutdown in FastAPI?"
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI


# ── Pattern: Lifespan Context Manager ────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Quản lý toàn bộ lifecycle của application.
    
    Tại sao dùng contextmanager thay vì on_event?
    - on_event("startup") deprecated từ FastAPI 0.93
    - contextmanager rõ ràng hơn (startup / yield / shutdown)
    - Dễ test hơn
    - Guaranteed cleanup ngay cả khi startup fails
    """

    # ─── STARTUP PHASE ────────────────────────────────────────
    # Thứ tự quan trọng: dependency trước, user sau

    # 1. Database connection pool
    await init_database()
    
    # 2. Redis connection
    await init_redis(url=settings.redis_url)
    
    # 3. HTTP client (connection pooling)
    init_http_client()
    
    # 4. Fail-fast checks — CRASH trước khi accept requests
    # Nếu fail → pod unhealthy → K8s tự rollback deployment!
    await startup_checks()
    
    # 5. Background tasks (chỉ start sau khi infra ready)
    start_cleanup_task()
    start_redis_subscriber()   # Lắng nghe events từ services khác

    # ─── SERVE REQUESTS ───────────────────────────────────────
    yield  # App đang chạy — nhận requests ở đây

    # ─── SHUTDOWN PHASE (REVERSE ORDER) ───────────────────────
    # Luôn chạy dù startup có fail không
    stop_cleanup_task()
    stop_redis_subscriber()
    await shutdown_http_client()    # Chờ in-flight requests xong
    await shutdown_database()       # Close connection pool
    await shutdown_redis()


app = FastAPI(
    title="VuongLearning API",
    lifespan=lifespan,
)


# ── Fail-Fast Startup Checks ──────────────────────────────────
async def startup_checks() -> None:
    """
    Kiểm tra tất cả dependencies trước khi accept requests.
    
    CRITICAL → raise Exception → app crash → K8s rollback
    WARNING  → log warning → app vẫn chạy
    
    Tại sao quan trọng?
    - Phát hiện misconfiguration sớm (sai DB password, missing secret...)
    - K8s readiness probe fail → không nhận traffic
    - Tự động rollback deployment khi config sai
    """
    errors = []

    # CRITICAL: App không thể chạy nếu thiếu những này
    critical_checks = [
        ("JWT_SECRET", settings.jwt_secret, lambda v: len(v) >= 32),
        ("INTERNAL_API_KEY", settings.internal_api_key, lambda v: len(v) >= 20),
        ("DATABASE_URL", settings.database_url, lambda v: bool(v)),
    ]

    for name, value, validator in critical_checks:
        if not value or not validator(value):
            errors.append(f"CRITICAL: {name} invalid or missing")

    if errors:
        for error in errors:
            logger.critical(error)
        raise RuntimeError(f"Startup checks failed: {errors}")

    # Database connectivity
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        logger.info("startup.db_check.ok")
    except Exception as e:
        raise RuntimeError(f"Database unreachable: {e}") from e

    # Redis connectivity
    try:
        redis = get_redis()
        await redis.ping()
        logger.info("startup.redis_check.ok")
    except Exception as e:
        raise RuntimeError(f"Redis unreachable: {e}") from e

    # WARNING: App vẫn chạy nhưng feature bị degraded
    warning_checks = [
        ("AI_SERVICE_URL", settings.ai_service_url),
        ("SMTP_HOST", settings.smtp_host),
    ]
    for name, value in warning_checks:
        if not value:
            logger.warning(f"startup.check.warning: {name} not configured")


# ── Testing Lifespan ──────────────────────────────────────────
"""
Khi viết tests, cần mock lifespan:
"""
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient

@asynccontextmanager
async def test_lifespan(app: FastAPI):
    """Test lifespan dùng in-memory SQLite, mock Redis"""
    await init_test_database()
    yield
    await cleanup_test_database()

# Trong conftest.py:
# @pytest.fixture
# def app():
#     return FastAPI(lifespan=test_lifespan)
#
# @pytest.fixture  
# def client(app):
#     with TestClient(app) as c:
#         yield c


# ── Key Interview Points ──────────────────────────────────────
"""
1. "Why lifespan instead of on_event?"
   - on_event deprecated, lifespan là cách recommended từ FastAPI 0.93+
   - Cleanup guaranteed qua finally clause của contextmanager
   - Testable — có thể swap lifespan trong tests

2. "What's fail-fast startup?"
   - App crash ngay khi start nếu config sai
   - K8s deployment tự rollback khi pod không healthy
   - Tốt hơn: silent start với broken config → khó debug

3. "What's the reverse order in shutdown?"
   - Stop consumers trước → không nhận messages mới
   - Flush in-flight work
   - Close connections cuối cùng (sau khi work done)

4. "How do you test lifespan?"
   - Tạo test_lifespan riêng với in-memory resources
   - Override lifespan trong test fixture
   - Hoặc dùng TestClient context manager (tự trigger lifespan)
"""
