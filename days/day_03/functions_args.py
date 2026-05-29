"""
Python Functions — *args, **kwargs và các loại arguments
So sánh với JavaScript
"""

# ============================================================
# 1. BASIC — default parameters (giống JS)
# ============================================================
# JS: function greet(name = "World") { return `Hello ${name}` }
def greet(name="World"):
    return f"Hello {name}"

print(greet())          # "Hello World"
print(greet("Vuong"))   # "Hello Vuong"

# ⚠️  GOTCHA: đừng dùng mutable làm default value!
def bad_append(item, lst=[]):    # lst=[] tạo RA MỘT LẦN khi define function
    lst.append(item)
    return lst

print(bad_append(1))    # [1]
print(bad_append(2))    # [1, 2]  ← bug! lst bị share giữa các lần gọi
print(bad_append(3))    # [1, 2, 3]

# Fix: dùng None làm sentinel
def good_append(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

print(good_append(1))   # [1]
print(good_append(2))   # [2]  ← đúng rồi


# ============================================================
# 2. POSITIONAL vs KEYWORD ARGUMENTS
# ============================================================
def create_user(name, age, city):
    return f"{name}, {age}, {city}"

# Positional — theo thứ tự
print(create_user("Vuong", 25, "Da Lat"))

# Keyword — gọi theo tên, không cần đúng thứ tự
print(create_user(age=25, city="Da Lat", name="Vuong"))

# Mix — positional trước, keyword sau
print(create_user("Vuong", city="Da Lat", age=25))


# ============================================================
# 3. *args — nhận NHIỀU positional arguments
# ============================================================
# JS: function sum(...numbers) { return numbers.reduce(...) }
# Python: dùng *args (tên args là convention, * mới là quan trọng)

def total(*args):
    print(type(args))   # <class 'tuple'>
    return sum(args)

print(total(1, 2, 3))           # 6
print(total(1, 2, 3, 4, 5))     # 15
print(total())                   # 0

# Mix với positional
def log(level, *messages):
    for msg in messages:
        print(f"[{level}] {msg}")

log("INFO", "Server started")                    # 1 message
log("ERROR", "DB failed", "Retry in 5s", "...")  # 3 messages


# ============================================================
# 4. **kwargs — nhận NHIỀU keyword arguments
# ============================================================
# JS: function config({ host, port, ...rest }) {}
# Python:

def build_url(**kwargs):
    print(type(kwargs))     # <class 'dict'>
    print(kwargs)
    return "&".join(f"{k}={v}" for k, v in kwargs.items())

print(build_url(host="localhost", port=8080, debug=True))
# host=localhost&port=8080&debug=True

# Mix *args và **kwargs
def everything(name, *args, **kwargs):
    print(f"name: {name}")
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

everything("Vuong", 1, 2, 3, city="Da Lat", job="dev")
# name: Vuong
# args: (1, 2, 3)
# kwargs: {'city': 'Da Lat', 'job': 'dev'}


# ============================================================
# 5. KEYWORD-ONLY arguments — sau dấu *
# ============================================================
# KHÔNG có trong JS — Python exclusive!
# Bắt buộc caller phải gọi theo tên, không được dùng positional

def send_email(to, subject, *, cc=None, bcc=None):
    #                         ^--- sau * là keyword-only
    print(f"To: {to}, Subject: {subject}, CC: {cc}, BCC: {bcc}")

send_email("a@b.com", "Hello", cc="c@b.com")   # ✅
# send_email("a@b.com", "Hello", "c@b.com")    # ❌ TypeError

# Tại sao dùng? Tránh nhầm lẫn khi nhiều optional params
def resize(width, height, *, keep_ratio=True, quality=90):
    pass

resize(1920, 1080, quality=75)          # rõ ràng
# resize(1920, 1080, True, 75)          # ❌ confusing, bị block


# ============================================================
# 6. POSITIONAL-ONLY arguments — trước dấu /
# ============================================================
# Python 3.8+ — cũng không có trong JS

def distance(x1, y1, x2, y2, /):
    #                          ^--- trước / là positional-only
    return ((x2-x1)**2 + (y2-y1)**2) ** 0.5

distance(0, 0, 3, 4)                    # ✅ positional
# distance(x1=0, y1=0, x2=3, y2=4)     # ❌ TypeError

# Mix tất cả — thứ tự bắt buộc:
# positional-only | regular | keyword-only
def full_example(pos_only, /, regular, *, kw_only):
    print(pos_only, regular, kw_only)

full_example(1, 2, kw_only=3)           # ✅
full_example(1, regular=2, kw_only=3)   # ✅
# full_example(pos_only=1, regular=2, kw_only=3)  # ❌


# ============================================================
# 7. UNPACKING khi GỌI function — dùng * và **
# ============================================================
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add(*nums))           # unpack list → add(1, 2, 3)

config = {"a": 10, "b": 20, "c": 30}
print(add(**config))        # unpack dict → add(a=10, b=20, c=30)

# Hay dùng khi pass kwargs từ function này sang function khác
def wrapper(**kwargs):
    return add(**kwargs)    # forward toàn bộ kwargs

print(wrapper(a=1, b=2, c=3))


# ============================================================
# 8. THỨ TỰ ARGUMENTS — phải đúng không lỗi
# ============================================================
# def func(positional, *args, keyword_only, **kwargs)
#           ^           ^      ^              ^
#           |           |      |              └── dict, phải cuối cùng
#           |           |      └── sau * → bắt buộc keyword
#           |           └── tuple, nhận tất cả positional dư
#           └── tham số thường

def api_call(endpoint, *paths, method="GET", **params):
    url = "/" + "/".join(paths)
    print(f"{method} {endpoint}{url} params={params}")

api_call("https://api.com", "users", "123", method="POST", include="profile")
# POST https://api.com/users/123 params={'include': 'profile'}


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌─────────────────┬────────────────────────┬──────────────────────────┐
│ Loại            │ Syntax                 │ Trong function           │
├─────────────────┼────────────────────────┼──────────────────────────┤
│ Positional-only │ def f(x, /)            │ chỉ gọi bằng vị trí     │
│ Regular         │ def f(x)               │ positional hoặc keyword  │
│ *args           │ def f(*args)           │ tuple, nhận tất cả dư    │
│ Keyword-only    │ def f(*, x)            │ bắt buộc gọi theo tên    │
│ **kwargs        │ def f(**kwargs)        │ dict, nhận tất cả kw dư  │
├─────────────────┼────────────────────────┼──────────────────────────┤
│ Thứ tự          │ pos_only / reg *args * kw_only **kwargs           │
├─────────────────┼────────────────────────────────────────────────────┤
│ JS tương đương  │ *args → ...rest  |  **kwargs → destructuring {}   │
│ Không có trong  │ positional-only (/)  |  keyword-only (*)          │
│ JS              │ for...else  |  walrus :=                          │
└─────────────────┴────────────────────────────────────────────────────┘
""")
