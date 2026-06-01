"""
Section 15 & 16 — Special Methods, Inheritance
@staticmethod, @classmethod, super(), name mangling, @abstractmethod
"""

# ============================================================
# 83. METHOD vs FUNCTION
# ============================================================
# Function  = hàm độc lập, không thuộc class nào
# Method    = hàm THUỘC class, có self làm param đầu tiên

def standalone_function(x):     # function
    return x * 2

class MyClass:
    def instance_method(self):  # method — có self
        return "instance"

    @staticmethod
    def static_method():        # method — KHÔNG có self
        return "static"

    @classmethod
    def class_method(cls):      # method — có cls (class)
        return "class"


# ============================================================
# 84. @staticmethod — không cần self, không cần cls
# ============================================================
# JS: static myMethod() { }  ← giống nhau!

class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def is_even(n):
        return n % 2 == 0

    @staticmethod
    def celsius_to_fahrenheit(c):
        return c * 9/5 + 32

# Gọi qua class — không cần tạo object
print(MathUtils.add(3, 4))                    # 7
print(MathUtils.is_even(6))                   # True
print(MathUtils.celsius_to_fahrenheit(100))   # 212.0

# Gọi qua instance cũng được (nhưng kỳ)
m = MathUtils()
print(m.add(1, 2))   # 3

# Khi nào dùng @staticmethod?
# → Khi logic liên quan đến class nhưng KHÔNG cần access self hay cls
# → Utility/helper functions thuộc về class về mặt ý nghĩa


# ============================================================
# 85. @classmethod — nhận cls (class) thay vì self (instance)
# ============================================================
# JS: không có tương đương trực tiếp

class User:
    user_count = 0

    def __init__(self, name, email, role="user"):
        self.name  = name
        self.email = email
        self.role  = role
        User.user_count += 1

    # @classmethod hay dùng làm ALTERNATIVE CONSTRUCTOR
    # Tạo object theo cách khác nhau
    @classmethod
    def from_dict(cls, data: dict):
        # cls = User class → cls(...) = User(...)
        return cls(data["name"], data["email"], data.get("role", "user"))

    @classmethod
    def from_string(cls, user_str: str):
        # "Vuong:vuong@gmail.com:admin"
        name, email, role = user_str.split(":")
        return cls(name, email, role)

    @classmethod
    def get_user_count(cls):
        return cls.user_count

    def __str__(self):
        return f"{self.name} <{self.email}> [{self.role}]"


# Tạo user theo nhiều cách
u1 = User("Vuong", "vuong@gmail.com", "admin")
u2 = User.from_dict({"name": "Alice", "email": "alice@gmail.com"})
u3 = User.from_string("Bob:bob@gmail.com:moderator")

print(u1)   # Vuong <vuong@gmail.com> [admin]
print(u2)   # Alice <alice@gmail.com> [user]
print(u3)   # Bob <bob@gmail.com> [moderator]
print(User.get_user_count())   # 3

# staticmethod vs classmethod:
# @staticmethod → không biết class là gì
# @classmethod  → biết class (cls), có thể tạo instance, access class attrs


# ============================================================
# 86. PROJECT: PASSWORD CHECKER
# ============================================================
import re

class PasswordChecker:
    MIN_LENGTH   = 8
    SPECIAL_CHARS = "!@#$%^&*"

    def __init__(self, password):
        self.password = password
        self.errors   = []

    def check(self):
        self.errors = []
        self._check_length()
        self._check_uppercase()
        self._check_number()
        self._check_special()
        return len(self.errors) == 0

    def _check_length(self):
        if len(self.password) < self.MIN_LENGTH:
            self.errors.append(f"Ít nhất {self.MIN_LENGTH} ký tự")

    def _check_uppercase(self):
        if not any(c.isupper() for c in self.password):
            self.errors.append("Cần ít nhất 1 chữ hoa")

    def _check_number(self):
        if not any(c.isdigit() for c in self.password):
            self.errors.append("Cần ít nhất 1 số")

    def _check_special(self):
        if not any(c in self.SPECIAL_CHARS for c in self.password):
            self.errors.append(f"Cần ít nhất 1 ký tự đặc biệt {self.SPECIAL_CHARS}")

    @staticmethod
    def generate_strong():
        import secrets, string
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(chars) for _ in range(16))

    @classmethod
    def is_valid(cls, password):
        checker = cls(password)
        return checker.check()

for pwd in ["abc", "password123", "Password1!", "Str0ng!Pass"]:
    checker = PasswordChecker(pwd)
    valid = checker.check()
    status = "✅" if valid else "❌"
    print(f"{status} '{pwd}': {checker.errors if not valid else 'OK'}")

print(f"\nGenerated: {PasswordChecker.generate_strong()}")


# ============================================================
# 87. INHERITANCE — kế thừa
# ============================================================
# JS: class Dog extends Animal { }
# Python: class Dog(Animal):

class Animal:
    def __init__(self, name, species):
        self.name    = name
        self.species = species
        self.alive   = True

    def eat(self):
        print(f"{self.name} đang ăn")

    def sleep(self):
        print(f"{self.name} đang ngủ")

    def __str__(self):
        return f"{self.species}: {self.name}"


class Dog(Animal):              # Dog kế thừa Animal
    def __init__(self, name, breed):
        # 88. super() — gọi method của class cha
        super().__init__(name, species="Dog")   # JS: super(name, "Dog")
        self.breed = breed

    def bark(self):             # method riêng của Dog
        print(f"{self.name} sủa: Woof!")

    def eat(self):              # OVERRIDE method của cha
        print(f"{self.name} ăn kibble")
        super().eat()           # vẫn có thể gọi method cha nếu cần


class Cat(Animal):
    def __init__(self, name, indoor=True):
        super().__init__(name, species="Cat")
        self.indoor = indoor

    def purr(self):
        print(f"{self.name}: Purrr...")

    def eat(self):
        print(f"{self.name} ăn cá")


dog = Dog("Rex", "German Shepherd")
cat = Cat("Whiskers")

print(dog)              # Dog: Rex
dog.eat()               # ăn kibble + ăn (từ super)
dog.bark()              # Woof!
dog.sleep()             # kế thừa từ Animal

print(cat)              # Cat: Whiskers
cat.eat()               # ăn cá
cat.purr()              # Purrr...

# isinstance() — check kế thừa
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True — Dog là con của Animal
print(isinstance(cat, Dog))     # False


# ============================================================
# 89. NAME MANGLING — __ prefix
# ============================================================
# Không có trong JS
# __name (double underscore prefix) → Python đổi tên thành _ClassName__name
# Dùng để tránh bị override khi kế thừa

class BankAccount:
    def __init__(self, owner, balance):
        self.owner    = owner       # public
        self._balance = balance     # protected (convention — vẫn access được)
        self.__pin    = "1234"      # private (name mangling)

    def get_balance(self):
        return self._balance

    def verify_pin(self, pin):
        return pin == self.__pin    # access trong class OK

acc = BankAccount("Vuong", 1000)

print(acc.owner)         # "Vuong"   ✅ public
print(acc._balance)      # 1000      ⚠️  protected — có thể nhưng đừng
# print(acc.__pin)       # ❌ AttributeError

# Name mangling: __pin → _BankAccount__pin
print(acc._BankAccount__pin)   # "1234" — vẫn access được nhưng xấu xí
print(acc.verify_pin("1234"))  # True

# Tác dụng name mangling trong kế thừa:
class SavingsAccount(BankAccount):
    def hack(self):
        # self.__pin  → _SavingsAccount__pin (khác với _BankAccount__pin!)
        # Tránh vô tình override thuộc tính cha
        pass

# Naming convention Python:
# name      → public       — ai cũng dùng được
# _name     → protected    — internal use, tránh dùng ngoài class
# __name    → private      — name mangling, thực sự "ẩn"
# __name__  → dunder       — magic methods, Python reserved


# ============================================================
# 90. @abstractmethod — bắt buộc subclass phải implement
# ============================================================
# JS: không có (phải throw Error thủ công)
# Python: dùng ABC (Abstract Base Class)

from abc import ABC, abstractmethod

class Shape(ABC):           # ABC = Abstract Base Class
    def __init__(self, color="white"):
        self.color = color

    @abstractmethod         # bắt buộc subclass phải override
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

    def describe(self):     # method bình thường — không cần override
        return f"{self.__class__.__name__}: màu {self.color}, diện tích {self.area():.2f}"

# shape = Shape()  # ❌ TypeError — không tạo instance từ abstract class được!

class Circle(Shape):
    def __init__(self, radius, color="white"):
        super().__init__(color)
        self.radius = radius

    def area(self):          # phải implement
        import math
        return math.pi * self.radius ** 2

    def perimeter(self):     # phải implement
        import math
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width, height, color="blue"):
        super().__init__(color)
        self.width  = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

# class BadShape(Shape):   # ❌ nếu không implement area()/perimeter()
#     pass                 # TypeError khi tạo instance

c = Circle(5, "red")
r = Rectangle(4, 6)

print(c.describe())   # Circle: màu red, diện tích 78.54
print(r.describe())   # Rectangle: màu blue, diện tích 24.00
print(c.perimeter())  # 31.41...

shapes = [Circle(3), Rectangle(2, 5), Circle(7)]
for s in shapes:
    print(f"  area = {s.area():.2f}")


# ============================================================
# TÓM TẮT
# ============================================================
print("""
┌────────────────────┬────────────────────────────────────────────────┐
│ Khái niệm          │ Chi tiết                                       │
├────────────────────┼────────────────────────────────────────────────┤
│ @staticmethod      │ Không cần self/cls — utility function của class│
│ @classmethod       │ Nhận cls — alternative constructor, factory    │
│ Inheritance        │ class Child(Parent): — kế thừa method/attr    │
│ super()            │ Gọi method của class cha                       │
│ name               │ Public — ai cũng dùng                         │
│ _name              │ Protected — convention "đừng dùng ngoài class" │
│ __name             │ Private — name mangling _ClassName__name       │
│ @abstractmethod    │ Bắt buộc subclass phải implement               │
│ ABC                │ Abstract Base Class — không tạo instance được  │
├────────────────────┼────────────────────────────────────────────────┤
│ JS tương đương     │                                                │
│ static method()    │ = @staticmethod ✅ giống                       │
│ extends            │ = class Child(Parent) ✅ giống                 │
│ super()            │ = super() ✅ giống                             │
│ private fields #   │ ≈ __name (name mangling — khác cơ chế)        │
│ @abstractmethod    │ ❌ JS không có, phải throw Error thủ công     │
└────────────────────┴────────────────────────────────────────────────┘
""")
