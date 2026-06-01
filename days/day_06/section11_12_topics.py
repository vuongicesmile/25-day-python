"""
Section 11 & 12 — Truthy, Float Problem, Scope, global, nonlocal,
                   main(), List Comprehensions, Slicing, Looping Problem
"""

# ============================================================
# 61. TRUTHY & FALSY
# ============================================================
# JS có truthy/falsy, Python tương tự nhưng có điểm khác

# Falsy trong Python:
falsy_values = [
    False, 0, 0.0, 0j,   # bool, int, float, complex
    "", [], {}, set(),    # empty string, list, dict, set
    None,                 # None (≈ null)
    range(0),            # empty range
]

for v in falsy_values:
    print(f"{repr(v):<15} → bool: {bool(v)}")

# Truthy = tất cả còn lại
print(bool(1))          # True
print(bool("hello"))    # True
print(bool([0]))        # True — list có phần tử, dù là 0
print(bool(" "))        # True — string có space, không phải empty

# ⚠️ Điểm hay bị nhầm so với JS:
print(bool("0"))        # True  — JS: Boolean("0") = true ✅ giống
print(bool([]))         # False — JS: Boolean([]) = true ❌ KHÁC!
print(bool({}))         # False — JS: Boolean({}) = true ❌ KHÁC!

# Dùng truthy trong if:
name = ""
if not name:
    print("name rỗng")  # chạy

users = []
if not users:
    print("Không có user")  # chạy

data = {"key": "value"}
if data:
    print("Có data")  # chạy


# ============================================================
# 62. THE FLOAT PROBLEM
# ============================================================
# Không phải lỗi của Python — tất cả ngôn ngữ dùng IEEE 754 đều bị!
# JS: 0.1 + 0.2 === 0.3 → false (giống Python)

print(0.1 + 0.2)            # 0.30000000000000004
print(0.1 + 0.2 == 0.3)     # False ← đây là "float problem"

# Tại sao? Float lưu theo binary — 0.1 không biểu diễn chính xác trong binary
# Giống 1/3 = 0.3333... không kết thúc trong decimal

# Fix 1: round() — cho display
print(round(0.1 + 0.2, 1))          # 0.3

# Fix 2: math.isclose() — cho so sánh (CÁCH ĐÚNG)
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True ✅

# Fix 3: Decimal — cho tính toán tiền tệ chính xác tuyệt đối
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))           # 0.3 chính xác
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))  # True ✅

# Rule: dùng tiền → Decimal. So sánh float → math.isclose(). Display → round()


# ============================================================
# 63. SCOPES — LEGB Rule
# ============================================================
# JS: var (function scope), let/const (block scope)
# Python: LEGB — Local → Enclosing → Global → Built-in

x = "global"   # Global

def outer():
    x = "enclosing"   # Enclosing

    def inner():
        x = "local"   # Local
        print(x)      # "local" — tìm Local trước

    inner()
    print(x)          # "enclosing"

outer()
print(x)              # "global"

# Python KHÔNG có block scope!
for i in range(5):
    last = i         # last tồn tại sau for loop!

print(last)          # 4 — JS với var cũng vậy, let thì không


# ============================================================
# 64. GLOBAL — dùng biến global bên trong function
# ============================================================
# JS: không cần khai báo, tự access được (nhưng không gán được không)

count = 0

def increment():
    global count        # khai báo muốn dùng biến global
    count += 1          # không có global → UnboundLocalError

increment()
increment()
print(count)   # 2

# Không có global → Python nghĩ count là local variable
def bad_increment():
    # count += 1  # ❌ UnboundLocalError: referenced before assignment
    pass


# ============================================================
# 65. NONLOCAL — dùng biến của enclosing function
# ============================================================
# KHÔNG có trong JS — dùng trong closure

def make_counter():
    count = 0   # enclosing scope

    def increment():
        nonlocal count   # tham chiếu đến count của outer function
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())   # 1
print(counter())   # 2
print(counter())   # 3  — count được giữ lại trong closure!

# So sánh global vs nonlocal:
# global   → biến ở module level (top of file)
# nonlocal → biến ở enclosing function (outer function)


# ============================================================
# 67. MAIN() PATTERN
# ============================================================
# Convention chuẩn khi viết Python script

def setup():
    print("Khởi tạo...")

def run():
    print("Chạy logic chính...")

def teardown():
    print("Dọn dẹp...")

def main():
    setup()
    run()
    teardown()

if __name__ == "__main__":
    main()
# Tại sao? Khi file bị import, main() không tự chạy
# Unit test import file → không chạy side effects


# ============================================================
# 68. LIST COMPREHENSIONS
# ============================================================
# JS: .map() .filter() — phải chain
# Python: 1 expression gọn hơn

nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Basic
squares = [n**2 for n in nums]

# Với filter
even_squares = [n**2 for n in nums if n % 2 == 0]

# Nested (thay for lồng nhau)
# JS: [[1,2],[3,4]].flat() hoặc reduce
matrix = [[1,2,3],[4,5,6],[7,8,9]]
flat = [x for row in matrix for x in row]   # [1,2,3,4,5,6,7,8,9]

# Dict comprehension
word_len = {word: len(word) for word in ["apple","banana","cherry"]}

# Set comprehension
unique = {n % 3 for n in nums}   # {0, 1, 2}

# Generator (lazy — không tạo list trong RAM)
gen = (n**2 for n in range(1_000_000))   # chưa tính gì
print(next(gen))   # 0  — tính từng cái khi cần


# ============================================================
# 69. SLICING
# ============================================================
# JS: .slice() — Python mạnh hơn nhiều

lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
s = "Hello, World!"

# [start:stop:step]  — stop không bao gồm
print(lst[2:5])      # [2, 3, 4]
print(lst[:3])       # [0, 1, 2]    — từ đầu
print(lst[7:])       # [7, 8, 9]    — đến cuối
print(lst[::2])      # [0,2,4,6,8]  — bước 2
print(lst[::-1])     # [9,8,...,0]  — reverse!

# Index âm — đếm từ cuối
print(lst[-1])       # 9  — phần tử cuối
print(lst[-3:])      # [7, 8, 9]
print(lst[:-3])      # [0,1,2,3,4,5,6]

# String slicing — giống list
print(s[7:12])       # "World"
print(s[:5])         # "Hello"
print(s[::-1])       # "!dlroW ,olleH"

# Copy list bằng slice
original = [1, 2, 3]
copy = original[:]   # shallow copy — JS: [...original]


# ============================================================
# 70. THE LOOPING PROBLEM — modifying list while looping
# ============================================================
# BUG HAY GẶP: xóa phần tử khi đang loop

# ❌ SAI — skip phần tử
nums = [1, 2, 3, 4, 5, 6]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)   # list bị thay đổi trong lúc loop!
print(nums)   # [1, 3, 5] — OK trong case này nhưng không đáng tin

# ❌ SAI hơn — không xóa hết
nums = [1, 2, 2, 3, 4]
for n in nums:
    if n == 2:
        nums.remove(n)   # chỉ xóa được 1 trong 2 số 2!
print(nums)   # [1, 2, 3, 4] ← bug, vẫn còn số 2

# ✅ ĐÚNG 1 — loop qua copy
nums = [1, 2, 2, 3, 4]
for n in nums[:]:        # nums[:] tạo copy
    if n == 2:
        nums.remove(n)
print(nums)   # [1, 3, 4] ✅

# ✅ ĐÚNG 2 — list comprehension (Pythonic nhất)
nums = [1, 2, 2, 3, 4]
nums = [n for n in nums if n != 2]
print(nums)   # [1, 3, 4] ✅

# ✅ ĐÚNG 3 — filter()
nums = list(filter(lambda n: n != 2, [1, 2, 2, 3, 4]))
print(nums)   # [1, 3, 4] ✅


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌──────────────────┬─────────────────────────────────────────────┐
│ Topic            │ Key point                                   │
├──────────────────┼─────────────────────────────────────────────┤
│ Truthy           │ [], {}, "" là False — khác JS!             │
│ Float problem    │ 0.1+0.2 ≠ 0.3 → dùng math.isclose()       │
│ Scope (LEGB)     │ Local→Enclosing→Global→Built-in            │
│ global           │ khai báo để gán biến global trong function  │
│ nonlocal         │ khai báo để gán biến enclosing trong closure│
│ main()           │ if __name__=="__main__": main()             │
│ Comprehension    │ [x for x in lst if cond] — gọn hơn map/filter│
│ Slicing          │ lst[start:stop:step] — lst[::-1] reverse   │
│ Looping problem  │ KHÔNG xóa/thêm list khi đang for loop      │
└──────────────────┴─────────────────────────────────────────────┘
""")
