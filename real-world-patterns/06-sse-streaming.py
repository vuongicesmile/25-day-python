"""
Pattern 06: SSE Streaming + Stream Resume (Disconnect Recovery)

Server-Sent Events cho AI chat với graceful disconnect handling.
Khi user refresh browser giữa chừng → server tiếp tục → client reconnect → resume.

Interview: "How do you handle real-time streaming when clients disconnect?"
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask


# ── Pattern 1: Basic SSE ──────────────────────────────────────
async def generate_sse_events(chat_id: str) -> AsyncGenerator[str, None]:
    """
    Generator tạo SSE events.
    Mỗi event = "data: {json}\n\n"
    """
    yield f"data: {json.dumps({'type': 'start', 'chat_id': chat_id})}\n\n"

    async for chunk in get_ai_response_chunks(chat_id):
        event = {
            "type": "content",
            "choices": [{"delta": {"content": chunk}}]
        }
        yield f"data: {json.dumps(event)}\n\n"

    yield "data: [DONE]\n\n"

@app.post("/chat/{chat_id}/completions")
async def stream_chat(chat_id: str):
    return StreamingResponse(
        generate_sse_events(chat_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


# ── Pattern 2: ActiveStreamManager (Production) ──────────────
class ActiveStreamManager:
    """
    In-memory pub/sub cho stream resume.
    
    Khi client disconnect giữa chừng:
    1. Background task tiếp tục đọc AI response
    2. Chunks được buffer vào accumulated_content + subscribers
    3. Client reconnect → nhận accumulated content + chunks mới
    
    Architecture:
    AI Service → Background Task → ActiveStreamManager → Reconnected Client
                                        ↓
                                  Accumulated Buffer (cho reconnect)
    """

    def __init__(self) -> None:
        self._streams: dict[str, StreamState] = {}
        self._lock = asyncio.Lock()

    async def register(self, chat_id: str) -> None:
        """Đăng ký stream mới."""
        async with self._lock:
            self._streams[chat_id] = StreamState(chat_id=chat_id)

    async def publish_chunk(self, chat_id: str, chunk: str) -> None:
        """Background task gọi method này để push chunk."""
        async with self._lock:
            state = self._streams.get(chat_id)
            if not state:
                return

            state.accumulated_content += chunk

            # Notify tất cả subscribers (reconnected clients)
            dead = []
            for queue in state.subscribers:
                try:
                    queue.put_nowait(chunk)
                except asyncio.QueueFull:
                    dead.append(queue)

            for q in dead:
                state.subscribers.discard(q)

    async def subscribe(self, chat_id: str) -> tuple[str, asyncio.Queue]:
        """
        Client reconnect gọi method này.
        Returns: (accumulated_so_far, queue_for_new_chunks)
        """
        async with self._lock:
            state = self._streams.get(chat_id)
            if not state:
                return None, None  # Stream not found

            queue = asyncio.Queue(maxsize=1000)
            state.subscribers.add(queue)
            return state.accumulated_content, queue

    async def mark_completed(self, chat_id: str) -> None:
        """Background task gọi khi AI response hoàn tất."""
        async with self._lock:
            state = self._streams.get(chat_id)
            if state:
                state.is_complete = True
                # Notify subscribers stream đã xong
                for queue in state.subscribers:
                    queue.put_nowait(None)  # None = sentinel (done)

    async def cleanup(self, chat_id: str, delay_seconds: int = 30) -> None:
        """Cleanup stream state sau khi clients đã nhận xong."""
        await asyncio.sleep(delay_seconds)
        async with self._lock:
            self._streams.pop(chat_id, None)


active_streams = ActiveStreamManager()


# ── Pattern 3: Streaming Endpoint với Background Task ─────────
@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat_id = str(request.chat_id)

    # ── Resume path ───────────────────────────────────────────
    if request.resume_stream:
        accumulated, queue = await active_streams.subscribe(chat_id)

        if queue is None:
            # Stream không còn active → báo client fetch từ DB
            return JSONResponse({
                "type": "stream_resume_fallback",
                "reason": "no_active_stream",
            })

        # Stream đang active → resume từ accumulated content
        return StreamingResponse(
            _resume_stream_events(accumulated, queue, chat_id),
            media_type="text/event-stream",
        )

    # ── Fresh stream ──────────────────────────────────────────
    await active_streams.register(chat_id)

    # Background task tiếp tục ngay cả khi client disconnect
    background = BackgroundTask(
        _relay_and_finalize,
        chat_id=chat_id,
        request=request,
        user_id=str(user.id),
    )

    return StreamingResponse(
        _primary_stream_events(chat_id, request),
        media_type="text/event-stream",
        background=background,
    )


async def _primary_stream_events(
    chat_id: str,
    request: ChatCompletionRequest,
) -> AsyncGenerator[str, None]:
    """
    Stream cho client ban đầu.
    Khi client disconnect → generator bị cancel.
    Nhưng background task (_relay_and_finalize) tiếp tục!
    """
    queue = asyncio.Queue(maxsize=1000)
    await active_streams.subscribe_primary(chat_id, queue)

    while True:
        chunk = await queue.get()
        if chunk is None:  # Done sentinel
            yield "data: [DONE]\n\n"
            break
        yield f"data: {chunk}\n\n"


async def _relay_and_finalize(
    chat_id: str,
    request: ChatCompletionRequest,
    user_id: str,
) -> None:
    """
    Background task — chạy độc lập với client connection.
    1. Gọi AI service
    2. Push chunks vào ActiveStreamManager
    3. Persist message vào DB khi hoàn tất
    4. Schedule cleanup
    """
    try:
        async for chunk in call_ai_service(request):
            await active_streams.publish_chunk(chat_id, chunk)

        # Persist message (TRƯỚC KHI mark_completed)
        await persist_assistant_message(chat_id, user_id)

        await active_streams.mark_completed(chat_id)
    except Exception as e:
        logger.error("stream.relay_failed", extra={"chat_id": chat_id, "error": str(e)})
        await active_streams.mark_completed(chat_id)
    finally:
        # Cleanup sau 30s (cho client có thời gian reconnect)
        asyncio.create_task(active_streams.cleanup(chat_id, delay_seconds=30))


# ── Key Interview Points ──────────────────────────────────────
"""
1. "Why SSE instead of WebSocket?"
   - SSE: unidirectional server→client, simpler, HTTP/1.1 compatible
   - WebSocket: bidirectional, requires upgrade, more complex
   - AI chat: server streams response, client sends new message via POST
   - SSE + POST = simpler than WebSocket for this use case

2. "How do you handle client disconnect mid-stream?"
   - Background task (BackgroundTask) không bị cancel khi client disconnect
   - StreamingResponse generator bị cancel, nhưng background vẫn chạy
   - Background push chunks vào ActiveStreamManager buffer
   - Client reconnect → lấy accumulated + subscribe cho chunks mới

3. "X-Accel-Buffering: no header?"
   - nginx mặc định buffer responses từ upstream
   - Header này disable nginx buffering cho SSE
   - Không có header → client nhận chunks theo batch, không real-time

4. "Cleanup strategy?"
   - Giữ stream state 30s sau khi complete
   - Client có 30s để reconnect và nhận full content
   - Sau 30s → garbage collected
   - Production: adjust delay dựa trên mobile network latency

5. "Why mark_completed AFTER persist?"
   - Tránh race condition: client reconnect nhận [DONE] trước khi DB có data
   - Sequence: persist → mark_completed → client gets done signal → fetch from DB works
"""
