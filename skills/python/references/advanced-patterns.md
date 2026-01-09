# ABOUTME: Advanced Python patterns for iteration, functools, collections
# ABOUTME: Extended reference for generators, context managers, functional programming

# Advanced Python Patterns

## Iteration Utilities (itertools)

```python
from itertools import chain, islice, groupby, product, combinations, permutations

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

# Combinations and permutations
for combo in combinations([1, 2, 3, 4], 2):
    print(combo)  # (1,2), (1,3), (1,4), (2,3), ...
```

## Generator Functions

```python
from collections.abc import Generator, Iterator

def fibonacci() -> Generator[int, None, None]:
    """Infinite Fibonacci sequence."""
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

## Context Managers

### Custom Context Manager

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
from contextlib import suppress, closing, ExitStack

# Suppress specific exceptions
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# Ensure close() is called
from urllib.request import urlopen
with closing(urlopen("https://example.com")) as page:
    content = page.read()

# Dynamic context manager stack
with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in filenames]
    # All files automatically closed
```

## functools Utilities

```python
from functools import partial, lru_cache, cached_property, wraps

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

# Decorator that preserves metadata
def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

## Collections Module

### defaultdict

```python
from collections import defaultdict

groups: defaultdict[str, list[str]] = defaultdict(list)
for item in items:
    groups[item.category].append(item.name)

counts: defaultdict[str, int] = defaultdict(int)
for word in words:
    counts[word] += 1
```

### Counter

```python
from collections import Counter

word_counts = Counter(words)
most_common = word_counts.most_common(10)

# Counter operations
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(c1 + c2)  # Counter({'a': 4, 'b': 3})
print(c1 - c2)  # Counter({'a': 2})
```

### namedtuple

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p.x, p.y)

# With defaults (Python 3.7+)
Point = namedtuple("Point", ["x", "y", "z"], defaults=[0])
p = Point(1, 2)  # z defaults to 0
```

### deque

```python
from collections import deque

# Efficient append/pop from both ends
d = deque(maxlen=5)  # Bounded length
d.append(1)
d.appendleft(0)
d.rotate(1)  # Rotate right
```

## Dataclasses

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
    _cache: dict = field(default_factory=dict, repr=False)  # Hidden
    MAX_SIZE: ClassVar[int] = 100  # Class variable
```

## Enumerations

```python
from enum import Enum, auto, IntEnum, StrEnum

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()

# String enum (Python 3.11+)
class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

# Integer enum
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# Iteration
for status in Status:
    print(status.name, status.value)
```

## String Formatting

```python
name = "Alice"
score = 95.678

# f-string formatting
print(f"Score: {score:.2f}")  # 95.68
print(f"{'centered':^20}")  # '      centered      '
print(f"{1000000:,}")  # 1,000,000

# Debug format (Python 3.8+)
x = 42
print(f"{x=}")  # x=42
print(f"{x=:>10}")  # x=        42
```

## TypedDict for Data Contracts

```python
from typing import TypedDict, NotRequired

class UserProfile(TypedDict):
    """Data contract for external API."""
    user_id: int
    email: str
    is_active: bool
    nickname: NotRequired[str]  # Optional key

def process_user(profile: UserProfile) -> None:
    print(f"Processing user {profile['user_id']}")
```
