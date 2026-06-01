"""
Python Modules — So sánh với JavaScript import/export
"""

# ============================================================
# 1. IMPORT CƠ BẢN
# ============================================================
# JS (CommonJS):  const math = require('math')
# JS (ES6):       import math from 'math'
# Python:

import math
import os
import json

print(math.pi)          # 3.14159...
print(math.sqrt(16))    # 4.0
print(os.getcwd())      # thư mục hiện tại


# ============================================================
# 2. FROM ... IMPORT — import cụ thể
# ============================================================
# JS:  import { sqrt, pi } from 'math'
# Python:

from math import sqrt, pi, ceil, floor

print(sqrt(25))   # 5.0  — không cần math.sqrt
print(pi)         # 3.14...
print(ceil(3.2))  # 4
print(floor(3.9)) # 3

# Import tất cả — TRÁNH DÙNG trong production
# from math import *   # ô nhiễm namespace


# ============================================================
# 3. ALIAS — import với tên khác
# ============================================================
# JS:  import * as np from 'numpy'
# Python:

import numpy as np          # convention — ai cũng dùng np
import pandas as pd          # convention — ai cũng dùng pd
import datetime as dt

from collections import defaultdict as dd

# Alias hay thấy trong codebase Python:
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import tensorflow as tf
# import torch


# ============================================================
# 4. __name__ == "__main__" — QUAN TRỌNG
# ============================================================
# Không có khái niệm tương đương trong JS (Node có process.argv)
# Đây là điểm hay bị hỏi nhất về modules!

# Khi Python chạy 1 file:
#   - file được chạy trực tiếp → __name__ = "__main__"
#   - file được import bởi file khác → __name__ = tên module

def tinh_tong(a, b):
    return a + b

def main():
    print("Đang chạy trực tiếp!")
    print(tinh_tong(3, 4))

if __name__ == "__main__":
    main()
# → Khi import module này, main() sẽ KHÔNG tự chạy
# → Khi chạy trực tiếp: python modules.py → main() chạy


# ============================================================
# 5. STANDARD LIBRARY — hay dùng nhất
# ============================================================

# --- os: thao tác file system ---
import os
print(os.path.exists("README.md"))      # True/False
print(os.path.join("folder", "file.txt"))  # folder/file.txt
print(os.path.dirname("/home/user/file.py"))  # /home/user
print(os.path.basename("/home/user/file.py")) # file.py
os.makedirs("temp/nested", exist_ok=True)  # mkdir -p

# --- pathlib: OOP way (Python 3.4+, dùng cái này đi) ---
from pathlib import Path

p = Path(".")
print(p.resolve())              # absolute path
print(list(p.glob("*.py")))    # tất cả file .py
p2 = Path("/home/user") / "docs" / "file.txt"  # path join đẹp hơn
print(p2.suffix)   # ".txt"
print(p2.stem)     # "file"
print(p2.parent)   # /home/user/docs

# --- datetime ---
from datetime import datetime, timedelta

now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))
tomorrow = now + timedelta(days=1)
diff = tomorrow - now
print(diff.days)   # 1

# --- collections: cấu trúc dữ liệu nâng cao ---
from collections import Counter, defaultdict, deque, namedtuple

# Counter — đếm phần tử
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
count = Counter(words)
print(count)                    # Counter({'apple': 3, 'banana': 2, ...})
print(count.most_common(2))     # [('apple', 3), ('banana', 2)]

# defaultdict — dict không throw KeyError khi key không có
scores = defaultdict(list)
scores["Alice"].append(90)      # không cần khởi tạo key trước
scores["Alice"].append(85)
scores["Bob"].append(78)
print(dict(scores))             # {'Alice': [90, 85], 'Bob': [78]}

# deque — double-ended queue, O(1) append/pop cả hai đầu
dq = deque([1, 2, 3])
dq.appendleft(0)    # [0, 1, 2, 3]
dq.append(4)        # [0, 1, 2, 3, 4]
dq.popleft()        # 0, còn [1, 2, 3, 4]

# namedtuple — tuple với tên field (nhẹ hơn class)
Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(p.x, p.y)     # 10 20
print(p[0], p[1])   # 10 20 — vẫn access bằng index được

# --- itertools: công cụ iterator nâng cao ---
from itertools import chain, combinations, permutations, product

# chain — nối nhiều iterable
print(list(chain([1,2], [3,4], [5,6])))  # [1,2,3,4,5,6]

# combinations — tổ hợp (không lặp, không quan tâm thứ tự)
print(list(combinations([1,2,3], 2)))    # [(1,2),(1,3),(2,3)]

# permutations — hoán vị (quan tâm thứ tự)
print(list(permutations([1,2,3], 2)))   # [(1,2),(1,3),(2,1)...]

# --- functools ---
from functools import lru_cache, reduce, partial

# lru_cache — memoize function (cache kết quả)
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(40))   # nhanh vì được cache

# reduce — JS: array.reduce()
total = reduce(lambda acc, x: acc + x, [1,2,3,4,5])
print(total)   # 15

# partial — tạo function mới với một số args cố định
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)
print(square(5))   # 25
print(cube(3))     # 27


# ============================================================
# 6. PACKAGE — thư mục chứa nhiều modules
# ============================================================
# Cấu trúc package:
# mypackage/
# ├── __init__.py      ← đánh dấu đây là package (có thể empty)
# ├── utils.py
# ├── models.py
# └── services/
#     ├── __init__.py
#     └── payment.py

# Import từ package:
# from mypackage import utils
# from mypackage.services import payment
# from mypackage.services.payment import charge

# __init__.py có thể export gọn:
# mypackage/__init__.py:
#   from .utils import helper_func
#   from .models import User
# → bên ngoài: from mypackage import helper_func, User


# ============================================================
# 7. RELATIVE vs ABSOLUTE IMPORT (trong package)
# ============================================================
# Absolute — từ root của project (recommended)
# from mypackage.utils import helper

# Relative — từ vị trí file hiện tại
# from .utils import helper        # cùng package
# from ..models import User        # package cha
# from ..services.payment import charge  # package cha / subpackage


# ============================================================
# TÓM TẮT SO SÁNH
# ============================================================
print("""
┌──────────────────────┬──────────────────────┬────────────────────────────┐
│ Tính năng            │ JavaScript           │ Python                     │
├──────────────────────┼──────────────────────┼────────────────────────────┤
│ Import module        │ import x from 'x'    │ import x                   │
│ Import cụ thể        │ import { a } from 'x'│ from x import a            │
│ Import alias         │ import x as y        │ import x as y              │
│ Import tất cả        │ import * as x        │ from x import * (tránh)   │
│ Chạy trực tiếp       │ if (require.main)    │ if __name__=="__main__"    │
│ Package marker       │ package.json         │ __init__.py                │
│ Relative import      │ import './utils'     │ from .utils import ...     │
│ Install package      │ npm install          │ pip install                │
│ Lock file            │ package-lock.json    │ requirements.txt / uv.lock │
└──────────────────────┴──────────────────────┴────────────────────────────┘

Standard library hay dùng:
  os / pathlib    → file system
  json            → parse/stringify JSON
  datetime        → date/time
  collections     → Counter, defaultdict, deque, namedtuple
  itertools       → chain, combinations, permutations
  functools       → lru_cache, reduce, partial
  re              → regex
  typing          → type hints
""")
