"""
Pattern 01: Async SQLAlchemy 2.0 với Mapped Types

Đây là cách viết SQLAlchemy HIỆN ĐẠI (2.0+) — khác hoàn toàn với 1.x.
Production codebase (vuonglearning) dùng pattern này cho toàn bộ models.

Interview question: "What's the difference between SQLAlchemy 1.x and 2.0?"
"""

from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Text, String, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


# ── Base Class ────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Model 1.x Style (OLD WAY — không dùng nữa) ───────────────
# class UserOld(Base):
#     __tablename__ = "users"
#     id = Column(UUID, primary_key=True)          # Không có type hint
#     email = Column(Text, nullable=False)         # Không biết type khi code
#     settings = Column(JSONB, default=dict)       # IDE không autocomplete được


# ── Model 2.0 Style (CURRENT — production standard) ──────────
class User(Base):
    """
    Mapped[] type hints = compile-time type safety.
    IDE biết user.email là str, không phải Any.

    Từ khoá quan trọng cần nhớ:
    - Mapped[T] = column với type T
    - mapped_column() = khai báo column options
    - server_default = default do DATABASE xử lý (không phải Python)
    - lazy="selectin" = eager load bằng SELECT IN (không phải JOIN)
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,      # Python-side default
    )
    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
    )
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # JSONB — semi-structured config (chỉ PostgreSQL)
    settings: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),  # DB default
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default="active",
    )

    # Timestamps — DB tự set
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),  # DB function, không phải Python
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(),  # Tự update khi record thay đổi
        nullable=True,
    )

    # Foreign Key với optional relationship
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships với lazy loading strategy
    plan: Mapped[Plan | None] = relationship(
        "Plan",
        lazy="selectin",         # Load cùng user trong 1 SELECT IN query
        # Không dùng lazy="joined" vì plan có thể None
    )
    mfa_config: Mapped[MFAConfig | None] = relationship(
        back_populates="user",
        uselist=False,           # 1-1 relationship
        cascade="all, delete-orphan",  # Xóa user → xóa mfa_config
        lazy="selectin",
    )

    # ── Dunder methods cho debugging ──────────────────────────
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


# ── Async Engine & Session ────────────────────────────────────
"""
KHÁC BIỆT LỚN với sync SQLAlchemy:
- create_async_engine() thay vì create_engine()
- AsyncSession thay vì Session
- async_sessionmaker thay vì sessionmaker
- Mọi query đều dùng await
"""

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname",
    # asyncpg là async driver cho PostgreSQL
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,   # Test connection trước khi dùng
    echo=False,           # True để log SQL (chỉ dev)
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Không expire objects sau commit (quan trọng!)
    autocommit=False,
    autoflush=False,
)


# ── FastAPI Dependency ────────────────────────────────────────
from typing import AsyncGenerator
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Query Examples ────────────────────────────────────────────
from sqlalchemy import select, update, delete

async def example_queries(db: AsyncSession):
    # SELECT * FROM users WHERE id = ?
    result = await db.execute(
        select(User).where(User.id == some_uuid)
    )
    user = result.scalar_one_or_none()

    # SELECT với eager load (đã config lazy="selectin" nên tự động)
    result = await db.execute(
        select(User)
        .where(User.status == "active")
        .limit(10)
    )
    users = result.scalars().all()

    # INSERT
    new_user = User(email="test@example.com", status="active")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # Reload để lấy id, created_at từ DB

    # UPDATE bulk (không load objects vào memory — hiệu quả hơn)
    await db.execute(
        update(User)
        .where(User.status == "inactive")
        .values(status="deleted")
    )
    await db.commit()


# ── Key Interview Points ──────────────────────────────────────
"""
Câu hỏi hay bị hỏi:

1. "What's lazy='selectin' vs lazy='joined'?"
   - selectin: 2 queries (SELECT users, SELECT plans WHERE id IN (...))
   - joined: 1 query với JOIN (có thể nhiều duplicate data)
   - Dùng selectin khi relationship có thể None hoặc nhiều items

2. "Why expire_on_commit=False?"
   - Mặc định SQLAlchemy expire tất cả attributes sau commit
   - Khi access attribute → lại query DB
   - Trong async, expired objects gây ra MissingGreenlet error
   - expire_on_commit=False giữ attributes sau commit

3. "server_default vs default?"
   - default: Python xử lý (chạy ở application layer)
   - server_default: Database xử lý (chỉ SQL string)
   - server_default tốt hơn cho timestamps (consistent với DB timezone)

4. "Why asyncpg instead of psycopg2?"
   - asyncpg: Pure async, nhanh hơn 2-3x
   - psycopg2: Sync, block event loop khi dùng trong async context
"""
