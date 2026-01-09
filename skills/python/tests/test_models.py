# ABOUTME: Tests for Pydantic v2 models
# ABOUTME: Validates model creation, validation, and serialization
"""Tests for Pydantic models."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import (
    Address,
    DateRange,
    ImmutableConfig,
    Order,
    OrderItem,
    Product,
    Severity,
    Status,
    Task,
    User,
)


class TestStatus:
    """Tests for Status enum."""

    def test_status_values(self) -> None:
        assert Status.PENDING.value == "pending"
        assert Status.RUNNING.value == "running"
        assert Status.COMPLETED.value == "completed"

    def test_status_from_string(self) -> None:
        assert Status("pending") == Status.PENDING


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self) -> None:
        assert Severity.LOW.value == "low"
        assert Severity.CRITICAL.value == "critical"


class TestAddress:
    """Tests for Address model."""

    def test_valid_address(self) -> None:
        addr = Address(street="123 Main St", city="NYC", country="USA")
        assert addr.street == "123 Main St"
        assert addr.city == "NYC"
        assert addr.country == "USA"
        assert addr.postal_code is None

    def test_address_with_postal_code(self) -> None:
        addr = Address(street="123 Main St", city="NYC", country="USA", postal_code="10001")
        assert addr.postal_code == "10001"

    def test_invalid_postal_code(self) -> None:
        with pytest.raises(ValidationError):
            Address(
                street="123 Main St",
                city="NYC",
                country="USA",
                postal_code="invalid!!",
            )

    def test_empty_street_fails(self) -> None:
        with pytest.raises(ValidationError):
            Address(street="", city="NYC", country="USA")


class TestUser:
    """Tests for User model."""

    def test_valid_user(self) -> None:
        user = User(id=1, email="alice@example.com", name="alice smith")
        assert user.id == 1
        assert user.email == "alice@example.com"
        assert user.name == "Alice Smith"  # Title cased
        assert user.is_active is True

    def test_user_display_name(self) -> None:
        user = User(id=1, email="test@test.com", name="john doe")
        assert user.display_name == "John Doe"

    def test_invalid_email(self) -> None:
        with pytest.raises(ValidationError):
            User(id=1, email="not-an-email", name="Test")

    def test_negative_id_fails(self) -> None:
        with pytest.raises(ValidationError):
            User(id=-1, email="test@test.com", name="Test")

    def test_user_serialization(self) -> None:
        user = User(id=1, email="test@example.com", name="Test User")
        data = user.model_dump()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"


class TestProduct:
    """Tests for Product model."""

    def test_valid_product(self) -> None:
        product = Product(name="Widget", price=19.99, quantity=100)
        assert product.name == "Widget"
        assert product.price == 19.99
        assert product.quantity == 100

    def test_product_total_value(self) -> None:
        product = Product(name="Widget", price=10.00, quantity=5)
        assert product.total_value == 50.00

    def test_zero_price_fails(self) -> None:
        with pytest.raises(ValidationError):
            Product(name="Widget", price=0, quantity=100)

    def test_negative_quantity_fails(self) -> None:
        with pytest.raises(ValidationError):
            Product(name="Widget", price=10.00, quantity=-1)

    def test_valid_sku(self) -> None:
        product = Product(name="Widget", price=10.00, quantity=1, sku="ABC-1234")
        assert product.sku == "ABC-1234"

    def test_invalid_sku_fails(self) -> None:
        with pytest.raises(ValidationError):
            Product(name="Widget", price=10.00, quantity=1, sku="invalid")


class TestTask:
    """Tests for Task model."""

    def test_default_status(self) -> None:
        task = Task(name="Test task")
        assert task.status == "pending"  # use_enum_values=True

    def test_task_is_complete_false(self) -> None:
        task = Task(name="Test", status=Status.RUNNING)
        assert task.is_complete is False

    def test_task_is_complete_true(self) -> None:
        task = Task(name="Test", status=Status.COMPLETED)
        assert task.is_complete is True

    def test_task_priority_bounds(self) -> None:
        task = Task(name="Test", priority=10)
        assert task.priority == 10

        with pytest.raises(ValidationError):
            Task(name="Test", priority=11)


class TestOrderItem:
    """Tests for OrderItem model."""

    def test_valid_order_item(self) -> None:
        item = OrderItem(name="Widget", quantity=2, unit_price=9.99)
        assert item.line_total == 19.98

    def test_zero_quantity_fails(self) -> None:
        with pytest.raises(ValidationError):
            OrderItem(name="Widget", quantity=0, unit_price=9.99)


class TestOrder:
    """Tests for Order model."""

    def test_valid_order(self) -> None:
        order = Order(
            order_id="ORD-001",
            customer_email="test@example.com",
            items=[OrderItem(name="Widget", quantity=2, unit_price=10.00)],
        )
        assert order.subtotal == 20.00
        assert order.total == 20.00

    def test_order_with_discount(self) -> None:
        order = Order(
            order_id="ORD-002",
            customer_email="test@example.com",
            items=[OrderItem(name="Widget", quantity=1, unit_price=100.00)],
            discount_percent=10,
        )
        assert order.subtotal == 100.00
        assert order.total == 90.00

    def test_empty_items_fails(self) -> None:
        with pytest.raises(ValidationError):
            Order(
                order_id="ORD-003",
                customer_email="test@example.com",
                items=[],
            )

    def test_invalid_order_id_fails(self) -> None:
        with pytest.raises(ValidationError):
            Order(
                order_id="INVALID",
                customer_email="test@example.com",
                items=[OrderItem(name="Widget", quantity=1, unit_price=10.00)],
            )


class TestDateRange:
    """Tests for DateRange model."""

    def test_valid_date_range(self) -> None:
        dr = DateRange(
            start=datetime(2024, 1, 1),
            end=datetime(2024, 12, 31),
        )
        assert dr.days == 365

    def test_invalid_range_fails(self) -> None:
        with pytest.raises(ValidationError):
            DateRange(
                start=datetime(2024, 12, 31),
                end=datetime(2024, 1, 1),
            )

    def test_same_start_end_fails(self) -> None:
        with pytest.raises(ValidationError):
            DateRange(
                start=datetime(2024, 1, 1),
                end=datetime(2024, 1, 1),
            )


class TestImmutableConfig:
    """Tests for ImmutableConfig model."""

    def test_valid_config(self) -> None:
        config = ImmutableConfig(api_key="secret123", base_url="https://api.example.com")
        assert config.api_key == "secret123"
        assert config.timeout_seconds == 30

    def test_immutable_fails_on_modification(self) -> None:
        config = ImmutableConfig(api_key="secret", base_url="https://api.example.com")
        with pytest.raises(ValidationError):
            config.api_key = "new_secret"  # type: ignore[misc]  # Intentionally testing frozen model

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            ImmutableConfig(
                api_key="secret",
                base_url="https://api.example.com",
                unknown_field="value",  # type: ignore[call-arg]
            )

    def test_invalid_url_fails(self) -> None:
        with pytest.raises(ValidationError):
            ImmutableConfig(api_key="secret", base_url="not-a-url")
