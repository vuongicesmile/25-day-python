"""
Exception Handling — So sánh Python vs JavaScript
"""

# ============================================================
# 1. CƠ BẢN: try/except vs try/catch
# ============================================================
# JS:
# try { JSON.parse(badJson) }
# catch (e) { console.log(e.message) }

# Python: "catch" → "except"
import json

bad_json = "{ not valid }"

try:
    data = json.loads(bad_json)
except Exception as e:
    print(f"Lỗi: {e}")   # Expecting property name


# ============================================================
# 2. NHIỀU EXCEPT — bắt từng loại lỗi cụ thể
# ============================================================
# JS: phải dùng if (e instanceof TypeError) bên trong catch
# Python: nhiều except block riêng biệt — rõ ràng hơn nhiều

def chia(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Không chia được cho 0!")
    except TypeError as e:
        print(f"Sai kiểu dữ liệu: {e}")

chia(10, 2)      # 5.0
chia(10, 0)      # Không chia được cho 0!
chia(10, "abc")  # Sai kiểu dữ liệu


# ============================================================
# 3. ELSE — chạy khi KHÔNG có exception
# ============================================================
# KHÔNG có trong JS — hay bị hỏi interview!

def doc_file(filename):
    try:
        f = open(filename)
    except FileNotFoundError:
        print(f"File '{filename}' không tồn tại")
    else:
        # Chạy khi try thành công, KHÔNG có exception
        content = f.read()
        f.close()
        print(f"Đọc được {len(content)} ký tự")

doc_file("khong_ton_tai.txt")  # exception
doc_file("README.md")          # else chạy


# ============================================================
# 4. FINALLY — luôn chạy dù có lỗi hay không
# ============================================================
# Giống JS finally, nhưng Python dùng nhiều hơn

def ket_noi_db():
    conn = None
    try:
        print("Đang kết nối DB...")
        conn = {"status": "connected"}  # giả lập
        result = 1 / 0                  # lỗi xảy ra ở đây
        return result
    except ZeroDivisionError as e:
        print(f"Lỗi: {e}")
    finally:
        # Luôn chạy — dù try thành công, thất bại, hay return
        if conn:
            print("Đóng kết nối DB")   # cleanup luôn xảy ra

ket_noi_db()


# ============================================================
# 5. CẤU TRÚC ĐẦY ĐỦ: try / except / else / finally
# ============================================================
def xu_ly(data):
    try:
        result = int(data)          # có thể lỗi
    except ValueError:
        print("Không convert được sang int")
        return None
    except TypeError:
        print("data phải là string hoặc number")
        return None
    else:
        print(f"Thành công: {result}")  # chỉ chạy khi không lỗi
        return result
    finally:
        print("Kết thúc xu_ly()")       # luôn chạy

xu_ly("42")     # else + finally
xu_ly("abc")    # except ValueError + finally
xu_ly(None)     # except TypeError + finally


# ============================================================
# 6. RAISE — tự throw exception
# ============================================================
# JS: throw new Error("message")
# Python: raise ExceptionType("message")

def dat_tuoi(tuoi):
    if not isinstance(tuoi, int):
        raise TypeError(f"tuoi phải là int, nhận được {type(tuoi).__name__}")
    if tuoi < 0 or tuoi > 150:
        raise ValueError(f"tuoi không hợp lệ: {tuoi}")
    return tuoi

try:
    dat_tuoi(-5)
except ValueError as e:
    print(f"ValueError: {e}")

try:
    dat_tuoi("hai mươi")
except TypeError as e:
    print(f"TypeError: {e}")

# Re-raise — throw lại sau khi log
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        print(f"[LOG] Chia cho 0 với a={a}")
        raise   # re-raise nguyên exception, không mất traceback


# ============================================================
# 7. CUSTOM EXCEPTION — tự tạo loại lỗi riêng
# ============================================================
# JS: class MyError extends Error { constructor(msg) { super(msg) } }

class AppError(Exception):
    """Base exception cho app"""
    pass

class ValidationError(AppError):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"[{field}] {message}")

class NotFoundError(AppError):
    def __init__(self, resource, id):
        super().__init__(f"{resource} với id={id} không tìm thấy")

# Dùng custom exception
def get_user(user_id):
    users = {1: "Vuong", 2: "Alice"}
    if user_id not in users:
        raise NotFoundError("User", user_id)
    return users[user_id]

def validate_email(email):
    if "@" not in email:
        raise ValidationError("email", "Phải có ký tự @")

try:
    get_user(99)
except NotFoundError as e:
    print(e)   # User với id=99 không tìm thấy

try:
    validate_email("not-an-email")
except ValidationError as e:
    print(f"Field: {e.field}, Msg: {e.message}")

# Bắt cả class cha
try:
    get_user(99)
except AppError as e:       # bắt được NotFoundError vì nó là AppError
    print(f"App error: {e}")


# ============================================================
# 8. EXCEPTION CHAINING — Python exclusive
# ============================================================
# Giữ context "lỗi này gây ra bởi lỗi kia"

def parse_config(path):
    try:
        with open(path) as f:
            return json.loads(f.read())
    except FileNotFoundError as e:
        raise RuntimeError(f"Không load được config: {path}") from e
        #                                                       ^^^^^^^
        #                               giữ original exception làm __cause__

try:
    parse_config("config.json")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
    print(f"Caused by: {e.__cause__}")


# ============================================================
# 9. COMMON EXCEPTIONS cần nhớ
# ============================================================
exceptions = {
    "ValueError"      : 'int("abc")  — giá trị sai',
    "TypeError"       : 'len(42)     — sai kiểu',
    "KeyError"        : 'd["missing"]— key không có trong dict',
    "IndexError"      : 'lst[99]     — index out of range',
    "AttributeError"  : 'None.split()— gọi method không tồn tại',
    "FileNotFoundError": 'open("x")  — file không tồn tại',
    "ZeroDivisionError": '1/0        — chia cho 0',
    "ImportError"     : 'import xyz  — module không tồn tại',
    "StopIteration"   : 'next() hết  — dùng trong generator',
    "PermissionError" : 'open("/etc/shadow") — không có quyền',
}
for exc, desc in exceptions.items():
    print(f"{exc:<20} → {desc}")


# ============================================================
# TÓM TẮT SO SÁNH
# ============================================================
print("""
┌──────────────────┬────────────────────┬──────────────────────────┐
│ Tính năng        │ JavaScript         │ Python                   │
├──────────────────┼────────────────────┼──────────────────────────┤
│ Bắt lỗi          │ catch (e) {}       │ except Exception as e:   │
│ Nhiều loại lỗi   │ if (e instanceof)  │ nhiều except block       │
│ Khi không lỗi    │ ❌ không có        │ else: ✅                 │
│ Luôn chạy        │ finally {}         │ finally:                 │
│ Throw            │ throw new Error()  │ raise ValueError()       │
│ Custom error     │ extends Error      │ class E(Exception)       │
│ Re-raise         │ throw e            │ raise (giữ traceback)    │
│ Exception chain  │ ❌ không có        │ raise X from Y ✅        │
└──────────────────┴────────────────────┴──────────────────────────┘
""")
