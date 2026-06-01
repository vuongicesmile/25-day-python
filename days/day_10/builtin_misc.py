"""
Section 19 & 20 — filter, map, sorted, eval, exec, zip,
                   docstrings, assert, multiple assignment, is vs ==
"""

# ============================================================
# 102. filter() — lọc phần tử
# ============================================================
# JS: arr.filter(fn)
# Python: filter(fn, iterable) → trả về iterator (lazy)

nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# JS: nums.filter(n => n % 2 === 0)
evens = list(filter(lambda n: n % 2 == 0, nums))
print(evens)   # [2, 4, 6, 8, 10]

# filter với function có sẵn
words = ["hello", "", "world", "", "python", ""]
non_empty = list(filter(None, words))   # filter(None) = lọc truthy
print(non_empty)   # ['hello', 'world', 'python']

# ⚡ Pythonic hơn: dùng list comprehension
evens = [n for n in nums if n % 2 == 0]   # rõ ràng hơn filter()

# filter trả về iterator — lazy (không tính ngay)
lazy = filter(lambda n: n > 5, nums)
print(next(lazy))   # 6
print(next(lazy))   # 7


# ============================================================
# 103. map() — biến đổi từng phần tử
# ============================================================
# JS: arr.map(fn)
# Python: map(fn, iterable) → iterator (lazy)

nums = [1, 2, 3, 4, 5]

# JS: nums.map(n => n ** 2)
squares = list(map(lambda n: n**2, nums))
print(squares)   # [1, 4, 9, 16, 25]

# map với nhiều iterables
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)   # [11, 22, 33]

# map với built-in function
strings = ["1", "2", "3", "4"]
numbers = list(map(int, strings))   # convert string → int
print(numbers)   # [1, 2, 3, 4]

names = ["vuong", "alice", "bob"]
upper = list(map(str.upper, names))
print(upper)   # ['VUONG', 'ALICE', 'BOB']

# ⚡ Pythonic hơn: list comprehension
squares = [n**2 for n in nums]   # dễ đọc hơn map + lambda


# ============================================================
# 104. sorted() — sắp xếp
# ============================================================
# JS: arr.sort() — sửa IN-PLACE, mặc định so sánh string!
# Python: sorted() → tạo list MỚI; .sort() → in-place

nums = [3, 1, 4, 1, 5, 9, 2, 6]

# sorted() — không sửa original
sorted_nums = sorted(nums)
print(sorted_nums)   # [1, 1, 2, 3, 4, 5, 6, 9]
print(nums)          # [3, 1, 4, 1, 5, 9, 2, 6] — không đổi!

# .sort() — in-place
nums.sort()
print(nums)          # [1, 1, 2, 3, 4, 5, 6, 9]

# Reverse
print(sorted(nums, reverse=True))   # [9, 6, 5, 4, 3, 2, 1, 1]

# key= — sắp xếp theo tiêu chí tùy chỉnh
words = ["banana", "apple", "cherry", "fig", "date"]
print(sorted(words))                        # alphabetical
print(sorted(words, key=len))               # theo độ dài
print(sorted(words, key=len, reverse=True)) # dài → ngắn
print(sorted(words, key=lambda w: w[-1]))   # theo ký tự cuối

# Sắp xếp list of dict
users = [
    {"name": "Bob",   "age": 30, "score": 85},
    {"name": "Alice", "age": 25, "score": 92},
    {"name": "Carol", "age": 28, "score": 78},
]
by_age   = sorted(users, key=lambda u: u["age"])
by_score = sorted(users, key=lambda u: u["score"], reverse=True)

print([u["name"] for u in by_age])    # ['Alice', 'Carol', 'Bob']
print([u["name"] for u in by_score])  # ['Alice', 'Bob', 'Carol']

# Sort nhiều tiêu chí — dùng tuple
students = [("Alice", 90), ("Bob", 85), ("Carol", 90), ("Dave", 85)]
# Sort: score desc, name asc
result = sorted(students, key=lambda x: (-x[1], x[0]))
print(result)   # [('Alice', 90), ('Carol', 90), ('Bob', 85), ('Dave', 85)]


# ============================================================
# 105. eval() — chạy string như code Python
# ============================================================
# JS: eval() — giống nhau, cả 2 đều NGUY HIỂM!

result = eval("2 + 3 * 4")
print(result)   # 14

expr = "len([1, 2, 3, 4, 5])"
print(eval(expr))   # 5

# ⚠️ NGUY HIỂM — KHÔNG dùng với user input!
# eval("__import__('os').system('rm -rf /')")  # có thể xóa hệ thống!

# Chỉ dùng eval khi: biểu thức toán học đơn giản từ nguồn tin cậy
# Thay thế an toàn: ast.literal_eval() — chỉ chấp nhận literals
import ast
safe = ast.literal_eval("[1, 2, 3]")     # ✅ safe
print(safe)   # [1, 2, 3]
# ast.literal_eval("os.system('rm -rf')")  # ❌ ValueError — an toàn!


# ============================================================
# 106. exec() — chạy string như nhiều dòng code
# ============================================================
# eval() chỉ chạy 1 expression
# exec() chạy cả block code

code = """
def greet(name):
    return f"Hello, {name}!"

result = greet("Vuong")
print(result)
"""
exec(code)   # Hello, Vuong!

# Thực tế: exec dùng trong code generation, scripting tools
# ⚠️ Cũng nguy hiểm như eval với user input!

# Biết sự khác biệt:
# eval("x + 1")   → expression, trả về giá trị
# exec("x = 1")   → statement, không trả về gì (None)


# ============================================================
# 107. zip() — ghép nhiều iterables lại
# ============================================================
# JS: không có built-in — phải dùng map với index

names  = ["Alice", "Bob", "Carol"]
ages   = [25, 30, 28]
cities = ["HCM", "HN", "Da Lat"]

# zip → tạo iterator các tuple
for name, age, city in zip(names, ages, cities):
    print(f"{name}, {age} tuổi, {city}")

# Tạo dict từ 2 list — rất hay dùng!
keys   = ["name", "age", "city"]
values = ["Vuong", 25, "Da Lat"]
d = dict(zip(keys, values))
print(d)   # {'name': 'Vuong', 'age': 25, 'city': 'Da Lat'}

# zip dừng ở iterable ngắn nhất
a = [1, 2, 3, 4, 5]
b = ["x", "y", "z"]
print(list(zip(a, b)))   # [(1,'x'), (2,'y'), (3,'z')] — 4,5 bị bỏ

# zip_longest — fill giá trị thiếu
from itertools import zip_longest
print(list(zip_longest(a, b, fillvalue=None)))
# [(1,'x'), (2,'y'), (3,'z'), (4,None), (5,None)]

# Unzip — * unpack
pairs = [(1, "a"), (2, "b"), (3, "c")]
nums, letters = zip(*pairs)
print(nums)     # (1, 2, 3)
print(letters)  # ('a', 'b', 'c')

# Transpose matrix
matrix = [[1,2,3],[4,5,6],[7,8,9]]
transposed = list(zip(*matrix))
print(transposed)   # [(1,4,7), (2,5,8), (3,6,9)]


# ============================================================
# 108. PROJECT: EMAIL FINDER
# ============================================================
import re

def find_emails(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

text = """
    Liên hệ chúng tôi tại support@company.com hoặc sales@business.org
    Không liên hệ: not-an-email, @invalid, missing@
    Admin: admin@example.co.uk và dev+test@github.io
"""

emails = find_emails(text)
print("Found emails:", emails)

for email in emails:
    valid = validate_email(email)
    print(f"  {'✅' if valid else '❌'} {email}")


# ============================================================
# 109. DOC STRINGS — tài liệu hóa code
# ============================================================
# JS: JSDoc /** @param ... @returns ... */
# Python: docstring — string ngay đầu function/class

def calculate_bmi(weight: float, height: float) -> float:
    """
    Tính chỉ số BMI.

    Args:
        weight: Cân nặng tính bằng kg
        height: Chiều cao tính bằng mét

    Returns:
        Chỉ số BMI (float)

    Raises:
        ValueError: Nếu weight hoặc height <= 0

    Example:
        >>> calculate_bmi(70, 1.75)
        22.857142857142858
    """
    if weight <= 0 or height <= 0:
        raise ValueError("weight và height phải > 0")
    return weight / (height ** 2)

# Truy cập docstring
print(calculate_bmi.__doc__)
help(calculate_bmi)   # formatted output


# ============================================================
# 110. ASSERT — kiểm tra điều kiện, raise nếu sai
# ============================================================
# JS: console.assert() — không throw, chỉ log
# Python: assert → raise AssertionError nếu sai

def divide(a, b):
    assert b != 0, "Không thể chia cho 0"   # message tùy chọn
    return a / b

print(divide(10, 2))   # 5.0
# divide(10, 0)        # AssertionError: Không thể chia cho 0

# Dùng trong testing
def test_add():
    assert 1 + 1 == 2
    assert "hello" + " " + "world" == "hello world"
    assert len([1,2,3]) == 3
    print("All tests passed!")

test_add()

# ⚠️ assert bị tắt khi chạy python với -O (optimize flag)
# Dùng assert cho: debugging, testing — KHÔNG dùng cho validation production
# Validation production → dùng if + raise


# ============================================================
# 111. MULTIPLE ASSIGNMENT — gán nhiều biến cùng lúc
# ============================================================
# JS: const [a, b] = [1, 2]  (destructuring)
# Python: a, b = 1, 2  (unpacking)

# Basic
a, b, c = 1, 2, 3
print(a, b, c)   # 1 2 3

# Swap — Python style
a, b = b, a      # không cần biến temp!
print(a, b)      # 2 1

# Unpack từ function return
def min_max(lst):
    return min(lst), max(lst)   # trả về tuple

lo, hi = min_max([3, 1, 4, 1, 5, 9])
print(lo, hi)   # 1 9

# Extended unpacking với *
first, *middle, last = [1, 2, 3, 4, 5]
print(first)    # 1
print(middle)   # [2, 3, 4]
print(last)     # 5

head, *tail = [10, 20, 30, 40]
print(head)   # 10
print(tail)   # [20, 30, 40]

# Unpack nested
(a, b), c = (1, 2), 3
print(a, b, c)   # 1 2 3

# Gán nhiều biến cùng giá trị
x = y = z = 0
print(x, y, z)   # 0 0 0
# ⚠️ Cẩn thận với mutable!
a = b = []       # a và b CÙNG object!
a.append(1)
print(b)         # [1] ← b cũng bị thay đổi!
# Fix:
a, b = [], []    # tạo 2 list riêng biệt


# ============================================================
# 112. is VS == — phân biệt quan trọng nhất
# ============================================================
# JS: === so sánh value + type (không có is)
# Python: == so sánh VALUE, is so sánh IDENTITY (cùng object?)

# == so sánh giá trị
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)   # True  — cùng giá trị

# is so sánh identity — cùng ô nhớ?
print(a is b)   # False — 2 list khác nhau trong RAM
c = a           # c trỏ đến CÙNG object với a
print(a is c)   # True  — cùng object

# is với None — LUÔN dùng is, không dùng ==
result = None
print(result is None)     # ✅ đúng cách
print(result == None)     # ⚠️ hoạt động nhưng không Pythonic

# Integer caching — CPython cache small ints (-5 đến 256)
x = 256
y = 256
print(x is y)   # True  — cached

x = 257
y = 257
print(x is y)   # False — không cached (có thể True tùy implementation)

# String interning
s1 = "hello"
s2 = "hello"
print(s1 is s2)   # True  — CPython intern short strings

s1 = "hello world"
s2 = "hello world"
print(s1 is s2)   # False (thường) — string dài không intern


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌──────────────────┬───────────────────────────┬─────────────────────────┐
│ Topic            │ Key point                 │ JS tương đương          │
├──────────────────┼───────────────────────────┼─────────────────────────┤
│ filter(fn, lst)  │ Lọc → iterator lazy       │ .filter()               │
│ map(fn, lst)     │ Transform → iterator lazy │ .map()                  │
│ sorted(lst,key=) │ Tạo list MỚI, key= mạnh  │ .sort() (sửa original!) │
│ eval(str)        │ Chạy expression ⚠️ nguy   │ eval() ⚠️ giống          │
│ exec(str)        │ Chạy nhiều dòng code ⚠️  │ không có                │
│ zip(a, b)        │ Ghép iterables → tuples   │ không có built-in       │
│ docstring """    │ Tài liệu hóa function     │ JSDoc /***/             │
│ assert cond      │ Raise nếu sai — cho test │ console.assert (khác!)  │
│ a, b = b, a      │ Swap không cần temp var   │ [a,b] = [b,a]           │
│ is               │ So sánh identity (object) │ không có tương đương    │
│ ==               │ So sánh value             │ === (gần giống)         │
├──────────────────┼───────────────────────────┴─────────────────────────┤
│ Gotchas          │ sorted() tạo list mới ↔ .sort() sửa in-place       │
│                  │ is None ✅  vs  == None ⚠️ (dùng is cho None)      │
│                  │ a = b = [] → CÙNG object! Dùng a, b = [], []       │
│                  │ filter/map trả về iterator, phải list() để xem     │
└──────────────────┴──────────────────────────────────────────────────────┘
""")
