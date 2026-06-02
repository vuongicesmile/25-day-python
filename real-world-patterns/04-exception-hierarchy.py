"""
Pattern 04: Exception Hierarchy + Global Handler

Domain exceptions thay vì raise HTTPException khắp nơi.
Consistent error format cho FE, machine-readable error codes.

Interview: "How do you structure error handling in a large FastAPI app?"
"""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# ── Exception Hierarchy ───────────────────────────────────────
class AppError(Exception):
    """Base exception — tất cả domain errors đều kế thừa."""
    code: str = "app.error"
    
    def __init__(self, message: str, **extra):
        super().__init__(message)
        self.extra = extra   # Metadata thêm vào response


class AuthenticationError(AppError):
    """401 — Token invalid, expired, missing"""
    code = "auth.invalid"


class AuthorizationError(AppError):
    """403 — Authenticated nhưng không có quyền"""
    code = "auth.forbidden"


class NotFoundError(AppError):
    """404 — Resource không tồn tại"""
    code = "not_found"
    
    def __init__(self, resource: str, id: str | int | None = None):
        msg = f"{resource} not found"
        if id:
            msg = f"{resource} with id={id} not found"
        super().__init__(msg)


class ConflictError(AppError):
    """409 — Duplicate hoặc constraint violation"""
    code = "conflict"


class ValidationError(AppError):
    """422 — Business rule violation (khác với Pydantic validation)"""
    code = "validation.failed"


class QuotaExceededError(AppError):
    """429 — Rate limit hoặc quota exceeded"""
    code = "quota.exceeded"
    
    def __init__(self, message: str, retry_after: int = 60, resource: str = ""):
        super().__init__(message)
        self.retry_after = retry_after
        self.resource = resource


class ServiceUnavailableError(AppError):
    """503 — Upstream service down"""
    code = "service.unavailable"


# ── Status Code Map ───────────────────────────────────────────
_STATUS_MAP: dict[type[AppError], int] = {
    AuthenticationError:   status.HTTP_401_UNAUTHORIZED,
    AuthorizationError:    status.HTTP_403_FORBIDDEN,
    NotFoundError:         status.HTTP_404_NOT_FOUND,
    ConflictError:         status.HTTP_409_CONFLICT,
    ValidationError:       status.HTTP_422_UNPROCESSABLE_ENTITY,
    QuotaExceededError:    status.HTTP_429_TOO_MANY_REQUESTS,
    ServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


# ── Global Exception Handlers ─────────────────────────────────
def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        status_code = _STATUS_MAP.get(type(exc), 500)
        
        # Xây dựng error body cơ bản
        error_body: dict = {
            "code": exc.code,
            "message": str(exc)[:500],  # Truncate để tránh info leak
        }
        
        # Thêm metadata đặc biệt cho một số exception types
        if isinstance(exc, QuotaExceededError):
            error_body["retry_after"] = exc.retry_after
            error_body["resource"] = exc.resource
        
        # Headers đặc biệt
        headers: dict = {}
        if isinstance(exc, QuotaExceededError):
            headers["Retry-After"] = str(exc.retry_after)
        if isinstance(exc, AuthenticationError):
            headers["WWW-Authenticate"] = "Bearer"
        
        logger.info(
            "request.error",
            extra={
                "code": exc.code,
                "status": status_code,
                "path": str(request.url.path),
            }
        )
        
        return JSONResponse(
            status_code=status_code,
            content={"error": error_body},
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def pydantic_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Override Pydantic 422 format → consistent với AppError format."""
        errors = []
        for error in exc.errors():
            loc = [str(l) for l in error["loc"] if l != "body"]
            errors.append({
                "field": " → ".join(loc) if loc else "unknown",
                "message": error["msg"],
                "type": error["type"],
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation.input",
                    "message": "Input validation failed",
                    "details": errors,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all: log chi tiết, return generic message."""
        logger.error(
            "request.unhandled_error",
            exc_info=True,
            extra={"path": str(request.url.path), "method": request.method},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred",
                }
            },
        )


# ── Dùng trong Service ────────────────────────────────────────
class UserService:
    async def get_user(self, user_id: str, db) -> User:
        user = await user_repo.get_by_id(user_id, db)
        if not user:
            raise NotFoundError("User", user_id)  # ← Rõ ràng hơn HTTPException
        return user

    async def update_email(self, user_id: str, new_email: str, db) -> User:
        existing = await user_repo.get_by_email(new_email, db)
        if existing and existing.id != user_id:
            raise ConflictError(f"Email '{new_email}' already in use")
        # ...

    async def check_quota(self, user: User) -> None:
        if user.daily_tokens >= user.plan.token_limit:
            raise QuotaExceededError(
                "Daily token limit exceeded",
                retry_after=seconds_until_midnight(),
                resource="tokens",
            )


# ── Key Interview Points ──────────────────────────────────────
"""
1. "Why domain exceptions instead of raising HTTPException directly?"
   - Domain exceptions không phụ thuộc vào HTTP layer
   - Service code không biết về HTTP status codes → separation of concerns
   - Dễ test: raise exception, check message và code
   - Dễ thêm exception types mới (chỉ thêm vào _STATUS_MAP)
   - Reusable trong jobs, scripts, không chỉ HTTP handlers

2. "How do you avoid exposing internal errors to clients?"
   - Truncate messages ([:500])
   - Unhandled exceptions return generic "unexpected error"
   - Log internal details server-side, client nhận generic message

3. "Machine-readable error codes vs HTTP status codes?"
   - HTTP status = coarse-grained (401, 403, 404...)
   - error.code = fine-grained (auth.invalid_token, auth.token_expired, auth.mfa_required)
   - FE có thể show message phù hợp với error.code
   - Analytics: query logs theo error.code

4. "What's in the Retry-After header?"
   - RFC 7231: số giây client nên đợi trước khi retry
   - Quan trọng cho rate limiting implementation
   - Client-side: exponential backoff + respect Retry-After
"""
