---
name: python
description: >-
  Guide for writing clean, efficient, idiomatic Python 3.11+ code. Enforces type hints,
  Pydantic v2 for APIs, comprehensions over loops, EAFP error handling. Triggers on
  "python", "pythonic", ".py file", "write python", "python script", "python function",
  "python class", "pydantic", "fastapi", "pytest", "type hint", "typing", "dataclass",
  "async def", "asyncio", "aiohttp", "comprehension", "generator", "decorator",
  "context manager", "with statement", "exception handling", "try except", "raise",
  "logging python", "argparse", "click", "typer", "__init__", "__main__", "import",
  "from import", "python module", "python package", "requirements.txt", "pyproject.toml",
  "ruff", "mypy", "black", "isort", "python testing", "fixture", "parametrize".
  PROACTIVE: MUST invoke when writing ANY .py file.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# ABOUTME: Comprehensive skill for idiomatic Python best practices
# ABOUTME: Covers loops, dicts, comprehensions, typing, Pydantic v2, error handling

# Idiomatic Python Best Practices

A comprehensive reference for writing clean, efficient, and Pythonic code.
Target: Python 3.11+ with modern tooling (uv, Pydantic v2, type hints).

---

## Quick Reference

| Pattern | Pythonic Way | Avoid |
|---------|--------------|-------|
| Iteration | `for item in items:` | `for i in range(len(items)):` |
| Index + Value | `for i, v in enumerate(seq):` | Manual counter |
| Dict Access | `d.get("key", default)` | `if "key" in d: d["key"]` |
| Dict Iteration | `for k, v in d.items():` | `for k in d: v = d[k]` |
| Swap Variables | `a, b = b, a` | `temp = a; a = b; b = temp` |
| Build Strings | `"".join(parts)` | `s += part` in loop |
| Membership | `x in set_or_dict` | `x in list` (for large) |
| File I/O | `with open(...) as f:` | Manual `f.close()` |
| Truthiness | `if items:` | `if len(items) > 0:` |
| None Check | `if x is None:` | `if x == None:` |

---

## 🔄 RESUMED SESSION CHECKPOINT

**When a session is resumed from context compaction, verify Python coding state:**

```
┌─────────────────────────────────────────────────────────────┐
│  SESSION RESUMED - PYTHON SKILL VERIFICATION                │
│                                                             │
│  Before continuing Python implementation:                   │
│                                                             │
│  1. Was I in the middle of writing Python code?             │
│     → Check summary for "implementing", "writing", "adding" │
│                                                             │
│  2. Did I follow all Python skill guidelines?               │
│     → Type hints on all functions                           │
│     → Pydantic v2 for validation                            │
│     → ABOUTME headers on new files                          │
│                                                             │
│  3. Check code quality before continuing:                   │
│     → Run: ruff check <file>.py                             │
│     → Run: mypy <file>.py                                   │
│                                                             │
│  If implementation was in progress:                         │
│  → Review the partial code for completeness                 │
│  → Ensure all functions have type hints                     │
│  → Verify Pydantic models use v2 patterns                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Loops and Iteration

### Direct Iteration (Preferred)

```python
# DO: Iterate directly over collections
names = ["Alice", "Bob", "Charlie"]
for name in names:
    process(name)

# DON'T: C-style indexing
for i in range(len(names)):
    process(names[i])
```

### enumerate() for Index + Value

```python
# DO: Use enumerate when you need the index
for index, item in enumerate(items):
    print(f"{index}: {item}")

# With custom start index
for num, item in enumerate(items, start=1):
    print(f"Item {num}: {item}")
```

### zip() for Parallel Iteration

```python
# DO: Iterate multiple sequences together
names = ["Alice", "Bob"]
scores = [95, 87]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Use strict=True (Python 3.10+) to catch length mismatches
for name, score in zip(names, scores, strict=True):
    process(name, score)
```

### reversed() and sorted()

```python
# DO: Use built-in functions
for item in reversed(items):
    process(item)

for item in sorted(items, key=lambda x: x.name):
    process(item)

# DON'T: Create intermediate lists
for item in items[::-1]:  # Creates a copy
    process(item)
```

### Iteration Utilities (itertools)

```python
from itertools import chain, islice, groupby, product

# Chain multiple iterables
for item in chain(list1, list2, list3):
    process(item)

# Take first N items
for item in islice(infinite_generator(), 10):
    process(item)

# Group consecutive items
for key, group in groupby(sorted(items, key=keyfunc), key=keyfunc):
    process_group(key, list(group))

# Cartesian product
for x, y in product(range(3), range(3)):
    print(f"({x}, {y})")
```

---

## 2. Dictionaries

### Safe Access with .get()

```python
# DO: Use .get() with default
config = {"host": "localhost"}
port = config.get("port", 8080)  # Returns 8080 if missing

# DON'T: Check then access
if "port" in config:
    port = config["port"]
else:
    port = 8080
```

### .setdefault() for Initialize-If-Missing

```python
# DO: setdefault for accumulating
groups: dict[str, list[str]] = {}
for item in items:
    groups.setdefault(item.category, []).append(item.name)

# DON'T: Manual check
if item.category not in groups:
    groups[item.category] = []
groups[item.category].append(item.name)
```

### defaultdict for Auto-Initialization

```python
from collections import defaultdict

# Auto-initialize with empty list
groups: defaultdict[str, list[str]] = defaultdict(list)
for item in items:
    groups[item.category].append(item.name)

# Auto-initialize with zero
counts: defaultdict[str, int] = defaultdict(int)
for word in words:
    counts[word] += 1
```

### Counter for Frequency

```python
from collections import Counter

word_counts = Counter(words)
most_common = word_counts.most_common(10)
```

### Dict Comprehension

```python
# Create dict from transformation
squares = {n: n**2 for n in range(10)}

# Filter dict
active_users = {uid: user for uid, user in users.items() if user.is_active}

# Invert dict
name_to_id = {name: uid for uid, name in id_to_name.items()}
```

### Merge Dicts (Python 3.9+)

```python
# DO: Use | operator
merged = defaults | overrides

# Update in place
config |= new_settings

# DON'T: Use .update() when you want a new dict
```

---

## 3. Comprehensions and Generators

### List Comprehension

```python
# DO: Concise transformations
squared = [x**2 for x in numbers]
evens = [x for x in numbers if x % 2 == 0]
pairs = [(x, y) for x in xs for y in ys]

# DON'T: Use for simple iteration without result
# Comprehensions should CREATE data, not cause side effects
[print(x) for x in items]  # Bad: side effect only
```

### Generator Expression (Memory Efficient)

```python
# DO: Use parentheses for generators
total = sum(x**2 for x in range(1_000_000))  # Memory efficient
any_match = any(item.is_valid for item in items)
all_valid = all(item.is_valid for item in items)

# DON'T: Create full list just to iterate
total = sum([x**2 for x in range(1_000_000)])  # Wastes memory
```

### Generator Functions

```python
from collections.abc import Generator, Iterator

def fibonacci() -> Generator[int, None, None]:
    """Infinite Fibonacci sequence generator."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def read_large_file(path: str) -> Iterator[str]:
    """Memory-efficient file reading."""
    with open(path) as f:
        for line in f:
            yield line.strip()
```

### Set Comprehension

```python
# Deduplicate while transforming
unique_domains = {email.split("@")[1].lower() for email in emails}
```

---

## 4. Unpacking

### Basic Unpacking

```python
# Tuple/list unpacking
x, y, z = coordinates
first, second, *rest = items
first, *middle, last = items

# Swap variables
a, b = b, a

# Ignore values with _
_, important, _ = get_triple()
```

### Extended Unpacking

```python
# Collect remaining items
head, *tail = [1, 2, 3, 4, 5]  # head=1, tail=[2,3,4,5]
*init, last = [1, 2, 3, 4, 5]  # init=[1,2,3,4], last=5

# In function returns
def min_max(items):
    return min(items), max(items)

lo, hi = min_max(numbers)
```

### Dict Unpacking

```python
# Merge dicts with **
combined = {**defaults, **overrides, "extra": "value"}

# Pass dict as keyword arguments
config = {"host": "localhost", "port": 8080}
connect(**config)  # Same as connect(host="localhost", port=8080)
```

---

## 5. Context Managers

### File Handling

```python
# DO: Always use with statement
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Multiple files
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    outfile.write(infile.read().upper())

# DON'T: Manual open/close
f = open("data.txt")
try:
    content = f.read()
finally:
    f.close()
```

### Custom Context Managers

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label: str):
    """Time a block of code."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")

with timer("Data processing"):
    process_data()
```

### contextlib Utilities

```python
from contextlib import suppress, closing

# Suppress specific exceptions
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Ensure close() is called
from urllib.request import urlopen
with closing(urlopen("https://example.com")) as page:
    content = page.read()
```

---

## 6. Type Hints (Python 3.11+)

### Basic Type Hints

```python
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

### Optional and Union

```python
from typing import Optional

# Optional[X] is same as X | None
def find_user(user_id: int) -> Optional[User]:
    return db.get(user_id)

# Union types with |
def process(value: int | str | None) -> str:
    if value is None:
        return "none"
    return str(value)
```

### Generic Collections

```python
from collections.abc import Sequence, Mapping, Iterable, Callable

def process_items(items: Sequence[str]) -> list[str]:
    return [item.upper() for item in items]

def apply_func(data: Iterable[int], func: Callable[[int], int]) -> list[int]:
    return [func(x) for x in data]
```

### TypeVar for Generics

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None
```

---

## 7. TypedDict for Data Contracts

Use TypedDict for dictionary shapes (external data, JSON responses).

```python
from typing import TypedDict, NotRequired, Required

class UserProfile(TypedDict):
    """Data contract for user profile from external API."""
    user_id: int
    email: str
    is_active: bool
    nickname: NotRequired[str]  # Optional key

class PartialUser(TypedDict, total=False):
    """All keys optional."""
    user_id: int
    email: str

def process_user(profile: UserProfile) -> None:
    print(f"Processing user {profile['user_id']}")
    # Type checker knows profile["email"] is str
```

### Nested TypedDict

```python
class Address(TypedDict):
    street: str
    city: str
    country: str

class Customer(TypedDict):
    name: str
    address: Address
    tags: list[str]
```

---

## 8. Pydantic v2 for API Models

Use Pydantic for validation, serialization, and settings.

### Basic Model

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class User(BaseModel):
    """User model with validation."""
    id: int
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

# Parse from dict
user = User.model_validate({"id": 1, "email": "test@example.com", "name": "Alice"})

# Serialize
print(user.model_dump())  # To dict
print(user.model_dump_json())  # To JSON string
```

### Field Validation

```python
from pydantic import BaseModel, Field, field_validator
from typing import Annotated

class Product(BaseModel):
    name: str
    price: Annotated[float, Field(gt=0, description="Price in USD")]
    quantity: Annotated[int, Field(ge=0, le=1000)]

    @field_validator("name")
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        return v.strip().title()
```

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

### Model Configuration

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,  # No type coercion
        frozen=True,  # Immutable
        extra="forbid",  # No extra fields
        str_strip_whitespace=True,
    )

    name: str
    value: int
```

### Enums with Pydantic

```python
from enum import Enum
from pydantic import BaseModel, ConfigDict

class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    status: Status = Status.PENDING
```

### Nested Models

```python
from pydantic import BaseModel
from typing import Optional

class Address(BaseModel):
    street: str
    city: str
    country: str = "USA"

class Company(BaseModel):
    name: str
    address: Address
    employees: list[str] = []

# Nested validation works automatically
company = Company.model_validate({
    "name": "Acme",
    "address": {"street": "123 Main", "city": "NYC"}
})
```

---

## 9. Dataclasses

Use dataclasses for simple data containers without validation needs.

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

@dataclass(frozen=True)  # Immutable
class ImmutablePoint:
    x: float
    y: float

@dataclass
class Config:
    name: str
    values: list[int] = field(default_factory=list)  # Mutable default
    _cache: dict = field(default_factory=dict, repr=False)  # Hidden from repr
    MAX_SIZE: ClassVar[int] = 100  # Class variable, not instance
```

### dataclass vs Pydantic

| Feature | dataclass | Pydantic |
|---------|-----------|----------|
| Validation | No | Yes |
| Serialization | Manual | Built-in |
| Performance | Faster | Slower (validates) |
| Use Case | Internal data | API/External data |

---

## 10. Enumerations

```python
from enum import Enum, auto, IntEnum, StrEnum

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

# String enum (Python 3.11+)
class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

# Integer enum for interop
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# Usage
task_status = Status.RUNNING
if task_status == Status.RUNNING:
    print("Task in progress")

# Iteration
for status in Status:
    print(status.name, status.value)
```

---

## 11. Error Handling

### Catch Specific Exceptions

```python
# DO: Catch specific exceptions
try:
    value = int(user_input)
except ValueError:
    print("Invalid number format")
except TypeError:
    print("Wrong type provided")

# DON'T: Catch bare Exception (hides bugs)
try:
    value = int(user_input)
except:  # Catches everything including KeyboardInterrupt
    pass
```

### EAFP vs LBYL

```python
# EAFP (Easier to Ask Forgiveness than Permission) - Pythonic
try:
    value = mapping[key]
except KeyError:
    value = default

# LBYL (Look Before You Leap) - Less Pythonic for dict access
if key in mapping:
    value = mapping[key]
else:
    value = default

# But LBYL is fine when check is cheap and exception is expensive
if user.has_permission("admin"):
    perform_admin_action()
```

### Context-Specific Exceptions

```python
class ValidationError(Exception):
    """Raised when data validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

def validate_email(email: str) -> str:
    if "@" not in email:
        raise ValidationError("email", "Must contain @")
    return email.lower()
```

### Exception Chaining

```python
try:
    process_data()
except ValueError as e:
    raise RuntimeError("Data processing failed") from e
```

---

## 12. String Handling

### f-strings (Formatted String Literals)

```python
name = "Alice"
score = 95.678

# Basic interpolation
print(f"Hello, {name}!")

# Expressions
print(f"Score: {score:.2f}")  # 95.68
print(f"{'centered':^20}")  # '      centered      '
print(f"{1000000:,}")  # 1,000,000

# Debug format (Python 3.8+)
x = 42
print(f"{x=}")  # x=42
print(f"{x=:>10}")  # x=        42
```

### String Building

```python
# DO: Use join for multiple strings
parts = ["Hello", "World", "!"]
result = " ".join(parts)

# DON'T: Concatenate in loop
result = ""
for part in parts:
    result += part + " "  # Creates new string each time
```

### Multiline Strings

```python
# Use triple quotes
query = """
    SELECT *
    FROM users
    WHERE active = true
"""

# Or parentheses for implicit concatenation
message = (
    "This is a very long message that "
    "spans multiple lines for readability"
)
```

---

## 13. Functional Patterns

### map, filter, reduce

```python
# Prefer comprehensions, but map/filter are valid
numbers = [1, 2, 3, 4, 5]

# Comprehension (preferred)
doubled = [x * 2 for x in numbers]
evens = [x for x in numbers if x % 2 == 0]

# map/filter (useful with existing functions)
from functools import reduce

doubled = list(map(lambda x: x * 2, numbers))
evens = list(filter(lambda x: x % 2 == 0, numbers))
total = reduce(lambda a, b: a + b, numbers, 0)

# Built-in sum/any/all preferred
total = sum(numbers)
any_even = any(x % 2 == 0 for x in numbers)
all_positive = all(x > 0 for x in numbers)
```

### functools Utilities

```python
from functools import partial, lru_cache, cached_property

# Partial application
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)

# Memoization
@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    return sum(range(n))

# Cached property
class DataProcessor:
    @cached_property
    def processed_data(self):
        return self._load_and_process()
```

---

## 14. Best Practices Summary

### DO

- Use meaningful variable names
- Prefer composition over inheritance
- Keep functions small and focused
- Use type hints consistently
- Write docstrings for public APIs
- Use `pathlib.Path` for file paths
- Use `logging` instead of print for production

### DON'T

- Use mutable default arguments: `def f(items=[]):`
- Modify lists while iterating over them
- Use `from module import *`
- Catch bare `except:` or `except Exception:`
- Use `eval()` or `exec()` with untrusted input
- Use single-letter variable names (except `i`, `j`, `k` for indices, `x`, `y` for coordinates)

---

## References

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Real Python - Idiomatic Python](https://realpython.com/learning-paths/writing-idiomatic-python/)
- [Effective Python by Brett Slatkin](https://effectivepython.com/)
