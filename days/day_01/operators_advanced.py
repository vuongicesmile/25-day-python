"""
Python Operators — Những điểm đặc biệt cần nhớ
"""

# ============================================================
# 1. WALRUS OPERATOR := (Python 3.8+) — KHÔNG có trong JS
# ============================================================
# Gán giá trị VÀ trả về giá trị trong cùng 1 expression
# Hay gặp trong interview vì là feature mới

# Trước walrus — phải viết 2 dòng
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
n = len(data)
if n > 5:
    print(f"Danh sách dài: {n}")

# Với walrus — gọn hơn
if (n := len(data)) > 5:
    print(f"Danh sách dài: {n}")  # n vẫn dùng được ở đây!

# Use case hay nhất: vòng lặp đọc dữ liệu
import re
texts = ["price: 100", "name: Vuong", "age: 25"]
for text in texts:
    if match := re.search(r'\d+', text):   # gán và check cùng lúc
        print(f"Tìm thấy số: {match.group()}")


# ============================================================
# 2. FLOOR DIVISION // với số âm — hay bị nhầm
# ============================================================
# JS: Math.floor(-7/2) = -4
# Python: -7 // 2 = -4  (floor về phía âm vô cực)

print(7 // 2)    #  3  — bình thường
print(-7 // 2)   # -4  — KHÔNG phải -3! (floor về phía âm)
print(7 // -2)   # -4
print(-7 // -2)  #  3

# Khác với int() truncation (về phía 0):
print(int(-7/2))   # -3  — truncate về 0
print(-7 // 2)     # -4  — floor về -∞


# ============================================================
# 3. CHAINED COMPARISONS — Python cho phép, JS không có
# ============================================================
x = 5

# JS: x > 0 && x < 10
# Python:
print(0 < x < 10)      # True  — đọc như toán học!
print(1 < x < 4)       # False
print(0 < x < 10 < 100)# True  — chain thoải mái

age = 25
print(18 <= age <= 65)  # True — rất readable


# ============================================================
# 4. SHORT-CIRCUIT — giống JS nhưng có điểm khác
# ============================================================
# Python: and/or trả về GIÁ TRỊ, không phải True/False
# JS: && || cũng vậy — nhưng Python hay dùng hơn

# or → trả về giá trị truthy đầu tiên, hoặc giá trị cuối
print(0 or "default")       # "default"
print("" or [] or "hello")  # "hello"
print(None or 0 or False)   # False  — hết truthy, trả cái cuối

# and → trả về giá trị falsy đầu tiên, hoặc giá trị cuối
print(1 and 2 and 3)        # 3     — hết falsy, trả cái cuối
print(1 and 0 and 3)        # 0     — gặp falsy đầu tiên

# Dùng làm default value (giống ?? trong JS)
name = "" or "Anonymous"    # "Anonymous"
value = None or 42          # 42

# Khác JS: Python có "or" assignment pattern
config = {}
timeout = config.get("timeout") or 30   # default 30


# ============================================================
# 5. UNPACKING OPERATORS * và ** — rất mạnh, hay gặp interview
# ============================================================

# * unpack list/tuple
a, *b, c = [1, 2, 3, 4, 5]
print(a)   # 1
print(b)   # [2, 3, 4]   — phần giữa
print(c)   # 5

first, *rest = [10, 20, 30, 40]
print(first)  # 10
print(rest)   # [20, 30, 40]

# * merge lists
list1 = [1, 2, 3]
list2 = [4, 5, 6]
merged = [*list1, *list2]        # [1, 2, 3, 4, 5, 6]
merged = [*list1, 99, *list2]    # [1, 2, 3, 99, 4, 5, 6]

# ** merge dicts (Python 3.9+: dùng | operator)
d1 = {"a": 1, "b": 2}
d2 = {"c": 3, "d": 4}
merged_dict = {**d1, **d2}       # {"a":1, "b":2, "c":3, "d":4}
override = {**d1, "b": 99}       # {"a":1, "b":99}  — d1's b bị override

# Python 3.9+ — dùng | thay **
merged_new = d1 | d2             # {"a":1, "b":2, "c":3, "d":4}
d1 |= d2                         # in-place merge (như +=)


# ============================================================
# 6. TERNARY — giống JS nhưng viết khác
# ============================================================
# JS: condition ? valueIfTrue : valueIfFalse
# Python: valueIfTrue if condition else valueIfFalse

age = 20
status = "adult" if age >= 18 else "minor"
print(status)   # "adult"

# Nested ternary (tránh dùng nhiều)
score = 75
grade = "A" if score >= 90 else "B" if score >= 75 else "C"
print(grade)    # "B"


# ============================================================
# 7. BITWISE — ít gặp nhưng interview hay hỏi
# ============================================================
a, b = 0b1010, 0b1100   # 10, 12 in binary

print(a & b)    # 0b1000 = 8   — AND
print(a | b)    # 0b1110 = 14  — OR
print(a ^ b)    # 0b0110 = 6   — XOR
print(~a)       # -11           — NOT (đảo bit + đổi dấu)
print(a << 1)   # 0b10100 = 20 — left shift (nhân 2)
print(a >> 1)   # 0b0101 = 5   — right shift (chia 2)

# Use case thực tế: check số chẵn lẻ (nhanh hơn %)
def is_even(n): return not (n & 1)
print(is_even(4))   # True
print(is_even(7))   # False

# Check bit thứ n có bật không
def has_bit(n, pos): return bool(n & (1 << pos))
print(has_bit(0b1010, 1))  # True  — bit 1 bật
print(has_bit(0b1010, 0))  # False — bit 0 tắt


# ============================================================
# TÓM TẮT — Những điểm hay bị hỏi trong interview
# ============================================================
print("""
┌──────────────────┬───────────────────────────────────────────┐
│ Operator         │ Điểm đặc biệt                             │
├──────────────────┼───────────────────────────────────────────┤
│ :=  (walrus)     │ Gán + trả về trong 1 expression (3.8+)   │
│ //  (floor div)  │ -7//2 = -4 (về -∞, không phải về 0)      │
│ 0<x<10 (chain)  │ Chain comparison — JS không có            │
│ or / and         │ Trả về giá trị, không phải bool           │
│ * / **           │ Unpack list/dict, merge collections       │
│ x if c else y   │ Ternary (ngược thứ tự so với JS)          │
│ & | ^ ~ << >>   │ Bitwise — check even: n & 1 == 0          │
│ |= (dict merge) │ In-place dict merge (Python 3.9+)         │
└──────────────────┴───────────────────────────────────────────┘
""")
