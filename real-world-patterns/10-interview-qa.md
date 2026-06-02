# Pattern 10: Interview Q&A — Từ Production Codebase

> Các câu hỏi thực tế hay bị hỏi trong phỏng vấn Senior/Mid-level Backend, kèm câu trả lời từ kinh nghiệm thực tế.

---

## Python / FastAPI

### Q: "Async vs Sync trong Python — khi nào dùng async?"

**A:** Async hữu ích cho **I/O-bound** operations — database, HTTP calls, file I/O. Khi code đang chờ I/O, event loop có thể chạy coroutine khác.

Không dùng async cho **CPU-bound** (image processing, ML inference) — dùng `ProcessPoolExecutor` hoặc tách ra service riêng.

```python
# I/O bound → async
async def get_user(user_id: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# CPU bound → sync + ThreadPoolExecutor
import asyncio
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor()

async def process_image(image_data: bytes) -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _cpu_process, image_data)
```

---

### Q: "N+1 query problem — how do you detect and fix?"

**A:** N+1 = 1 query để lấy list, sau đó N queries riêng cho mỗi item trong list.

**Detect:** Enable SQL logging (`echo=True` trong SQLAlchemy), đếm queries. Hoặc dùng `sqlalchemy.event` để log.

**Fix:** Eager loading với `selectinload()` hoặc `joinedload()`.

```python
# ❌ N+1: 1 query lấy books + N queries cho author
books = db.execute(select(Book)).scalars().all()
for book in books:
    print(book.author.name)  # Mỗi book → 1 query!

# ✅ Fix: selectinload
books = db.execute(
    select(Book).options(selectinload(Book.author))
).scalars().all()
for book in books:
    print(book.author.name)  # Không thêm query!
```

---

### Q: "How do you handle database migrations in production?"

**A:** Chúng tôi dùng Alembic với quy trình:

1. Dev tạo migration: `alembic revision --autogenerate -m "add_isbn_to_books"`
2. Review generated migration (đôi khi cần sửa)
3. CI validate: `alembic heads` phải return đúng 1 head (không có branch)
4. Deploy: migration chạy trước khi app start (`alembic upgrade head`)
5. Nếu migration fail → deployment fail → rollback tự động

**Tip:** Migration phải backward-compatible. Không DROP column trong cùng deploy với code remove column — làm 2 bước:
- Deploy 1: Remove code dùng column (app không cần column nữa)
- Deploy 2: Drop column

---

### Q: "How do you implement rate limiting?"

**A:** Sliding window với Redis Sorted Set + Lua script (atomic).

```python
# Lua script đảm bảo atomic: check count + add new entry
# không bị race condition giữa 2 operations
result = await redis.eval(script, 1, key, now, window_start, limit, window_seconds)
```

Keys: `ratelimit:ip:1.2.3.4`, `ratelimit:email:user@example.com`

Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`

---

### Q: "How do you test async FastAPI endpoints?"

```python
# conftest.py
@pytest.fixture
def client(db):
    """TestClient với test DB"""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:  # TestClient handle event loop
        yield c
    app.dependency_overrides.clear()

# test_books.py
def test_create_book_returns_201(client, author, category):
    response = client.post("/books/", json={
        "title": "Python 101",
        "author_id": author.id,
        "category_id": category.id,
    })
    assert response.status_code == 201
    assert response.json()["author"]["name"] == author.name
```

---

## System Design

### Q: "How do you design a streaming AI chat API?"

**A:**

```
Client → POST /chat/completions
         ↓
    ilmuchat-api
         ↓ (forward + relay)
    ai-service → LLM (stream)
         ↓
    SSE chunks back to client

Disconnect recovery:
- Background task continues reading LLM
- Chunks stored in ActiveStreamManager (in-memory pub/sub)
- Client reconnects with resume_stream=true
- Receives accumulated_content + new chunks
```

Key decisions:
- **SSE không phải WebSocket**: AI response là unidirectional (server→client), SSE đủ
- **Background task**: Đảm bảo LLM response hoàn tất dù client disconnect
- **Redis Streams**: Cho cross-pod stream sharing (khi multiple API pods)

---

### Q: "How do you scale this system?"

**A:**

```
Horizontal scaling:
- API pods: stateless (session trong DB + Redis), scale freely
- AI pods: CPU/GPU bound, scale based on queue depth

Redis:
- User cache (slot 0): distributed across API pods (same data)
- Stream state: pod-local (in-memory) → cross-pod via Redis Pub/Sub
- Rate limiting: shared Redis ensures global limits

Database:
- Read replicas cho analytics queries
- Connection pooling (PgBouncer) giảm DB connections
- Partition large tables (messages by created_at)
```

---

## React / Frontend

### Q: "How do you manage state in a large React app?"

**A:** Tách server state và client state:

- **Server state** (data từ API): TanStack Query
  - Automatic caching, background refresh, deduplication
  - Don't store API data in Zustand!
- **Client state** (UI state): Zustand
  - Auth state, modals, streaming state
  - Không serialize cần thiết

```typescript
// ❌ SAI: Store API data trong Zustand
const useUserStore = create((set) => ({
  users: [],
  fetchUsers: async () => {
    const users = await api.getUsers();
    set({ users }); // Duplicate source of truth!
  }
}));

// ✅ ĐÚNG: TanStack Query cho server data
const { data: users } = useQuery({
  queryKey: ["users"],
  queryFn: () => api.getUsers(),
});

// Zustand CHỈ cho UI state
const { isModalOpen, openModal } = useUIStore();
```

---

### Q: "How do you handle SSE streaming in React?"

```typescript
// hooks/use-chat-stream.ts
export function useChatStream(chatId: string) {
  const { appendContent, finishStreaming } = useChatStore();

  const startStream = useCallback(async (request: ChatRequest) => {
    const response = await fetch(`/api/chat/${chatId}/completions`, {
      method: "POST",
      body: JSON.stringify(request),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getAccessToken()}`,
        Accept: "text/event-stream",  // QUAN TRỌNG
      },
    });

    // ReadableStream để parse SSE
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n\n");

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = line.slice(6);
        if (data === "[DONE]") {
          finishStreaming(chatId);
          return;
        }
        const event = JSON.parse(data);
        if (event.choices?.[0]?.delta?.content) {
          appendContent(chatId, event.choices[0].delta.content);
        }
      }
    }
  }, [chatId]);

  return { startStream };
}
```

**Tại sao fetch + ReadableStream thay vì EventSource?**
- EventSource không hỗ trợ POST (chỉ GET)
- EventSource không hỗ trợ custom headers (không thể gửi Bearer token)
- fetch + ReadableStream: full control, hỗ trợ mọi HTTP method/headers

---

## Kinh Nghiệm Thực Tế — Mistakes & Lessons

### 1. Async context + SQLAlchemy lazy loading

```python
# ❌ Lỗi: Truy cập relationship sau khi session close
async def get_book(id: str, db: AsyncSession) -> dict:
    book = await db.get(Book, id)
    return {"title": book.title}

# Vấn đề: book.author bị lazy load → session đã close
print(book.author.name)  # MissingGreenlet error!

# ✅ Fix: Eager load hoặc access trong session context
book = await db.execute(
    select(Book).options(selectinload(Book.author)).where(Book.id == id)
)
```

### 2. expire_on_commit trong async

```python
# ❌ Không có expire_on_commit=False
SessionLocal = sessionmaker(autocommit=False, autoflush=False)
# Sau commit, mọi attributes bị expired
# Truy cập → lazy load → MissingGreenlet!

# ✅ Luôn set expire_on_commit=False cho async
SessionLocal = sessionmaker(
    expire_on_commit=False,  # ← QUAN TRỌNG
    autocommit=False,
    autoflush=False,
)
```

### 3. Race condition trong rate limiting

```python
# ❌ Không atomic
count = await redis.get("rate:user:123")
if int(count or 0) < limit:
    await redis.incr("rate:user:123")  # Race condition!

# ✅ Atomic với Lua script hoặc Redis transactions
```

### 4. BOLA vulnerability

```python
# ❌ Chỉ check ID
chat = await db.get(Chat, chat_id)

# ✅ Check ownership trong query
chat = await db.execute(
    select(Chat).where(Chat.id == chat_id, Chat.user_id == user.id)
)
```
