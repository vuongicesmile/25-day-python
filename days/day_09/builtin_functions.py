"""
Section 17 & 18 — Built-in Functions
enumerate, round, range, slice, all, any, isinstance, callable
"""

# ============================================================
# 92. enumerate() — loop với index
# ============================================================
# JS: arr.forEach((item, i) => ...)  hoặc  arr.map((item, i) => ...)
# Python: enumerate trả về (index, value) pairs

fruits = ["apple", "banana", "cherry", "mango"]

# Cách thường (không Pythonic)
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Cách Pythonic — dùng enumerate
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Bắt đầu từ index khác (hay dùng cho numbering)
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
# 1. apple
# 2. banana
# 3. cherry

# Tạo dict từ list dùng enumerate
index_map = {fruit: i for i, fruit in enumerate(fruits)}
print(index_map)   # {'apple': 0, 'banana': 1, ...}

# Tìm index của phần tử thỏa điều kiện
data = [3, 7, 2, 9, 1, 8]
big_indices = [i for i, v in enumerate(data) if v > 5]
print(big_indices)   # [1, 3, 5]


# ============================================================
# 93. round() — làm tròn số
# ============================================================
# JS: Math.round() — chỉ làm tròn về số nguyên
# Python: round() linh hoạt hơn nhiều

print(round(3.14159))       # 3      — làm tròn về int
print(round(3.14159, 2))    # 3.14   — giữ 2 chữ số thập phân
print(round(3.14159, 4))    # 3.1416
print(round(3.5))           # 4
print(round(4.5))           # 4  ← BANKER'S ROUNDING! Không phải 5
print(round(2.5))           # 2  ← làm tròn về số chẵn gần nhất

# ⚠️ Banker's rounding — Python 3 dùng "round half to even"
# 2.5 → 2 (2 là chẵn), 3.5 → 4 (4 là chẵn)
# Khác với JS Math.round(2.5) = 3

# Làm tròn về hàng chục, trăm
print(round(1234, -1))   # 1230  — làm tròn về hàng chục
print(round(1234, -2))   # 1200  — làm tròn về hàng trăm
print(round(1567, -2))   # 1600

# Dùng trong tính toán tiền
price = 19.999
print(f"${round(price, 2)}")   # $20.0

# Format số đẹp hơn — dùng f-string
print(f"{3.14159:.2f}")   # "3.14" — 2 decimal places
print(f"{1234567:,}")     # "1,234,567" — comma separator
print(f"{0.8756:.1%}")    # "87.6%" — percentage


# ============================================================
# 94. range() — tạo dãy số
# ============================================================
# JS: không có built-in — phải dùng Array.from({length: n}, (_, i) => i)
# Python: range() rất mạnh và hiệu quả (lazy — không tạo list)

# range(stop)
print(list(range(5)))         # [0, 1, 2, 3, 4]

# range(start, stop)
print(list(range(2, 8)))      # [2, 3, 4, 5, 6, 7]

# range(start, stop, step)
print(list(range(0, 10, 2)))  # [0, 2, 4, 6, 8]
print(list(range(10, 0, -1))) # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
print(list(range(5, -1, -1))) # [5, 4, 3, 2, 1, 0]

# range là lazy — không tạo list, tiết kiệm RAM
r = range(1_000_000)
print(r[999999])   # 999999 — O(1), không loop!
print(len(r))      # 1000000
print(500 in r)    # True — O(1)!

# range hay dùng với reversed()
for i in reversed(range(5)):
    print(i, end=" ")   # 4 3 2 1 0

# Tạo list số nhanh
squares = [i**2 for i in range(1, 11)]
print(squares)   # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]


# ============================================================
# 95. slice() — object hóa slicing
# ============================================================
# Thay vì viết [1:5:2] trực tiếp — tạo slice object để tái dùng

data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Cách thường
print(data[1:5])      # [1, 2, 3, 4]
print(data[::2])      # [0, 2, 4, 6, 8]

# Dùng slice object — hay dùng khi slice cần tái sử dụng
every_other  = slice(None, None, 2)   # ::2
first_half   = slice(None, 5)         # :5
last_three   = slice(-3, None)        # -3:

print(data[every_other])    # [0, 2, 4, 6, 8]
print(data[first_half])     # [0, 1, 2, 3, 4]
print(data[last_three])     # [7, 8, 9]

# Dùng 1 slice cho nhiều sequence
headers = ["name", "age", "city", "email", "phone"]
row1    = ["Vuong", 25, "Da Lat", "v@gmail.com", "0901"]
row2    = ["Alice", 30, "HCM",    "a@gmail.com", "0902"]

key_fields = slice(0, 3)   # lấy 3 field đầu
print(headers[key_fields])  # ['name', 'age', 'city']
print(row1[key_fields])     # ['Vuong', 25, 'Da Lat']
print(row2[key_fields])     # ['Alice', 30, 'HCM']


# ============================================================
# 97. all() — True nếu TẤT CẢ đều truthy
# ============================================================
# JS: arr.every(x => x)
# Python: all(iterable)

nums = [2, 4, 6, 8, 10]
print(all(n % 2 == 0 for n in nums))   # True — tất cả đều chẵn
print(all(n > 5 for n in nums))        # False — 2, 4 không > 5

# Validate form fields
def validate_user(user):
    required = ["name", "email", "age"]
    return all(field in user and user[field] for field in required)

print(validate_user({"name": "Vuong", "email": "v@g.com", "age": 25}))  # True
print(validate_user({"name": "Alice", "email": "", "age": 30}))          # False

# all([]) = True — empty iterable → True (vacuous truth)
print(all([]))   # True

# Kiểm tra list có phần tử hợp lệ không
passwords = ["abc123!", "Pass@123", "Secure#1"]
all_strong = all(len(p) >= 8 for p in passwords)
print(all_strong)   # False (abc123! chỉ 7 ký tự)


# ============================================================
# 98. any() — True nếu CÓ ÍT NHẤT 1 truthy
# ============================================================
# JS: arr.some(x => x)
# Python: any(iterable)

nums = [1, 3, 5, 4, 7]
print(any(n % 2 == 0 for n in nums))   # True — có 4 là chẵn
print(any(n > 10 for n in nums))       # False — không có số nào > 10

# Tìm xem có user admin không
users = [
    {"name": "Alice", "role": "user"},
    {"name": "Bob",   "role": "admin"},
    {"name": "Carol", "role": "user"},
]
has_admin = any(u["role"] == "admin" for u in users)
print(has_admin)   # True

# any([]) = False — empty → False
print(any([]))   # False

# Kết hợp all() và any() 
scores = [85, 92, 78, 96, 88]
print(all(s >= 70 for s in scores))   # True — tất cả pass
print(any(s >= 90 for s in scores))   # True — có ít nhất 1 excellent


# ============================================================
# 99. isinstance() — kiểm tra kiểu dữ liệu
# ============================================================
# JS: typeof, instanceof
# Python: isinstance() — mạnh hơn vì check cả inheritance

print(isinstance(42, int))           # True
print(isinstance(3.14, float))       # True
print(isinstance("hello", str))      # True
print(isinstance([1,2,3], list))     # True
print(isinstance(True, int))         # True ← bool là subclass của int!
print(isinstance(True, bool))        # True

# Check nhiều type cùng lúc — truyền tuple
def process(value):
    if isinstance(value, (int, float)):
        return f"Số: {value * 2}"
    elif isinstance(value, str):
        return f"String: {value.upper()}"
    elif isinstance(value, list):
        return f"List: {len(value)} phần tử"
    else:
        return "Unknown type"

print(process(42))          # Số: 84
print(process("hello"))     # String: HELLO
print(process([1,2,3]))     # List: 3 phần tử

# isinstance check inheritance
class Animal: pass
class Dog(Animal): pass

d = Dog()
print(isinstance(d, Dog))     # True
print(isinstance(d, Animal))  # True  ← dog IS-A animal
print(type(d) == Animal)      # False ← type() không check inheritance

# isinstance vs type()
# isinstance → check kể cả subclass ✅ (dùng cái này)
# type()     → check chính xác type, không check subclass


# ============================================================
# 100. callable() — kiểm tra có gọi được không
# ============================================================
# JS: typeof fn === 'function'
# Python: callable()

def my_func(): pass
class MyClass: pass

print(callable(my_func))     # True  — function
print(callable(MyClass))     # True  — class cũng callable! (tạo instance)
print(callable(42))          # False — int không callable
print(callable("hello"))     # False

# Object có __call__ thì cũng callable
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):    # làm object callable như function
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(callable(double))    # True  — vì có __call__
print(double(5))           # 10
print(triple(4))           # 12

# Hay dùng khi nhận function làm argument
def apply(func, value):
    if not callable(func):
        raise TypeError(f"{func} không phải callable")
    return func(value)

print(apply(double, 7))      # 14
print(apply(str.upper, "hi"))  # "HI"


# ============================================================
# 101. PROJECT: FINANCE BAR CHART
# ============================================================
def finance_bar_chart(data: dict, width: int = 40):
    """
    data = {"Jan": 1200, "Feb": 950, "Mar": 1800, ...}
    """
    if not data:
        print("Không có dữ liệu")
        return

    max_val  = max(data.values())
    total    = sum(data.values())
    avg      = total / len(data)

    print(f"\n{'='*55}")
    print(f"{'FINANCE REPORT':^55}")
    print(f"{'='*55}")

    for month, amount in data.items():
        bar_len  = round((amount / max_val) * width)
        bar      = "█" * bar_len
        pct      = amount / total * 100
        marker   = " ← AVG" if abs(amount - avg) < (max_val * 0.05) else ""
        print(f"{month:>4} | {bar:<{width}} ${amount:>7,.0f} ({pct:.1f}%){marker}")

    print(f"{'─'*55}")
    print(f"{'Total':>4} | {'':>{width}} ${total:>7,.0f}")
    print(f"{'Avg':>4} | {'':>{width}} ${avg:>7,.0f}")
    print(f"{'Max':>4} | {'':>{width}} ${max_val:>7,.0f}")

monthly_revenue = {
    "Jan": 12500, "Feb": 9800,  "Mar": 15200,
    "Apr": 13100, "May": 17800, "Jun": 16400,
    "Jul": 14200, "Aug": 18900, "Sep": 15600,
    "Oct": 20100, "Nov": 22500, "Dec": 28000,
}

finance_bar_chart(monthly_revenue)

# Dùng all() và any() để validate
def is_valid_data(data):
    return (
        isinstance(data, dict) and
        all(isinstance(k, str) for k in data.keys()) and
        all(isinstance(v, (int, float)) and v >= 0 for v in data.values()) and
        any(v > 0 for v in data.values())
    )

print(f"\nDữ liệu hợp lệ: {is_valid_data(monthly_revenue)}")


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌─────────────────┬──────────────────────────────┬───────────────────────┐
│ Built-in        │ Dùng khi nào                 │ JS tương đương        │
├─────────────────┼──────────────────────────────┼───────────────────────┤
│ enumerate(lst)  │ Loop cần cả index + value    │ forEach((v,i)=>)      │
│ round(n, d)     │ Làm tròn số                  │ Math.round() (khác!)  │
│ range(s,e,step) │ Dãy số, loop n lần           │ Array.from({length})  │
│ slice(s,e,step) │ Tái dùng slice pattern       │ .slice() (kém hơn)    │
│ all(iterable)   │ Tất cả đều thỏa điều kiện?   │ .every()              │
│ any(iterable)   │ Có ít nhất 1 thỏa điều kiện? │ .some()               │
│ isinstance(x,T) │ Check kiểu + kế thừa         │ instanceof (yếu hơn)  │
│ callable(x)     │ Có gọi được như function?    │ typeof === 'function'  │
├─────────────────┼──────────────────────────────┴───────────────────────┤
│ Gotchas         │ round(2.5) = 2 (banker's rounding, không phải 3!)   │
│                 │ all([]) = True, any([]) = False (empty iterable)     │
│                 │ isinstance(True, int) = True (bool subclass of int)  │
│                 │ class callable → MyClass() tạo instance             │
└─────────────────┴──────────────────────────────────────────────────────┘
""")
