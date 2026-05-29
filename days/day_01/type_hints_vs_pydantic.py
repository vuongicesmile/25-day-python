"""
Type Hints vs Pydantic — Runtime Enforcement
"""

# ============================================================
# PHẦN 1: Type Hints — KHÔNG enforce lúc runtime
# ============================================================

def add(a: int, b: int) -> int:
    return a + b

# Python hoàn toàn không quan tâm, không lỗi gì cả
print(add("hello", " world"))   # "hello world" — chạy ngon!
print(add(2.5, 3.1))            # 5.6 — float cũng chạy được

def get_user(user_id: int) -> dict[str, str]:
    return {"id": user_id, "name": "Vuong"}

# Truyền string vào int param — vẫn chạy
print(get_user("not_an_int"))   # {'id': 'not_an_int', 'name': 'Vuong'}


# ============================================================
# PHẦN 2: Pydantic — CÓ enforce lúc runtime
# ============================================================
# pip install pydantic

from pydantic import BaseModel, field_validator, ValidationError

class User(BaseModel):
    id: int
    name: str
    age: int
    email: str

# ✅ Valid data — OK
user = User(id=1, name="Vuong", age=25, email="vuong@example.com")
print(user)
print(user.id, type(user.id))   # 1 <class 'int'>

# ✅ Pydantic tự coerce nếu có thể
user2 = User(id="42", name="Alice", age="30", email="alice@example.com")
print(user2.id, type(user2.id))  # 42 <class 'int'> — "42" → 42 tự động!

# ❌ Dữ liệu sai hoàn toàn — raise ValidationError
try:
    bad_user = User(id="not_a_number", name="Bob", age=25, email="bob@example.com")
except ValidationError as e:
    print("\nValidationError caught:")
    print(e)


# ============================================================
# PHẦN 3: Pydantic với custom validator
# ============================================================

class Product(BaseModel):
    name: str
    price: float
    stock: int

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price phải lớn hơn 0")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name không được rỗng")
        return v.strip()

# ✅ Valid
p = Product(name="Laptop", price=999.99, stock=10)
print(f"\nProduct: {p.name} — ${p.price}")

# ❌ Invalid price
try:
    Product(name="Laptop", price=-100, stock=10)
except ValidationError as e:
    print(f"Error: {e.errors()[0]['msg']}")

# ❌ Empty name
try:
    Product(name="   ", price=100, stock=5)
except ValidationError as e:
    print(f"Error: {e.errors()[0]['msg']}")


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌─────────────────────────────────────────────────────┐
│              Type Hints vs Pydantic                 │
├──────────────────┬──────────────────────────────────┤
│ Type Hints       │ Chỉ để IDE/mypy check, không ép  │
│                  │ kiểu lúc runtime                 │
├──────────────────┼──────────────────────────────────┤
│ Pydantic         │ Enforce + coerce kiểu lúc runtime │
│                  │ Raise ValidationError nếu sai    │
└──────────────────┴──────────────────────────────────┘
""")
