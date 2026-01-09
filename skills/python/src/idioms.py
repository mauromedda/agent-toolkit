# ABOUTME: Reference implementations of idiomatic Python patterns
# ABOUTME: Each function demonstrates a specific Pythonic technique
"""Idiomatic Python patterns and techniques.

This module provides reference implementations demonstrating
best practices for common Python operations.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Generator, Iterable, Iterator, Sequence
from contextlib import contextmanager
from functools import lru_cache, partial
from itertools import chain, groupby, islice
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# =============================================================================
# Iteration Patterns
# =============================================================================


def enumerate_with_start(items: Sequence[T], start: int = 1) -> list[tuple[int, T]]:
    """Demonstrate enumerate with custom start index.

    Example:
        >>> enumerate_with_start(["a", "b", "c"])
        [(1, 'a'), (2, 'b'), (3, 'c')]
    """
    return list(enumerate(items, start=start))


def parallel_iteration(names: Sequence[str], scores: Sequence[int]) -> list[tuple[str, int]]:
    """Demonstrate zip for parallel iteration.

    Example:
        >>> parallel_iteration(["Alice", "Bob"], [95, 87])
        [('Alice', 95), ('Bob', 87)]
    """
    return list(zip(names, scores, strict=True))


def chain_iterables(*iterables: Iterable[T]) -> list[T]:
    """Demonstrate chaining multiple iterables.

    Example:
        >>> chain_iterables([1, 2], [3, 4], [5])
        [1, 2, 3, 4, 5]
    """
    return list(chain(*iterables))


def take_first_n(iterable: Iterable[T], n: int) -> list[T]:
    """Take first n items from any iterable.

    Example:
        >>> take_first_n(range(100), 5)
        [0, 1, 2, 3, 4]
    """
    return list(islice(iterable, n))


def group_by_key(items: Iterable[T], key_func: Callable[[T], K]) -> dict[K, list[T]]:
    """Group items by a key function.

    Example:
        >>> group_by_key(["apple", "banana", "apricot"], lambda x: x[0])
        {'a': ['apple', 'apricot'], 'b': ['banana']}
    """
    result: dict[K, list[T]] = {}
    sorted_items = sorted(items, key=key_func)
    for key, group in groupby(sorted_items, key=key_func):
        result[key] = list(group)
    return result


# =============================================================================
# Dictionary Patterns
# =============================================================================


def safe_dict_access(d: dict[str, V], key: str, default: V) -> V:
    """Demonstrate safe dictionary access with .get().

    Example:
        >>> safe_dict_access({"a": 1}, "b", 0)
        0
        >>> safe_dict_access({"a": 1}, "a", 0)
        1
    """
    return d.get(key, default)


def accumulate_to_dict(items: Iterable[tuple[K, V]]) -> dict[K, list[V]]:
    """Accumulate values into lists using defaultdict.

    Example:
        >>> accumulate_to_dict([("a", 1), ("b", 2), ("a", 3)])
        {'a': [1, 3], 'b': [2]}
    """
    result: defaultdict[K, list[V]] = defaultdict(list)
    for key, value in items:
        result[key].append(value)
    return dict(result)


def count_frequencies(items: Iterable[T]) -> dict[T, int]:
    """Count item frequencies using Counter.

    Example:
        >>> count_frequencies(["a", "b", "a", "c", "a"])
        {'a': 3, 'b': 1, 'c': 1}
    """
    return dict(Counter(items))


def merge_dicts(*dicts: dict[K, V]) -> dict[K, V]:
    """Merge multiple dicts (later values override).

    Example:
        >>> merge_dicts({"a": 1}, {"b": 2}, {"a": 3})
        {'a': 3, 'b': 2}
    """
    result: dict[K, V] = {}
    for d in dicts:
        result |= d
    return result


def invert_dict(d: dict[K, V]) -> dict[V, K]:
    """Invert a dictionary (swap keys and values).

    Example:
        >>> invert_dict({"a": 1, "b": 2})
        {1: 'a', 2: 'b'}
    """
    return {v: k for k, v in d.items()}


# =============================================================================
# Comprehension Patterns
# =============================================================================


def filter_and_transform(
    items: Sequence[int], predicate: Callable[[int], bool], transform: Callable[[int], int]
) -> list[int]:
    """Filter then transform using list comprehension.

    Example:
        >>> filter_and_transform([1, 2, 3, 4, 5], lambda x: x % 2 == 0, lambda x: x ** 2)
        [4, 16]
    """
    return [transform(x) for x in items if predicate(x)]


def flatten_nested(nested: Sequence[Sequence[T]]) -> list[T]:
    """Flatten a nested sequence using comprehension.

    Example:
        >>> flatten_nested([[1, 2], [3, 4], [5]])
        [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested for item in sublist]


def unique_values(items: Iterable[T]) -> set[T]:
    """Get unique values using set comprehension.

    Example:
        >>> sorted(unique_values([1, 2, 2, 3, 3, 3]))
        [1, 2, 3]
    """
    return set(items)


# =============================================================================
# Generator Patterns
# =============================================================================


def fibonacci() -> Generator[int, None, None]:
    """Infinite Fibonacci sequence generator.

    Example:
        >>> list(islice(fibonacci(), 8))
        [0, 1, 1, 2, 3, 5, 8, 13]
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def chunked(items: Sequence[T], size: int) -> Generator[Sequence[T], None, None]:
    """Yield successive chunks of specified size.

    Example:
        >>> list(chunked([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(items), size):
        yield items[i : i + size]


def lazy_read_lines(filepath: str) -> Iterator[str]:
    """Memory-efficient line reading.

    Example:
        >>> # Would work with real file
        >>> # for line in lazy_read_lines("data.txt"): process(line)
    """
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


# =============================================================================
# Functional Patterns
# =============================================================================


@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Demonstrate memoization with lru_cache.

    Example:
        >>> expensive_computation.cache_clear()  # Reset cache for test
        >>> expensive_computation(10)
        55
        >>> expensive_computation.cache_info().misses
        1
    """
    return sum(range(n + 1))


def create_multiplier(factor: int) -> Callable[[int], int]:
    """Demonstrate partial application.

    Example:
        >>> double = create_multiplier(2)
        >>> double(5)
        10
    """

    def multiply(x: int, factor: int) -> int:
        return x * factor

    return partial(multiply, factor=factor)


# =============================================================================
# Context Manager Patterns
# =============================================================================


@contextmanager
def timer(label: str) -> Generator[None, None, None]:
    """Time a code block.

    Example:
        >>> with timer("test"):  # doctest: +SKIP
        ...     pass
        test: 0.000s
    """
    import time

    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")


@contextmanager
def suppress_exception(*exceptions: type[BaseException]) -> Generator[None, None, None]:
    """Suppress specified exceptions.

    Note: In production, use contextlib.suppress() instead.
    This demonstrates the pattern for educational purposes.

    Example:
        >>> with suppress_exception(ValueError):
        ...     raise ValueError("ignored")
        >>> print("continued")
        continued
    """
    try:
        yield
    except exceptions:
        return  # Explicitly return instead of pass


# =============================================================================
# Unpacking Patterns
# =============================================================================


def head_tail(items: Sequence[T]) -> tuple[T, Sequence[T]]:
    """Split sequence into head and tail.

    Example:
        >>> head_tail([1, 2, 3, 4, 5])
        (1, [2, 3, 4, 5])
    """
    first, *rest = items
    return first, rest


def first_last(items: Sequence[T]) -> tuple[T, T]:
    """Extract first and last elements.

    Example:
        >>> first_last([1, 2, 3, 4, 5])
        (1, 5)
    """
    first, *_, last = items
    return first, last


def swap_values(a: T, b: T) -> tuple[T, T]:
    """Swap two values idiomatically.

    Example:
        >>> swap_values(1, 2)
        (2, 1)
    """
    return b, a
