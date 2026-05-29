"""
Python Data Types — Giải thích cho FE developer (so sánh với JS)
"""

# ============================================================
# 1. LIST  →  giống Array trong JS
# ============================================================
# JS:  const fruits = ["apple", "banana", "cherry"]
fruits = ["apple", "banana", "cherry"]

fruits.append("mango")         # push()
fruits.remove("banana")        # filter ra phần tử đó
fruits.insert(1, "grape")      # splice()
print(fruits[0])               # "apple"   — index bình thường
print(fruits[-1])              # "mango"   — index âm: đếm từ cuối
print(fruits[1:3])             # ['grape', 'cherry'] — slice

# List có thể chứa nhiều kiểu khác nhau (như JS array)
mixed = [1, "hello", True, None, [1, 2]]

# Hay gặp trong interview:
nums = [3, 1, 4, 1, 5, 9]
print(sorted(nums))            # [1, 1, 3, 4, 5, 9] — không đổi original
nums.sort()                    # sort in-place, đổi original
print(len(nums))               # 6


# ============================================================
# 2. DICT  →  giống Object / Map trong JS
# ============================================================
# JS:  const user = { id: 1, name: "Vuong", age: 25 }
user = {"id": 1, "name": "Vuong", "age": 25}

print(user["name"])            # "Vuong"        — truy cập bằng key
print(user.get("email"))       # None           — get() không throw nếu không có key
print(user.get("email", "N/A"))# "N/A"          — default value như ?? trong JS

user["email"] = "v@gmail.com"  # thêm key mới
user["age"] = 26               # update value

# Loop dict — giống Object.entries() trong JS
for key, value in user.items():
    print(f"{key}: {value}")

print(user.keys())    # dict_keys(['id', 'name', 'age', 'email'])
print(user.values())  # dict_values([1, 'Vuong', 26, 'v@gmail.com'])

# Check key tồn tại — giống "key in obj" hoặc hasOwnProperty
print("name" in user)   # True
print("phone" in user)  # False

# Nested dict — giống nested object JS
profile = {
    "user": {
        "name": "Vuong",
        "address": {
            "city": "Da Lat",
            "country": "Vietnam"
        }
    }
}
print(profile["user"]["address"]["city"])  # "Da Lat"


# ============================================================
# 3. TUPLE  →  KHÔNG có trong JS (gần giống Array nhưng immutable)
# ============================================================
# Tuple = list nhưng KHÔNG thể thay đổi sau khi tạo
point = (10, 20)
color = (255, 128, 0)     # RGB
person = ("Vuong", 25, "Da Lat")

print(point[0])     # 10
print(point[-1])    # 20

# Không thể thay đổi — đây là điểm khác list
# point[0] = 99   # ❌ TypeError: 'tuple' object does not support item assignment

# Unpacking — rất hay dùng, giống destructuring trong JS
# JS: const [x, y] = point
x, y = point
print(x, y)     # 10 20

name, age, city = person
print(name, age, city)  # Vuong 25 Da Lat

# Dùng tuple khi nào?
# → Trả về nhiều giá trị từ function (JS thường dùng object)
def get_min_max(nums: list) -> tuple[int, int]:
    return min(nums), max(nums)

lo, hi = get_min_max([3, 1, 4, 1, 5, 9])
print(f"min={lo}, max={hi}")   # min=1, max=9

# → Làm key của dict (list không làm được vì mutable)
locations = {}
locations[(10, 20)] = "Da Lat"   # tuple làm key ✅
# locations[[10, 20]] = "Da Lat" # ❌ list không làm key được


# ============================================================
# 4. SET  →  giống Set trong JS (ES6)
# ============================================================
# JS: const unique = new Set([1, 2, 2, 3, 3])
unique = {1, 2, 2, 3, 3, 3}
print(unique)       # {1, 2, 3} — tự xóa duplicate

unique.add(4)       # thêm phần tử
unique.remove(1)    # xóa phần tử

# Dùng set để xóa duplicate trong list — rất hay gặp trong interview
nums = [1, 2, 2, 3, 3, 3, 4]
no_dup = list(set(nums))
print(no_dup)       # [1, 2, 3, 4]

# Set operations — rất mạnh
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a & b)        # {3, 4}        — intersection (giao)
print(a | b)        # {1,2,3,4,5,6} — union (hợp)
print(a - b)        # {1, 2}        — difference (hiệu)
print(a ^ b)        # {1,2,5,6}     — symmetric difference

# Check membership — O(1), nhanh hơn list O(n)
print(3 in a)       # True


# ============================================================
# 5. NONE  →  giống null trong JS (không phải undefined)
# ============================================================
result = None

# Kiểm tra None dùng "is", không dùng "=="
if result is None:
    print("Chưa có kết quả")

# Hay gặp khi function không return gì
def do_something():
    x = 1 + 1
    # không có return

val = do_something()
print(val)          # None


# ============================================================
# BẢNG TÓM TẮT
# ============================================================
print("""
┌────────────┬─────────────┬────────────┬──────────────────────────┐
│ Python     │ JS tương đương│ Mutable?  │ Dùng khi nào             │
├────────────┼─────────────┼────────────┼──────────────────────────┤
│ list       │ Array       │ ✅ Yes     │ Danh sách thay đổi được  │
│ dict       │ Object/Map  │ ✅ Yes     │ Key-value, JSON-like      │
│ tuple      │ (không có)  │ ❌ No      │ Return nhiều giá trị,     │
│            │             │           │ làm dict key              │
│ set        │ Set (ES6)   │ ✅ Yes     │ Unique values, so sánh   │
│            │             │           │ tập hợp                  │
│ None       │ null        │ —          │ Giá trị rỗng/chưa có     │
└────────────┴─────────────┴────────────┴──────────────────────────┘
""")
