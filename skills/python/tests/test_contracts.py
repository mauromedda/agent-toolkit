# ABOUTME: Tests for TypedDict contracts
# ABOUTME: Validates contract compliance and type safety
"""Tests for TypedDict contracts.

Note: TypedDict is primarily a static type checking tool.
These tests verify that the contracts work correctly at runtime.
"""

from __future__ import annotations

from src.contracts import (
    Address,
    APIResponse,
    ConfigDict,
    Customer,
    PaginatedResponse,
    RequiredConfig,
    TaskResult,
    UserProfile,
)


class TestUserProfile:
    """Tests for UserProfile contract."""

    def test_valid_user_profile(self) -> None:
        profile: UserProfile = {
            "user_id": 123,
            "email": "alice@example.com",
            "is_active": True,
        }
        assert profile["user_id"] == 123
        assert profile["email"] == "alice@example.com"
        assert profile["is_active"] is True

    def test_user_profile_with_optional_nickname(self) -> None:
        profile: UserProfile = {
            "user_id": 123,
            "email": "alice@example.com",
            "is_active": True,
            "nickname": "Ali",
        }
        assert profile.get("nickname") == "Ali"


class TestAddress:
    """Tests for Address contract."""

    def test_valid_address(self) -> None:
        addr: Address = {
            "street": "123 Main St",
            "city": "NYC",
            "country": "USA",
        }
        assert addr["city"] == "NYC"

    def test_address_with_postal_code(self) -> None:
        addr: Address = {
            "street": "123 Main St",
            "city": "NYC",
            "country": "USA",
            "postal_code": "10001",
        }
        assert addr["postal_code"] == "10001"


class TestCustomer:
    """Tests for Customer contract with nested Address."""

    def test_nested_customer(self) -> None:
        customer: Customer = {
            "name": "Alice",
            "email": "alice@example.com",
            "address": {"street": "123 Main", "city": "NYC", "country": "USA"},
        }
        assert customer["name"] == "Alice"
        assert customer["address"]["city"] == "NYC"


class TestAPIResponse:
    """Tests for APIResponse contract."""

    def test_success_response(self) -> None:
        response: APIResponse = {
            "status": "success",
            "data": {"user": "alice"},
        }
        assert response["status"] == "success"
        assert response["data"]["user"] == "alice"

    def test_response_with_meta(self) -> None:
        response: APIResponse = {
            "status": "success",
            "data": {},
            "meta": {"page": 1, "total": 100},
        }
        assert response["meta"]["page"] == 1

    def test_error_response(self) -> None:
        response: APIResponse = {
            "status": "error",
            "data": {},
            "error": "Something went wrong",
        }
        assert response["error"] == "Something went wrong"


class TestPaginatedResponse:
    """Tests for PaginatedResponse contract."""

    def test_paginated_response(self) -> None:
        paginated: PaginatedResponse = {
            "items": [{"id": 1}, {"id": 2}],
            "page": 1,
            "page_size": 10,
            "total_items": 100,
        }
        assert len(paginated["items"]) == 2
        assert paginated["page"] == 1
        assert paginated["total_items"] == 100

    def test_with_navigation_flags(self) -> None:
        paginated: PaginatedResponse = {
            "items": [],
            "page": 2,
            "page_size": 10,
            "total_items": 50,
            "has_next": True,
            "has_prev": True,
        }
        assert paginated["has_next"] is True
        assert paginated["has_prev"] is True


class TestConfigDict:
    """Tests for ConfigDict contract (total=False)."""

    def test_empty_config(self) -> None:
        config: ConfigDict = {}
        assert config.get("host") is None

    def test_partial_config(self) -> None:
        config: ConfigDict = {"host": "localhost"}
        assert config["host"] == "localhost"
        assert config.get("port", 8080) == 8080

    def test_full_config(self) -> None:
        config: ConfigDict = {
            "host": "localhost",
            "port": 8080,
            "debug": True,
            "timeout": 30.0,
            "retries": 3,
        }
        assert config["debug"] is True


class TestRequiredConfig:
    """Tests for RequiredConfig contract."""

    def test_required_fields_only(self) -> None:
        config: RequiredConfig = {
            "api_key": "secret",
            "base_url": "https://api.example.com",
        }
        assert config["api_key"] == "secret"

    def test_with_optional_fields(self) -> None:
        config: RequiredConfig = {
            "api_key": "secret",
            "base_url": "https://api.example.com",
            "timeout": 60,
            "max_retries": 5,
        }
        assert config["timeout"] == 60


class TestTaskResult:
    """Tests for TaskResult contract."""

    def test_pending_task(self) -> None:
        result: TaskResult = {
            "task_id": "abc123",
            "status": "pending",
        }
        assert result["status"] == "pending"

    def test_completed_task(self) -> None:
        result: TaskResult = {
            "task_id": "abc123",
            "status": "completed",
            "result": {"processed": 100},
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:01:00Z",
        }
        assert result["result"]["processed"] == 100

    def test_failed_task(self) -> None:
        result: TaskResult = {
            "task_id": "abc123",
            "status": "failed",
            "error": "Connection timeout",
        }
        assert result["error"] == "Connection timeout"
