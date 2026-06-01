"""
OOP in Python — Từ cơ bản đến Dunder Methods
So sánh với JavaScript class
"""

# ============================================================
# 72 & 73. OOP LÀ GÌ? CLASS & OBJECT
# ============================================================
# OOP = lập trình hướng đối tượng
# Class = bản thiết kế (blueprint)
# Object = thực thể được tạo ra từ class (instance)

# Ví dụ thực tế:
# Class = Thiết kế xe hơi
# Object = Chiếc xe cụ thể chạy trên đường

# JS:
# class Car {
#   constructor(brand, model) {
#     this.brand = brand
#     this.model = model
#   }
# }

# Python:
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

car1 = Car("Toyota", "Camry")
car2 = Car("Honda", "Civic")

print(car1.brand)   # "Toyota"
print(car2.model)   # "Civic"
print(type(car1))   # <class '__main__.Car'>


# ============================================================
# 74. __init__() — CONSTRUCTOR
# ============================================================
# JS:  constructor() { }
# Py:  def __init__(self): — chạy tự động khi tạo object

class Person:
    def __init__(self, name, age):
        # self.name, self.age là INSTANCE ATTRIBUTES
        # Mỗi object có bản sao riêng của chúng
        self.name = name
        self.age = age

    def greet(self):
        return f"Hi, tôi là {self.name}, {self.age} tuổi"

p1 = Person("Vuong", 25)
p2 = Person("Alice", 30)

print(p1.greet())   # Hi, tôi là Vuong, 25 tuổi
print(p2.greet())   # Hi, tôi là Alice, 30 tuổi

# p1 và p2 hoàn toàn độc lập
p1.age = 26         # chỉ thay đổi p1
print(p1.age)       # 26
print(p2.age)       # 30 — không bị ảnh hưởng


# ============================================================
# 75. SELF — là gì?
# ============================================================
# JS: this → tự động có
# Python: self → phải khai báo tường minh làm param đầu tiên

# self = tham chiếu đến object hiện tại
# Khi gọi p1.greet() → Python tự chuyển thành Person.greet(p1)

class Dog:
    def __init__(self, name):
        self.name = name        # self = con chó này

    def bark(self):
        print(f"{self.name} sủa: Woof!")   # self.name = tên của chó này

    def meet(self, other_dog):
        print(f"{self.name} gặp {other_dog.name}")

rex = Dog("Rex")
buddy = Dog("Buddy")

rex.bark()          # Rex sủa: Woof!
buddy.bark()        # Buddy sủa: Woof!
rex.meet(buddy)     # Rex gặp Buddy

# Tên "self" là convention — có thể đặt tên khác nhưng ĐỪNG làm vậy
class WeirdExample:
    def __init__(this, name):   # "this" thay self — hợp lệ nhưng kỳ
        this.name = name


# ============================================================
# 77. INSTANCE ATTRIBUTES vs 78. CLASS ATTRIBUTES
# ============================================================
# Instance attribute → riêng của mỗi object
# Class attribute    → chung cho tất cả objects của class

class BankAccount:
    # CLASS ATTRIBUTE — chung cho tất cả
    bank_name = "VietinBank"
    interest_rate = 0.05
    total_accounts = 0   # đếm số tài khoản đã tạo

    def __init__(self, owner, balance=0):
        # INSTANCE ATTRIBUTES — riêng mỗi object
        self.owner = owner
        self.balance = balance

        # Tăng class attribute khi tạo account mới
        BankAccount.total_accounts += 1

    def deposit(self, amount):
        self.balance += amount
        print(f"{self.owner} nạp {amount}. Số dư: {self.balance}")

    def get_interest(self):
        # Dùng cả instance và class attribute
        return self.balance * BankAccount.interest_rate

acc1 = BankAccount("Vuong", 1000)
acc2 = BankAccount("Alice", 5000)

print(acc1.bank_name)           # "VietinBank" — từ class
print(acc2.bank_name)           # "VietinBank" — cùng 1 giá trị
print(BankAccount.total_accounts)  # 2

acc1.deposit(500)
print(acc1.balance)   # 1500
print(acc2.balance)   # 5000 — không bị ảnh hưởng

# Thay đổi class attribute → ảnh hưởng tất cả
BankAccount.interest_rate = 0.07
print(acc1.get_interest())   # 1500 * 0.07 = 105.0
print(acc2.get_interest())   # 5000 * 0.07 = 350.0

# Override class attribute ở instance → chỉ ảnh hưởng instance đó
acc1.interest_rate = 0.10    # tạo INSTANCE attribute, không sửa CLASS
print(acc1.interest_rate)    # 0.10 — của riêng acc1
print(acc2.interest_rate)    # 0.07 — vẫn của class


# ============================================================
# 79. DUNDER METHODS — Magic Methods
# ============================================================
# Dunder = Double UNDERscore → __method__
# Python tự gọi chúng trong các tình huống đặc biệt

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # 80. __str__ — cho con người đọc (print(), str())
    # JS: toString()
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    # 80. __repr__ — cho developer debug (repr(), console)
    # Nên trả về string có thể dùng để tái tạo object
    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

    # 81. __eq__ — so sánh bằng ==
    # JS: không có, phải override valueOf hay dùng custom compare
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # __add__ — phép cộng +
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    # __len__ — hàm len()
    def __len__(self):
        return int((self.x**2 + self.y**2) ** 0.5)

    # __bool__ — truthy/falsy
    def __bool__(self):
        return self.x != 0 or self.y != 0

    # __getitem__ — truy cập bằng index v[0]
    def __getitem__(self, index):
        return (self.x, self.y)[index]


v1 = Vector(3, 4)
v2 = Vector(3, 4)
v3 = Vector(1, 2)

print(str(v1))      # "Vector(3, 4)"   → __str__
print(repr(v1))     # "Vector(x=3, y=4)" → __repr__
print(v1 == v2)     # True  → __eq__
print(v1 == v3)     # False → __eq__
print(v1 + v3)      # Vector(4, 6) → __add__ + __str__
print(len(v1))      # 5 → __len__ (3,4,5 tam giác vuông)
print(bool(v1))     # True → __bool__
print(v1[0])        # 3 → __getitem__


# ============================================================
# 80. __str__ vs __repr__ — điểm khác nhau
# ============================================================
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name}: ${self.price}"      # cho user xem

    def __repr__(self):
        return f"Product('{self.name}', {self.price})"  # cho dev debug

p = Product("Laptop", 999)
print(p)            # Product: $999   → __str__ (print dùng __str__)
print(str(p))       # Product: $999   → __str__
print(repr(p))      # Product('Laptop', 999) → __repr__

# Nếu chỉ define __repr__, nó sẽ được dùng cho cả str()
# Nếu chỉ define __str__, repr() vẫn dùng default xấu xí

products = [Product("A", 10), Product("B", 20)]
print(products)     # dùng __repr__ cho từng item trong list!


# ============================================================
# 76 & 82. PROJECT: CAR FACTORY
# ============================================================
class Car:
    # Class attributes
    total_cars = 0

    def __init__(self, brand, model, year, color="white"):
        self.brand  = brand
        self.model  = model
        self.year   = year
        self.color  = color
        self.speed  = 0
        self.is_stolen = False

        Car.total_cars += 1
        self.car_id = Car.total_cars

    def accelerate(self, amount):
        self.speed += amount
        print(f"{self} tăng tốc lên {self.speed} km/h")

    def brake(self, amount):
        self.speed = max(0, self.speed - amount)
        print(f"{self} phanh còn {self.speed} km/h")

    def repaint(self, color):
        print(f"{self} đổi màu: {self.color} → {color}")
        self.color = color

    # Dunder methods
    def __str__(self):
        return f"{self.year} {self.brand} {self.model} ({self.color})"

    def __repr__(self):
        return f"Car('{self.brand}', '{self.model}', {self.year})"

    def __eq__(self, other):
        return self.car_id == other.car_id

    def __bool__(self):
        return not self.is_stolen

# Car theft identifier (82)
class CarRegistry:
    def __init__(self):
        self.cars = {}

    def register(self, car, owner):
        self.cars[car.car_id] = {"car": car, "owner": owner}
        print(f"Đăng ký: {car} — Chủ: {owner}")

    def report_stolen(self, car):
        if car.car_id in self.cars:
            car.is_stolen = True
            print(f"🚨 Báo cắp: {car}")

    def check(self, car):
        if not bool(car):
            print(f"⚠️  {car} là xe bị cắp!")
        else:
            info = self.cars.get(car.car_id)
            print(f"✅ {car} — Chủ: {info['owner']}")


# Test
registry = CarRegistry()

car1 = Car("Toyota", "Camry", 2023, "silver")
car2 = Car("Honda", "Civic", 2022, "black")
car3 = Car("BMW", "X5", 2024, "white")

registry.register(car1, "Vuong")
registry.register(car2, "Alice")
registry.register(car3, "Bob")

car1.accelerate(60)
car1.accelerate(40)
car1.brake(30)

registry.report_stolen(car2)

registry.check(car1)   # ✅
registry.check(car2)   # ⚠️ xe bị cắp
registry.check(car3)   # ✅

print(f"\nTổng xe đã tạo: {Car.total_cars}")
print(f"car1 == car1: {car1 == car1}")
print(f"car1 == car3: {car1 == car3}")
