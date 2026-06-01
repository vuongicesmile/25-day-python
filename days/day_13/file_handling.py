"""
Section 25 & 26 — File Handling: Reading, Writing, Appending, JSON
+ Final: Python Docs & Best Practices
"""

import json
import os
from pathlib import Path

# ============================================================
# 130. READING FILES
# ============================================================
# JS (Node): fs.readFileSync() / fs.readFile()
# Python: open() với context manager (with)

# Tạo file test trước
Path("test.txt").write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

# Cách 1: read() — đọc toàn bộ file vào 1 string
with open("test.txt", "r") as f:
    content = f.read()
    print(content)
# "Line 1\nLine 2\n..."

# Cách 2: readlines() — đọc vào list, mỗi dòng 1 phần tử
with open("test.txt", "r") as f:
    lines = f.readlines()
    print(lines)   # ['Line 1\n', 'Line 2\n', ...]

# Cách 3: readline() — đọc từng dòng
with open("test.txt", "r") as f:
    first  = f.readline()   # "Line 1\n"
    second = f.readline()   # "Line 2\n"

# Cách 4: loop trực tiếp — PYTHONIC & tiết kiệm RAM nhất
with open("test.txt", "r") as f:
    for line in f:              # lazy — đọc từng dòng
        print(line.strip())     # strip() bỏ \n cuối

# Cách 5: pathlib — hiện đại nhất
content = Path("test.txt").read_text()
lines   = Path("test.txt").read_text().splitlines()  # không có \n

# ⚠️ Tại sao dùng "with"?
# with tự động gọi f.close() khi xong, dù có exception hay không
# Không dùng with → dễ quên close() → memory leak

# Encoding — quan trọng với tiếng Việt
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()

# File modes:
# "r"  → read (default)
# "w"  → write (tạo mới hoặc ghi đè)
# "a"  → append (thêm vào cuối)
# "rb" → read binary
# "wb" → write binary
# "r+" → read + write


# ============================================================
# 131. WRITING FILES
# ============================================================
# JS (Node): fs.writeFileSync("file", content)

# write() — tạo mới hoặc GHI ĐÈ toàn bộ
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Dòng 1\n")
    f.write("Dòng 2\n")
    f.write("Dòng 3\n")

# writelines() — ghi list of strings
lines = ["Alice\n", "Bob\n", "Carol\n"]
with open("names.txt", "w") as f:
    f.writelines(lines)

# pathlib — gọn nhất
Path("quick.txt").write_text("Nội dung file\n", encoding="utf-8")

# ⚠️ "w" sẽ XÓA nội dung cũ nếu file đã tồn tại!
# Kiểm tra file tồn tại trước
if not Path("important.txt").exists():
    Path("important.txt").write_text("Dữ liệu quan trọng")


# ============================================================
# 132. APPENDING — thêm vào cuối file
# ============================================================
# JS (Node): fs.appendFileSync()

# "a" mode — KHÔNG xóa nội dung cũ, thêm vào cuối
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("2026-06-01 10:00: User login\n")
    f.write("2026-06-01 10:05: User logout\n")

# Chạy lại → thêm vào cuối, không ghi đè

# Ứng dụng thực tế: logging
from datetime import datetime

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("app.log", "a") as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

log("Server started", "INFO")
log("DB connected",   "INFO")
log("High memory!",   "WARNING")

# Đọc lại log
print(Path("app.log").read_text())


# ============================================================
# 133. JSON — đọc & ghi dữ liệu JSON
# ============================================================
# JS: JSON.parse() / JSON.stringify()
# Python: json.loads() / json.dumps()  hoặc  json.load() / json.dump()

# --- String ↔ Dict ---
# JS:     JSON.parse(str)     → object
# Python: json.loads(str)     → dict   (loads = load STRING)

json_str = '{"name": "Vuong", "age": 25, "skills": ["Python", "React"]}'
data = json.loads(json_str)
print(data["name"])     # Vuong
print(data["skills"])   # ['Python', 'React']
print(type(data))       # <class 'dict'>

# JS:     JSON.stringify(obj)          → string
# Python: json.dumps(dict)             → string (dumps = dump STRING)

user = {"name": "Alice", "age": 30, "active": True}
json_str = json.dumps(user)
print(json_str)   # '{"name": "Alice", "age": 30, "active": true}'

# Formatting đẹp hơn
pretty = json.dumps(user, indent=2, ensure_ascii=False)
print(pretty)
# {
#   "name": "Alice",
#   "age": 30,
#   "active": true
# }

# --- File ↔ Dict ---
# json.dump()  → ghi dict vào FILE (không có s)
# json.load()  → đọc FILE thành dict (không có s)

# Ghi JSON ra file
config = {
    "database": {"host": "localhost", "port": 5432, "name": "mydb"},
    "cache":    {"ttl": 3600, "max_size": 1000},
    "debug":    False
}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

# Đọc JSON từ file
with open("config.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(loaded["database"]["host"])   # localhost
print(loaded["cache"]["ttl"])       # 3600

# Shorthand với pathlib
Path("data.json").write_text(json.dumps(config, indent=2))
loaded = json.loads(Path("data.json").read_text())

# Type mapping: Python ↔ JSON
# dict    ↔ object {}
# list    ↔ array  []
# str     ↔ string ""
# int     ↔ number
# float   ↔ number
# True    ↔ true
# False   ↔ false
# None    ↔ null

# ⚠️ Không phải mọi Python object đều JSON serializable
import datetime

data = {"date": datetime.datetime.now()}
# json.dumps(data)  # ❌ TypeError: Object of type datetime is not JSON serializable

# Fix: custom encoder
def json_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

print(json.dumps(data, default=json_serializer))
# {"date": "2026-06-01T10:30:00"}


# ============================================================
# 134. PROJECT: NOTES APP
# ============================================================
NOTES_FILE = "notes.json"

def load_notes() -> list:
    if not Path(NOTES_FILE).exists():
        return []
    return json.loads(Path(NOTES_FILE).read_text(encoding="utf-8"))

def save_notes(notes: list):
    Path(NOTES_FILE).write_text(
        json.dumps(notes, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def add_note(title: str, content: str):
    notes = load_notes()
    note  = {
        "id"      : len(notes) + 1,
        "title"   : title,
        "content" : content,
        "created" : datetime.datetime.now().isoformat(),
    }
    notes.append(note)
    save_notes(notes)
    print(f"✅ Đã thêm: '{title}'")
    return note

def list_notes():
    notes = load_notes()
    if not notes:
        print("Chưa có ghi chú nào")
        return
    print(f"\n{'ID':<4} {'TITLE':<20} {'CREATED'}")
    print("─" * 50)
    for n in notes:
        created = n["created"][:10]
        print(f"{n['id']:<4} {n['title']:<20} {created}")

def delete_note(note_id: int) -> bool:
    notes = load_notes()
    new_notes = [n for n in notes if n["id"] != note_id]
    if len(new_notes) == len(notes):
        print(f"❌ Không tìm thấy note ID={note_id}")
        return False
    save_notes(new_notes)
    print(f"🗑  Đã xóa note ID={note_id}")
    return True

def search_notes(keyword: str) -> list:
    notes = load_notes()
    return [
        n for n in notes
        if keyword.lower() in n["title"].lower()
        or keyword.lower() in n["content"].lower()
    ]

# Demo
add_note("Python Tips", "Dùng list comprehension thay vì map/filter")
add_note("FastAPI", "Pydantic validate input tự động")
add_note("Git", "git rebase -i HEAD~3 để squash commits")

list_notes()

results = search_notes("python")
print(f"\nTìm kiếm 'python': {len(results)} kết quả")

delete_note(2)
list_notes()


# ============================================================
# 136 & 137. PYTHON DOCS & AI-ASSISTED LEARNING
# ============================================================
# Tài liệu Python quan trọng nhất:
resources = {
    "Official Docs"   : "https://docs.python.org/3/",
    "Built-ins"       : "https://docs.python.org/3/library/functions.html",
    "Standard Library": "https://docs.python.org/3/library/",
    "PEP 8 Style"     : "https://peps.python.org/pep-0008/",
    "Type Hints"      : "https://docs.python.org/3/library/typing.html",
    "Async IO"        : "https://docs.python.org/3/library/asyncio.html",
    "Real Python"     : "https://realpython.com",
    "PyPI packages"   : "https://pypi.org",
}

# Dùng help() và dir() để explore
# help(list)         → full documentation của list
# help(str.split)    → documentation của method cụ thể
# dir(list)          → tất cả attributes & methods
# dir("")            → tất cả string methods

print("\n" + "="*55)
print("🎉 HOÀN THÀNH 25 DAYS PYTHON!")
print("="*55)
print("""
Tóm tắt những gì đã học:
 Day 1-5  : Basics — Data types, operators, control flow
 Day 6-9  : Functions — args, kwargs, */, exceptions, modules
 Day 10-12: Built-ins — enumerate, map, filter, sorted, ...
 Day 13-15: OOP — classes, inheritance, dunder methods
 Day 16-18: Advanced — decorators, generators, async/await
 Day 19-21: More built-ins & misc — all/any/isinstance/match
 Day 22-23: Async — asyncio, tasks, gather
 Day 24-25: File handling — read/write/JSON
 
Bước tiếp theo để phỏng vấn:
 1. Practice: LeetCode Easy/Medium bằng Python
 2. Build: 1 REST API với FastAPI
 3. Read: Real Python articles
 4. Review: Từng topic và giải thích bằng lời
""")
