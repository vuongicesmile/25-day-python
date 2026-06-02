"""
Pattern 05: Pure ASGI Middleware

Tại sao KHÔNG dùng BaseHTTPMiddleware?
- BaseHTTPMiddleware buffer toàn bộ request body vào memory
- Block streaming responses
- Overhead message-passing giữa các layers

Pure ASGI: trực tiếp intercept transport messages → hiệu quả hơn.

Interview: "What's the difference between BaseHTTPMiddleware and pure ASGI middleware?"
"""
from __future__ import annotations

from typing import Awaitable, Callable
from starlette.types import ASGIApp, Receive, Scope, Send, Message


# ── BAD: BaseHTTPMiddleware (tránh dùng) ─────────────────────
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# from starlette.responses import Response
#
# class BadMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next) -> Response:
#         # VẤN ĐỀ: call_next() buffer toàn bộ response vào memory
#         # Streaming responses bị break!
#         body = await request.body()  # Buffer toàn bộ request body
#         response = await call_next(request)
#         return response


# ── GOOD: Pure ASGI Middleware ────────────────────────────────
class RequestBodyLimitMiddleware:
    """
    Reject requests với body quá lớn (default: 10MB).
    
    Hoạt động ở transport layer — KHÔNG buffer vào memory.
    Chỉ đếm bytes và reject ngay khi vượt limit.
    
    Perfect cho AI APIs vì không block streaming responses.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB default
        exempt_paths: list[str] | None = None,
    ) -> None:
        self.app = app
        self.max_bytes = max_bytes
        self.exempt_paths = exempt_paths or ["/files/upload", "/audio"]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Chỉ xử lý HTTP requests (bỏ qua WebSocket, lifespan...)
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Exempt một số paths (file upload tự handle limit riêng)
        path: str = scope.get("path", "")
        if any(path.startswith(p) for p in self.exempt_paths):
            await self.app(scope, receive, send)
            return

        # ── Wrap receive để count bytes ───────────────────────
        bytes_received = 0

        async def receive_wrapper() -> Message:
            nonlocal bytes_received
            message = await receive()

            if message["type"] == "http.request":
                chunk = message.get("body", b"")
                bytes_received += len(chunk)

                if bytes_received > self.max_bytes:
                    # Reject ngay — không đọc thêm
                    raise _PayloadTooLargeError(self.max_bytes)

            return message

        try:
            await self.app(scope, receive_wrapper, send)
        except _PayloadTooLargeError as e:
            await _send_413_response(scope, receive, send, e.max_bytes)


class _PayloadTooLargeError(Exception):
    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes


async def _send_413_response(scope, receive, send, max_bytes: int) -> None:
    """Gửi 413 Payload Too Large response."""
    import json
    body = json.dumps({
        "error": {
            "code": "payload.too_large",
            "message": f"Request body exceeds {max_bytes // (1024*1024)}MB limit",
        }
    }).encode()

    await send({
        "type": "http.response.start",
        "status": 413,
        "headers": [
            [b"content-type", b"application/json"],
            [b"content-length", str(len(body)).encode()],
        ],
    })
    await send({
        "type": "http.response.body",
        "body": body,
        "more_body": False,
    })


# ── Middleware cho Logging ────────────────────────────────────
class RequestLoggingMiddleware:
    """Log mọi request với timing — pure ASGI style."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        import time
        start = time.perf_counter()
        status_code = 200

        # Wrap send để capture status code
        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "request",
                extra={
                    "method": scope.get("method", ""),
                    "path": scope.get("path", ""),
                    "status": status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )


# ── Đăng ký Middleware ────────────────────────────────────────
app = FastAPI()

# Thứ tự QUAN TRỌNG: middleware cuối cùng được thêm = chạy đầu tiên
app.add_middleware(RequestBodyLimitMiddleware, max_bytes=10_000_000)
app.add_middleware(RequestLoggingMiddleware)
# Request flow: Logging → BodyLimit → route handler
# Response flow: route handler → BodyLimit → Logging


# ── Key Interview Points ──────────────────────────────────────
"""
1. "ASGI triple (scope, receive, send) là gì?"
   - scope: metadata về request (path, method, headers, query)
   - receive: callable để đọc request body chunks (async generator)
   - send: callable để gửi response (status, headers, body)
   - Tất cả communication qua messages (dicts)

2. "Tại sao pure ASGI tốt hơn BaseHTTPMiddleware?"
   - BaseHTTPMiddleware wrap Request/Response objects
   - Phải buffer toàn bộ response vào memory để pass qua middleware
   - Pure ASGI: messages flow qua, không có buffering
   - SSE/WebSocket streaming vẫn hoạt động với pure ASGI

3. "nonlocal keyword trong receive_wrapper?"
   - bytes_received là variable trong outer scope (closure)
   - nonlocal cho phép inner function modify outer variable
   - Thay thế cho class attribute trong functional style

4. "Thứ tự middleware matters?"
   - add_middleware() thêm vào đầu stack
   - Middleware cuối cùng thêm = chạy đầu tiên
   - VD: Auth → RateLimit → Logging (thứ tự thêm ngược lại)
"""
