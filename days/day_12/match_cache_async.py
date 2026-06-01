"""
Section 23 & 24 — match, @lru_cache, AsyncIO, Tasks, Gather
"""

# ============================================================
# 123. MATCH — structural pattern matching (Python 3.10+)
# ============================================================
# JS: switch/case — chỉ so sánh value đơn giản
# Python match: so sánh STRUCTURE, type, pattern — mạnh hơn nhiều

# Basic — giống switch
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:            # default
            return f"Unknown: {status}"

print(http_status(200))   # OK
print(http_status(404))   # Not Found
print(http_status(999))   # Unknown: 999

# Match với OR (|)
def classify_status(code):
    match code:
        case 200 | 201 | 204:
            return "Success"
        case 400 | 422:
            return "Client Error"
        case 401 | 403:
            return "Auth Error"
        case 500 | 502 | 503:
            return "Server Error"
        case _:
            return "Other"

# Match với TYPE — cực mạnh, JS không làm được!
def process(value):
    match value:
        case int(n) if n > 0:
            return f"Positive int: {n}"
        case int(n):
            return f"Non-positive int: {n}"
        case str(s) if len(s) > 5:
            return f"Long string: {s}"
        case str(s):
            return f"Short string: {s}"
        case [x, y]:            # list 2 phần tử
            return f"2-item list: {x}, {y}"
        case [first, *rest]:    # list nhiều phần tử
            return f"List starts with {first}, rest: {rest}"
        case None:
            return "None value"
        case _:
            return "Unknown"

print(process(42))           # Positive int: 42
print(process(-5))           # Non-positive int: -5
print(process("hi"))         # Short string: hi
print(process("hello world"))# Long string: hello world
print(process([1, 2]))       # 2-item list: 1, 2
print(process([1, 2, 3, 4])) # List starts with 1, rest: [2, 3, 4]

# Match với dict pattern
def handle_command(command: dict):
    match command:
        case {"action": "move", "direction": direction}:
            return f"Moving {direction}"
        case {"action": "attack", "weapon": weapon}:
            return f"Attacking with {weapon}"
        case {"action": "quit"}:
            return "Quitting game"
        case {"action": action}:
            return f"Unknown action: {action}"
        case _:
            return "Invalid command"

print(handle_command({"action": "move", "direction": "north"}))
print(handle_command({"action": "attack", "weapon": "sword"}))
print(handle_command({"action": "quit"}))

# Match với class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def where_is(point):
    match point:
        case Point(x=0, y=0):
            return "Origin"
        case Point(x=0, y=y):
            return f"Y-axis at y={y}"
        case Point(x=x, y=0):
            return f"X-axis at x={x}"
        case Point(x=x, y=y):
            return f"Point at ({x}, {y})"


# ============================================================
# 124. @lru_cache — memoization tự động
# ============================================================
# JS: phải tự implement cache với Map
# Python: 1 dòng decorator

from functools import lru_cache
import time

# Không cache — tính lại mỗi lần
def fib_slow(n):
    if n < 2: return n
    return fib_slow(n-1) + fib_slow(n-2)

# Có @lru_cache — cache kết quả
@lru_cache(maxsize=128)   # cache tối đa 128 kết quả gần nhất
def fib_fast(n):
    if n < 2: return n
    return fib_fast(n-1) + fib_fast(n-2)

# So sánh tốc độ
start = time.time()
fib_slow(35)
print(f"Không cache: {time.time()-start:.3f}s")   # ~2-3s

start = time.time()
fib_fast(35)
print(f"Có cache:    {time.time()-start:.6f}s")   # ~0.0001s

# Cache info
print(fib_fast.cache_info())
# CacheInfo(hits=..., misses=36, maxsize=128, currsize=36)

# Clear cache
fib_fast.cache_clear()

# @cache (Python 3.9+) — maxsize=None, unbounded cache
from functools import cache

@cache
def expensive_api(user_id: int):
    # giả lập API call
    time.sleep(0.1)
    return {"id": user_id, "name": f"User_{user_id}"}

start = time.time()
expensive_api(1)   # 0.1s — call thật
expensive_api(1)   # instant — từ cache
expensive_api(2)   # 0.1s — call thật
print(f"Total: {time.time()-start:.2f}s")   # ~0.2s thay vì 0.3s

# ⚠️ @lru_cache chỉ dùng được với HASHABLE arguments
# list, dict không hashable → dùng tuple thay thế
@lru_cache
def process(items: tuple):   # tuple, không phải list
    return sum(items)

print(process((1, 2, 3)))   # OK


# ============================================================
# 126. ASYNCIO — async/await
# ============================================================
# JS: async/await — giống nhau về concept!
# Python: asyncio library

import asyncio

# Cơ bản: async function (coroutine)
async def greet(name):
    print(f"Hello {name}!")
    await asyncio.sleep(1)   # giống JS: await sleep(1000)
    print(f"Goodbye {name}!")

# Chạy coroutine
# asyncio.run(greet("Vuong"))   # entry point

# Vì sao cần async?
# I/O bound tasks: network, DB, file — CPU nghỉ chờ
# Async: trong khi chờ I/O → chạy task khác

# Sequential (chậm)
async def fetch_sequential():
    start = time.time()

    await asyncio.sleep(1)   # giả lập API call 1 (1s)
    await asyncio.sleep(1)   # giả lập API call 2 (1s)
    await asyncio.sleep(1)   # giả lập API call 3 (1s)

    print(f"Sequential: {time.time()-start:.1f}s")   # ~3s

# Concurrent (nhanh)
async def fetch_concurrent():
    start = time.time()

    # 128. gather — chạy nhiều coroutine ĐỒNG THỜI
    await asyncio.gather(
        asyncio.sleep(1),    # 3 cái này chạy CÙNG LÚC
        asyncio.sleep(1),
        asyncio.sleep(1),
    )

    print(f"Concurrent: {time.time()-start:.1f}s")   # ~1s!


# ============================================================
# 127. TASKS — chạy coroutine nền
# ============================================================
async def download(url, delay):
    print(f"  Bắt đầu download: {url}")
    await asyncio.sleep(delay)   # giả lập network delay
    print(f"  Xong: {url} ({delay}s)")
    return f"content of {url}"

async def main_tasks():
    print("=== Tasks example ===")

    # Tạo tasks — bắt đầu chạy NGAY, không cần await
    task1 = asyncio.create_task(download("site1.com", 2))
    task2 = asyncio.create_task(download("site2.com", 1))
    task3 = asyncio.create_task(download("site3.com", 3))

    # Await từng task
    r1 = await task1
    r2 = await task2
    r3 = await task3

    print(f"Results: {r1}, {r2}, {r3}")
    # site2 xong trước (1s), rồi site1 (2s), rồi site3 (3s)
    # Tổng thời gian: ~3s (không phải 6s!)


# ============================================================
# 128. GATHER — chạy nhiều coroutines đồng thời
# ============================================================
async def main_gather():
    print("=== Gather example ===")
    start = time.time()

    # gather: chạy tất cả CÙNG LÚC, đợi tất cả xong
    results = await asyncio.gather(
        download("a.com", 1),
        download("b.com", 2),
        download("c.com", 1.5),
    )

    print(f"Tất cả xong sau: {time.time()-start:.1f}s")
    print(f"Results: {results}")   # list theo thứ tự đưa vào

    # gather với return_exceptions=True — không stop khi có error
    results = await asyncio.gather(
        download("ok.com", 1),
        asyncio.sleep(0),          # dummy coroutine
        download("ok2.com", 0.5),
        return_exceptions=True
    )

# Task vs Gather:
# create_task → tạo task chạy nền, control từng cái
# gather      → chạy nhiều coroutines, lấy tất cả kết quả cùng lúc


# ============================================================
# 129. PROJECT: WEBSITE STATUS CHECKER
# ============================================================
import asyncio
import random

# Giả lập check website (thực tế dùng aiohttp)
async def check_website(url: str) -> dict:
    delay = random.uniform(0.1, 2.0)   # giả lập response time
    await asyncio.sleep(delay)

    # Giả lập: 80% OK, 20% DOWN
    status = "UP" if random.random() > 0.2 else "DOWN"
    code   = 200 if status == "UP" else random.choice([500, 503, 404])

    return {
        "url"    : url,
        "status" : status,
        "code"   : code,
        "time_ms": round(delay * 1000),
    }

async def check_all_websites(urls: list[str]) -> list[dict]:
    print(f"Checking {len(urls)} websites concurrently...")
    start = time.time()

    results = await asyncio.gather(
        *[check_website(url) for url in urls]
    )

    elapsed = time.time() - start
    return results, elapsed

async def website_status_report():
    websites = [
        "google.com", "github.com", "stackoverflow.com",
        "python.org",  "fastapi.tiangolo.com", "reddit.com",
        "youtube.com", "netflix.com", "shopee.vn",
    ]

    results, elapsed = await check_all_websites(websites)

    # Report
    up   = [r for r in results if r["status"] == "UP"]
    down = [r for r in results if r["status"] == "DOWN"]

    print(f"\n{'='*55}")
    print(f"{'WEBSITE STATUS REPORT':^55}")
    print(f"{'='*55}")

    for r in sorted(results, key=lambda x: x["time_ms"]):
        icon = "✅" if r["status"] == "UP" else "❌"
        print(f"{icon} {r['url']:<30} {r['code']}  {r['time_ms']}ms")

    print(f"{'─'*55}")
    print(f"Total: {len(results)} | Up: {len(up)} | Down: {len(down)}")
    print(f"Checked {len(results)} sites in {elapsed:.2f}s")
    print(f"(Sequential would take ~{sum(r['time_ms'] for r in results)/1000:.1f}s)")

# Chạy async main
asyncio.run(website_status_report())


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌─────────────────────┬──────────────────────────────┬──────────────────┐
│ Topic               │ Key point                    │ JS tương đương   │
├─────────────────────┼──────────────────────────────┼──────────────────┤
│ match/case          │ Pattern matching mạnh hơn    │ switch/case      │
│                     │ match type, struct, guard    │ (kém hơn nhiều)  │
│ @lru_cache(n)       │ Auto memoize, cache n items  │ tự implement Map │
│ @cache              │ Unbounded cache (3.9+)       │ ❌               │
│ async def           │ Coroutine function           │ async function   │
│ await               │ Chờ coroutine xong           │ await            │
│ asyncio.run()       │ Entry point chạy async       │ (tự động trong  │
│                     │                              │  JS runtime)     │
│ create_task()       │ Tạo task chạy nền ngay       │ Promise / then   │
│ asyncio.gather()    │ Chạy nhiều coros đồng thời   │ Promise.all()    │
├─────────────────────┼──────────────────────────────┴──────────────────┤
│ Async Gotchas       │ async fn phải await để chạy                     │
│                     │ asyncio.run() chỉ gọi 1 lần (top level)        │
│                     │ @lru_cache: args phải hashable (tuple, not list)│
│                     │ gather([...]) → * để unpack: gather(*list)      │
└─────────────────────┴──────────────────────────────────────────────────┘
""")
