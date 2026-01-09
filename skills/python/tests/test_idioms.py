# ABOUTME: Tests for idiomatic Python patterns
# ABOUTME: Validates iteration, dict, comprehension, and generator patterns
"""Tests for idiomatic Python patterns."""

from __future__ import annotations

from itertools import islice

import pytest

from src.idioms import (
    accumulate_to_dict,
    chain_iterables,
    chunked,
    count_frequencies,
    create_multiplier,
    enumerate_with_start,
    expensive_computation,
    fibonacci,
    filter_and_transform,
    first_last,
    flatten_nested,
    group_by_key,
    head_tail,
    invert_dict,
    merge_dicts,
    parallel_iteration,
    safe_dict_access,
    suppress_exception,
    swap_values,
    take_first_n,
    unique_values,
)


class TestIterationPatterns:
    """Tests for iteration patterns."""

    def test_enumerate_with_start(self) -> None:
        result = enumerate_with_start(["a", "b", "c"])
        assert result == [(1, "a"), (2, "b"), (3, "c")]

    def test_enumerate_with_custom_start(self) -> None:
        result = enumerate_with_start(["x", "y"], start=10)
        assert result == [(10, "x"), (11, "y")]

    def test_parallel_iteration(self) -> None:
        result = parallel_iteration(["Alice", "Bob"], [95, 87])
        assert result == [("Alice", 95), ("Bob", 87)]

    def test_parallel_iteration_strict_mismatch(self) -> None:
        with pytest.raises(ValueError):
            parallel_iteration(["Alice", "Bob", "Charlie"], [95, 87])

    def test_chain_iterables(self) -> None:
        result = chain_iterables([1, 2], [3, 4], [5])
        assert result == [1, 2, 3, 4, 5]

    def test_take_first_n(self) -> None:
        result = take_first_n(range(100), 5)
        assert result == [0, 1, 2, 3, 4]

    def test_group_by_key(self) -> None:
        result = group_by_key(["apple", "banana", "apricot"], lambda x: x[0])
        assert result == {"a": ["apple", "apricot"], "b": ["banana"]}


class TestDictionaryPatterns:
    """Tests for dictionary patterns."""

    def test_safe_dict_access_existing_key(self) -> None:
        result = safe_dict_access({"a": 1}, "a", 0)
        assert result == 1

    def test_safe_dict_access_missing_key(self) -> None:
        result = safe_dict_access({"a": 1}, "b", 0)
        assert result == 0

    def test_accumulate_to_dict(self) -> None:
        result = accumulate_to_dict([("a", 1), ("b", 2), ("a", 3)])
        assert result == {"a": [1, 3], "b": [2]}

    def test_count_frequencies(self) -> None:
        result = count_frequencies(["a", "b", "a", "c", "a"])
        assert result == {"a": 3, "b": 1, "c": 1}

    def test_merge_dicts(self) -> None:
        result = merge_dicts({"a": 1}, {"b": 2}, {"a": 3})
        assert result == {"a": 3, "b": 2}

    def test_invert_dict(self) -> None:
        result = invert_dict({"a": 1, "b": 2})
        assert result == {1: "a", 2: "b"}


class TestComprehensionPatterns:
    """Tests for comprehension patterns."""

    def test_filter_and_transform(self) -> None:
        result = filter_and_transform([1, 2, 3, 4, 5], lambda x: x % 2 == 0, lambda x: x**2)
        assert result == [4, 16]

    def test_flatten_nested(self) -> None:
        result = flatten_nested([[1, 2], [3, 4], [5]])
        assert result == [1, 2, 3, 4, 5]

    def test_unique_values(self) -> None:
        result = unique_values([1, 2, 2, 3, 3, 3])
        assert result == {1, 2, 3}


class TestGeneratorPatterns:
    """Tests for generator patterns."""

    def test_fibonacci(self) -> None:
        result = list(islice(fibonacci(), 8))
        assert result == [0, 1, 1, 2, 3, 5, 8, 13]

    def test_chunked(self) -> None:
        result = list(chunked([1, 2, 3, 4, 5], 2))
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunked_exact_division(self) -> None:
        result = list(chunked([1, 2, 3, 4], 2))
        assert result == [[1, 2], [3, 4]]


class TestFunctionalPatterns:
    """Tests for functional patterns."""

    def test_expensive_computation(self) -> None:
        result = expensive_computation(10)
        assert result == 55

    def test_expensive_computation_cached(self) -> None:
        expensive_computation.cache_clear()
        expensive_computation(10)
        expensive_computation(10)
        info = expensive_computation.cache_info()
        assert info.hits == 1
        assert info.misses == 1

    def test_create_multiplier(self) -> None:
        double = create_multiplier(2)
        triple = create_multiplier(3)
        assert double(5) == 10
        assert triple(5) == 15


class TestContextManagerPatterns:
    """Tests for context manager patterns."""

    def test_suppress_exception(self) -> None:
        with suppress_exception(ValueError):
            raise ValueError("ignored")
        # Should reach here without error

    def test_suppress_exception_does_not_catch_other(self) -> None:
        with pytest.raises(TypeError), suppress_exception(ValueError):
            raise TypeError("not ignored")


class TestUnpackingPatterns:
    """Tests for unpacking patterns."""

    def test_head_tail(self) -> None:
        head, tail = head_tail([1, 2, 3, 4, 5])
        assert head == 1
        assert tail == [2, 3, 4, 5]

    def test_first_last(self) -> None:
        first, last = first_last([1, 2, 3, 4, 5])
        assert first == 1
        assert last == 5

    def test_swap_values(self) -> None:
        a, b = swap_values(1, 2)
        assert a == 2
        assert b == 1
