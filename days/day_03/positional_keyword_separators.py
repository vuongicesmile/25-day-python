"""
/ và * trong function signature — Positional-only & Keyword-only separators
"""

# ============================================================
# 1. / — POSITIONAL-ONLY (mọi thứ TRƯỚC / chỉ dùng vị trí)
# ============================================================
def greet(name, age, /):
    print(f"{name}, {age}")

greet("Vuong", 25)           # ✅
# greet(name="Vuong", age=25) # ❌ TypeError: got unexpected keyword argument

# Ví dụ thực tế: built-in Python dùng / nhiều lắm
# len(obj, /)  → không thể gọi len(obj=mylist)
# abs(x, /)   → không thể gọi abs(x=-5)


# ============================================================
# 2. * bare — KEYWORD-ONLY (mọi thứ SAU * phải dùng tên)
# ============================================================
def send_email(to, subject, *, cc=None, urgent=False):
    print(f"To:{to} | Subject:{subject} | CC:{cc} | Urgent:{urgent}")

send_email("a@b.com", "Hello")                      # ✅
send_email("a@b.com", "Hello", cc="c@b.com")        # ✅
send_email("a@b.com", "Hello", urgent=True)          # ✅
# send_email("a@b.com", "Hello", "c@b.com")          # ❌ TypeError


# ============================================================
# 3. KẾT HỢP / và * trong cùng 1 function
# ============================================================
#   positional-only | regular (cả hai) | keyword-only
#        /          |                  |     *
def resize(src, /, width, height, *, quality=90, overwrite=False):
    print(f"src={src} | {width}x{height} | q={quality} | overwrite={overwrite}")

resize("img.png", 1920, 1080)                   # ✅ tất cả positional
resize("img.png", 1920, 1080, quality=75)       # ✅ keyword-only dùng tên
resize("img.png", width=1920, height=1080)      # ✅ regular dùng keyword OK

# resize(src="img.png", width=1920, height=1080) # ❌ src là positional-only
# resize("img.png", 1920, 1080, 75)              # ❌ quality là keyword-only


# ============================================================
# 4. * bare vs *args — khác nhau!
# ============================================================
# *args  → NHẬN arguments vào tuple
# * bare → chỉ là RANH GIỚI, không nhận gì

def with_args(*args, keyword_only):
    print(f"args={args}, keyword_only={keyword_only}")

def with_bare_star(a, b, *, keyword_only):
    print(f"a={a}, b={b}, keyword_only={keyword_only}")

with_args(1, 2, 3, keyword_only="hello")    # args=(1,2,3)
with_bare_star(1, 2, keyword_only="hello")  # a=1, b=2


# ============================================================
# 5. ĐẦY ĐỦ TẤT CẢ — thứ tự chuẩn
# ============================================================
def full(pos_only, /, regular, *args, kw_only, **kwargs):
    print(f"pos_only : {pos_only}")
    print(f"regular  : {regular}")
    print(f"args     : {args}")
    print(f"kw_only  : {kw_only}")
    print(f"kwargs   : {kwargs}")

full(1, 2, 3, 4, 5, kw_only="must", extra="ok", more=True)
# pos_only : 1
# regular  : 2
# args     : (3, 4, 5)
# kw_only  : must
# kwargs   : {'extra': 'ok', 'more': True}


# ============================================================
# TÓM TẮT
# ============================================================
print("""
def func( pos_only , / , regular , *args , * , kw_only , **kwargs )
          ^           ^             ^      ^    ^           ^
     chỉ vị trí   ranh giới   cả hai  tuple  ranh giới   dict
                                     dư ra            bắt buộc tên
""")
