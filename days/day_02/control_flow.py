"""
Control Flow — So sánh Python vs JavaScript
"""

# ============================================================
# 1. IF / ELIF / ELSE
# ============================================================
# JS:  else if
# Py:  elif  (viết gọn hơn)

score = 75

# JS:
# if (score >= 90) { grade = "A" }
# else if (score >= 75) { grade = "B" }
# else { grade = "C" }

# Python:
if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "F"

print(grade)  # "B"

# Python KHÔNG có switch/case (Python 3.10+ có match)
# Thay bằng dict lookup — đây là Pythonic way:
def get_day(n):
    days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
    return days.get(n, "Weekend")

print(get_day(3))   # "Wed"
print(get_day(7))   # "Weekend"

# Python 3.10+ match statement (giống switch nhưng mạnh hơn)
def classify(value):
    match value:
        case 0:
            return "zero"
        case int(n) if n < 0:
            return f"negative: {n}"
        case int(n):
            return f"positive: {n}"
        case str(s):
            return f"string: {s}"
        case _:
            return "unknown"

print(classify(0))      # "zero"
print(classify(-5))     # "negative: -5"
print(classify("hi"))   # "string: hi"


# ============================================================
# 2. FOR LOOP — khác hoàn toàn JS
# ============================================================
# JS for loop: for (let i = 0; i < 5; i++)
# Python KHÔNG có kiểu đó — dùng range()

for i in range(5):          # 0, 1, 2, 3, 4
    print(i, end=" ")
print()

for i in range(2, 8):       # 2, 3, 4, 5, 6, 7
    print(i, end=" ")
print()

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8  (bước nhảy 2)
    print(i, end=" ")
print()

for i in range(5, 0, -1):   # 5, 4, 3, 2, 1  (đếm ngược)
    print(i, end=" ")
print()

# for...of trong JS → for...in trong Python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# for...in (lấy key object) trong JS → không cần, dùng .items()
user = {"name": "Vuong", "age": 25, "city": "Da Lat"}
for key, value in user.items():     # giống Object.entries()
    print(f"{key}: {value}")

for key in user:                    # giống Object.keys() / for...in JS
    print(key)

for value in user.values():         # giống Object.values()
    print(value)


# ============================================================
# 3. ENUMERATE — KHÔNG có trong JS (phải dùng forEach với index)
# ============================================================
# JS: fruits.forEach((fruit, index) => ...)
# Python:
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry

# Bắt đầu từ index khác
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}. {fruit}")
# 1. apple
# 2. banana


# ============================================================
# 4. ZIP — loop nhiều list cùng lúc
# ============================================================
# JS: names.map((name, i) => ({name, score: scores[i]}))
names  = ["Alice", "Bob", "Charlie"]
scores = [90, 85, 92]

for name, score in zip(names, scores):
    print(f"{name}: {score}")

# zip dừng ở list ngắn nhất
# zip_longest để fill giá trị thiếu
from itertools import zip_longest
a = [1, 2, 3]
b = ["x", "y"]
for x, y in zip_longest(a, b, fillvalue=None):
    print(x, y)  # 3, None ở cuối


# ============================================================
# 5. WHILE LOOP
# ============================================================
# Giống JS, nhưng Python có thêm: while...else

count = 0
while count < 5:
    print(count, end=" ")
    count += 1
# 0 1 2 3 4

# while...else — else chạy khi loop kết thúc tự nhiên (không bị break)
# KHÔNG có trong JS — hay được hỏi trong interview!
def find_prime(numbers):
    for n in numbers:
        for i in range(2, n):
            if n % i == 0:
                break           # không phải prime
        else:
            print(f"{n} is prime")  # else của for chạy khi không bị break

find_prime([2, 3, 4, 5, 6, 7])


# ============================================================
# 6. BREAK / CONTINUE / PASS
# ============================================================
# break, continue — giống JS

# PASS — Python có, JS không có
# Dùng khi cần cú pháp hợp lệ nhưng chưa implement
for i in range(5):
    if i == 2:
        pass        # TODO: xử lý sau
    print(i)

# Dùng trong class/function chưa implement
class MyClass:
    pass    # placeholder — không lỗi

def todo_function():
    pass    # implement sau


# ============================================================
# 7. COMPREHENSION — Python exclusive, rất Pythonic
# ============================================================
# Thay for loop bằng 1 dòng

nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# List comprehension
# JS: nums.filter(n => n % 2 === 0).map(n => n ** 2)
evens_squared = [n**2 for n in nums if n % 2 == 0]
print(evens_squared)   # [4, 16, 36, 64, 100]

# Dict comprehension
# JS: Object.fromEntries(fruits.map(f => [f, len(f)]))
fruits = ["apple", "banana", "cherry"]
lengths = {f: len(f) for f in fruits}
print(lengths)  # {'apple': 5, 'banana': 6, 'cherry': 6}

# Set comprehension
unique_lens = {len(f) for f in fruits}
print(unique_lens)  # {5, 6}

# Generator expression (lazy — không tạo list ngay)
total = sum(n**2 for n in range(1000000))  # không tốn RAM


# ============================================================
# TÓM TẮT SO SÁNH
# ============================================================
print("""
┌─────────────────────┬──────────────────────┬────────────────────────┐
│ Tính năng           │ JavaScript           │ Python                 │
├─────────────────────┼──────────────────────┼────────────────────────┤
│ else if             │ else if              │ elif                   │
│ switch              │ switch/case          │ match (3.10+) / dict   │
│ for loop            │ for(i=0;i<n;i++)     │ for i in range(n)      │
│ for...of            │ for (x of arr)       │ for x in arr           │
│ forEach với index   │ arr.forEach((x,i)=>  │ enumerate(arr)         │
│ loop nhiều array    │ map với index        │ zip(a, b)              │
│ loop...else         │ ❌ không có          │ for/while...else ✅    │
│ placeholder         │ ❌ không có          │ pass ✅                │
│ filter+map gọn      │ .filter().map()      │ [x for x in if]        │
└─────────────────────┴──────────────────────┴────────────────────────┘
""")
