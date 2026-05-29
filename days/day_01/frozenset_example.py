"""
frozenset — Immutable Set
Quan hệ: set : frozenset  =  list : tuple
"""

# ============================================================
# 1. Tạo frozenset
# ============================================================
normal_set   = {1, 2, 3, 4}          # set thường — mutable
frozen       = frozenset([1, 2, 3, 4])  # frozenset — immutable

print(normal_set)   # {1, 2, 3, 4}
print(frozen)       # frozenset({1, 2, 3, 4})

# ============================================================
# 2. Không thể thay đổi sau khi tạo
# ============================================================
normal_set.add(5)       # ✅ OK
# frozen.add(5)         # ❌ AttributeError: 'frozenset' has no 'add'
# frozen.remove(1)      # ❌ AttributeError

# ============================================================
# 3. Vẫn dùng được set operations (read-only)
# ============================================================
a = frozenset([1, 2, 3])
b = frozenset([3, 4, 5])

print(a & b)    # frozenset({3})       — intersection
print(a | b)    # frozenset({1,2,3,4,5}) — union
print(a - b)    # frozenset({1, 2})    — difference
print(3 in a)   # True                 — membership check

# ============================================================
# 4. Dùng làm dict key (set thường KHÔNG làm được)
# ============================================================
# set không thể làm key vì mutable (unhashable)
# normal_set_key = {}
# normal_set_key[{1,2}] = "value"  # ❌ TypeError: unhashable type: 'set'

# frozenset có thể làm key vì immutable (hashable)
permissions = {
    frozenset(["read"])              : "viewer",
    frozenset(["read", "write"])     : "editor",
    frozenset(["read", "write", "delete"]): "admin",
}

user_perms = frozenset(["read", "write"])
print(permissions[user_perms])   # "editor"

# ============================================================
# 5. Thực tế hay gặp ở đâu?
# ============================================================

# Use case: cache/memoize với set làm argument
# Problem: set không hashable → không dùng làm cache key được
from functools import lru_cache

# ❌ Không được — set không hashable
# @lru_cache
# def process(items: set): ...

# ✅ Dùng frozenset thay thế
@lru_cache(maxsize=128)
def process(items: frozenset) -> int:
    return sum(items)

print(process(frozenset([1, 2, 3])))  # 6
print(process(frozenset([1, 2, 3])))  # 6 — lấy từ cache, không tính lại

# Use case: constant config không muốn ai sửa
ALLOWED_METHODS = frozenset(["GET", "POST", "PUT", "DELETE"])

def validate_method(method: str) -> bool:
    return method.upper() in ALLOWED_METHODS

print(validate_method("GET"))    # True
print(validate_method("PATCH"))  # False

# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌──────────────┬──────────────────────────────────────────────┐
│              │ set              │ frozenset                  │
├──────────────┼──────────────────┼────────────────────────────┤
│ Mutable      │ ✅ Yes           │ ❌ No                      │
│ Hashable     │ ❌ No            │ ✅ Yes                     │
│ Dict key     │ ❌ Không được    │ ✅ Được                    │
│ lru_cache    │ ❌ Không được    │ ✅ Được                    │
│ Set ops (&|-)│ ✅ Yes           │ ✅ Yes (read-only)          │
├──────────────┴──────────────────┴────────────────────────────┤
│ Dùng khi: cần set mà phải làm key, cache arg, hoặc config   │
│           constant không muốn ai modify                      │
└──────────────────────────────────────────────────────────────┘
""")
