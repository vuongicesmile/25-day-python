# Real-World Engineering Patterns — vuonglearning Codebase

> Extracted từ một production AI chat application (Python FastAPI + React + K8s).
> Tất cả patterns này đều được tested ở scale và hay được hỏi trong phỏng vấn Senior/Mid-level.

## Modules

| Module | Topic | Level |
|---|---|---|
| [01](01-async-sqlalchemy.py) | Async SQLAlchemy 2.0 + Mapped Types | ⭐⭐⭐ |
| [02](02-fastapi-lifespan.py) | FastAPI Lifespan + Startup Checks | ⭐⭐⭐ |
| [03](03-auth-caching.py) | Multi-layer Auth với Redis Cache | ⭐⭐⭐⭐ |
| [04](04-exception-hierarchy.py) | Exception Hierarchy + Global Handler | ⭐⭐⭐ |
| [05](05-pure-asgi-middleware.py) | Pure ASGI Middleware (không BaseHTTPMiddleware) | ⭐⭐⭐⭐ |
| [06](06-sse-streaming.py) | SSE Streaming + Stream Resume | ⭐⭐⭐⭐ |
| [07](07-background-tasks.py) | Background Tasks + Cancellation | ⭐⭐⭐⭐ |
| [08](08-redis-patterns.py) | Redis Patterns (Cache, Pub/Sub, Slots) | ⭐⭐⭐ |
| [09](09-security-patterns.py) | Security: Auth, BOLA, Token Lifecycle | ⭐⭐⭐⭐ |
| [10](10-frontend-patterns.md) | Frontend: Zustand, TanStack Query, Auto-retry | ⭐⭐⭐ |

## Interview Questions mỗi pattern hay bị hỏi

- "Explain how you'd implement JWT auth with Redis caching"
- "How do you prevent N+1 queries in SQLAlchemy?"
- "What's the difference between BaseHTTPMiddleware and pure ASGI?"
- "How do you handle streaming responses when client disconnects?"
- "How do you structure exceptions in a large FastAPI app?"
