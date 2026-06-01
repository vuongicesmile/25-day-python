"""
Section 21 & 22 — Lambdas, Walrus, Enums, Generators, Decorators, @wraps
"""

# ============================================================
# 114. LAMBDAS — anonymous function
# ============================================================
# JS: arrow function  x => x * 2  hoặc  (x, y) => x + y
# Python: lambda x: x * 2

# Basic
double = lambda x: x * 2
add    = lambda x, y: x + y
greet  = lambda name: f"Hello {name}"

print(double(5))        # 10
print(add(3, 4))        # 7
print(greet("Vuong"))   # Hello Vuong

# Lambda KHÔNG có: statements, multiple lines, return keyword
# Chỉ dùng cho expression đơn giản

# Hay dùng với sorted, map, filter
users = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
sorted_users = sorted(users, key=lambda u: u["age"])
print([u["name"] for u in sorted_users])   # ['Alice', 'Bob']

nums = [1, 2, 3, 4, 5]
evens   = list(filter(lambda n: n % 2 == 0, nums))
squares = list(map(lambda n: n**2, nums))

# ⚡ Lambda vs def — khi nào dùng cái nào?
# Lambda: dùng 1 lần, đơn giản (key=, callback ngắn)
# def:    tái dùng nhiều lần, cần docstring, phức tạp

# Conditional trong lambda
classify = lambda n: "even" if n % 2 == 0 else "odd"
print(classify(4))   # "even"
print(classify(7))   # "odd"

# Higher-order function với lambda
def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda x: x * 2, 3))   # 12  (3→6→12)
print(apply_twice(lambda x: x + 10, 5))  # 25  (5→15→25)


# ============================================================
# 115. WALRUS OPERATOR := (đã cover ở Day 01, ôn lại nhanh)
# ============================================================
# Python 3.8+ — assign và trả về giá trị trong 1 expression
# JS: không có

data = [1, 5, 2, 8, 3, 9, 4, 7, 6]

# Không walrus — 2 bước
filtered = [n for n in data if n > 5]
if filtered:
    print(f"Found {len(filtered)} items > 5: {filtered}")

# Có walrus — gọn hơn
if big := [n for n in data if n > 5]:
    print(f"Found {len(big)} items > 5: {big}")

# Hay dùng trong while loop
import random
attempts = 0
while (num := random.randint(1, 10)) != 7:
    attempts += 1
print(f"Tìm được 7 sau {attempts} lần thử")

# Tránh tính toán 2 lần
text = "Hello World Python"
if (words := text.split()) and len(words) > 2:
    print(f"Có {len(words)} từ: {words}")


# ============================================================
# 116. ENUMS — tập hợp constants có tên
# ============================================================
# JS: Object.freeze({RED: 'red', ...}) hoặc TypeScript enum
# Python: enum.Enum

from enum import Enum, auto

# Basic Enum
class Color(Enum):
    RED   = 1
    GREEN = 2
    BLUE  = 3

print(Color.RED)          # Color.RED
print(Color.RED.name)     # "RED"
print(Color.RED.value)    # 1
print(type(Color.RED))    # <enum 'Color'>

# So sánh enum
print(Color.RED == Color.RED)    # True
print(Color.RED == Color.BLUE)   # False
print(Color.RED == 1)            # False ← enum KHÔNG bằng raw value

# Truy cập bằng value
print(Color(1))         # Color.RED
print(Color["RED"])     # Color.RED

# auto() — tự động gán value
class Direction(Enum):
    NORTH = auto()   # 1
    SOUTH = auto()   # 2
    EAST  = auto()   # 3
    WEST  = auto()   # 4

print(Direction.NORTH.value)   # 1

# Enum với method
class Status(Enum):
    PENDING  = "pending"
    ACTIVE   = "active"
    INACTIVE = "inactive"
    BANNED   = "banned"

    def is_active(self):
        return self == Status.ACTIVE

    def can_login(self):
        return self in (Status.PENDING, Status.ACTIVE)

    def __str__(self):
        return self.value

user_status = Status.ACTIVE
print(user_status)              # "active"
print(user_status.is_active())  # True
print(user_status.can_login())  # True
print(Status.BANNED.can_login()) # False

# Loop qua Enum
for s in Status:
    print(f"  {s.name}: {s.value}")

# Dùng trong function
def process_order(status: Status):
    match status:
        case Status.PENDING:
            return "Đang xử lý..."
        case Status.ACTIVE:
            return "Đang hoạt động"
        case _:
            return "Không hợp lệ"


# ============================================================
# 118. GENERATORS — lazy iteration
# ============================================================
# JS: function* generator, yield
# Python: function với yield — giống JS!

# Generator function
def count_up(start, end):
    current = start
    while current <= end:
        yield current        # tạm dừng và trả về giá trị
        current += 1         # tiếp tục từ đây khi next() được gọi

gen = count_up(1, 5)
print(type(gen))          # <class 'generator'>
print(next(gen))          # 1
print(next(gen))          # 2
print(list(gen))          # [3, 4, 5] — consume phần còn lại

# Generator expression (giống list comprehension nhưng lazy)
squares_gen = (n**2 for n in range(1_000_000))   # không tốn RAM!
print(next(squares_gen))   # 0
print(next(squares_gen))   # 1

# Tại sao dùng generator?
# 1. Tiết kiệm RAM — tính từng giá trị khi cần
# 2. Xử lý dữ liệu lớn (file, stream, infinite sequence)

# Ví dụ thực tế: đọc file lớn
def read_chunks(filename, chunk_size=1024):
    with open(filename, 'r') as f:
        while chunk := f.read(chunk_size):
            yield chunk   # không load toàn bộ file vào RAM

# Fibonacci generator (infinite!)
def fibonacci():
    a, b = 0, 1
    while True:           # vô hạn nhưng lazy
        yield a
        a, b = b, a + b

fib = fibonacci()
first_10 = [next(fib) for _ in range(10)]
print(first_10)   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# Generator pipeline — chain generators
def integers(start=1):
    n = start
    while True:
        yield n
        n += 1

def take(n, iterable):
    for i, item in enumerate(iterable):
        if i >= n: break
        yield item

def only_even(iterable):
    for n in iterable:
        if n % 2 == 0:
            yield n

# Chain: integers → filter even → take 5
result = list(take(5, only_even(integers())))
print(result)   # [2, 4, 6, 8, 10]


# ============================================================
# 119 & 120. DECORATORS — wrap function với behavior mới
# ============================================================
# JS: Higher-order functions, không có @syntax
# Python: @decorator syntax — syntactic sugar

# Decorator cơ bản
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Trước khi gọi {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Sau khi gọi {func.__name__}")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello {name}!")

say_hello("Vuong")
# Trước khi gọi say_hello
# Hello Vuong!
# Sau khi gọi say_hello

# @my_decorator = syntactic sugar cho:
# say_hello = my_decorator(say_hello)

# Decorator thực tế: timing
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start  = time.time()
        result = func(*args, **kwargs)
        end    = time.time()
        print(f"{func.__name__} chạy trong {end-start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.1)
    return "done"

slow_function()   # slow_function chạy trong 0.1001s

# Decorator với arguments — cần thêm 1 lớp
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello {name}!")

greet("Vuong")   # in 3 lần

# Nhiều decorators — áp dụng từ dưới lên
@timer
@repeat(times=2)
def hello():
    print("Hi!")

# hello = timer(repeat(2)(hello))


# ============================================================
# 121. @wraps — giữ metadata của function gốc
# ============================================================
# Vấn đề: decorator làm mất __name__, __doc__ của function gốc

def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def my_func():
    """Đây là docstring của my_func"""
    pass

print(my_func.__name__)   # "wrapper" ← SAI! mất tên gốc
print(my_func.__doc__)    # None ← SAI! mất docstring

# Fix: dùng @wraps từ functools
from functools import wraps

def good_decorator(func):
    @wraps(func)          # copy metadata từ func sang wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def my_func():
    """Đây là docstring của my_func"""
    pass

print(my_func.__name__)   # "my_func" ✅
print(my_func.__doc__)    # "Đây là docstring..." ✅

# Best practice: LUÔN dùng @wraps khi viết decorator
def validate_input(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if arg is None:
                raise ValueError("Argument không được là None")
        return func(*args, **kwargs)
    return wrapper

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}({args}, {kwargs})")
        return func(*args, **kwargs)
    return wrapper

def cache_result(func):
    @wraps(func)
    def wrapper(*args):
        if args not in wrapper.cache:
            wrapper.cache[args] = func(*args)
        return wrapper.cache[args]
    wrapper.cache = {}
    return wrapper

@cache_result
@log_call
@validate_input
def compute(x, y):
    """Tính x^y"""
    return x ** y

print(compute(2, 10))   # log + validate + cache + compute
print(compute(2, 10))   # lấy từ cache, không log lại
print(compute.__name__) # "compute" ✅ nhờ @wraps


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌──────────────────┬───────────────────────────────┬────────────────────┐
│ Topic            │ Key point                     │ JS tương đương     │
├──────────────────┼───────────────────────────────┼────────────────────┤
│ lambda x: expr   │ Anonymous fn, 1 expression    │ x => expr          │
│ :=  walrus       │ Assign + return trong expr    │ ❌ không có        │
│ Enum             │ Named constants, type-safe    │ Object.freeze / TS │
│ Generator yield  │ Lazy iteration, tiết kiệm RAM │ function* yield    │
│ (x for x in...) │ Generator expression          │ ❌ không có        │
│ @decorator       │ Wrap function với behavior mới│ HOF, không có @    │
│ @wraps(func)     │ Giữ metadata function gốc     │ ❌ không có        │
├──────────────────┼───────────────────────────────┴────────────────────┤
│ Gotchas          │ Lambda: chỉ 1 expression, không statement          │
│                  │ Generator: chỉ iterate 1 lần (consumed)           │
│                  │ Enum: Color.RED != 1 (không bằng raw value)        │
│                  │ Decorator không có @wraps → mất __name__, __doc__ │
│                  │ Nhiều @decorator → áp dụng từ dưới lên trên       │
└──────────────────┴──────────────────────────────────────────────────────┘
""")
