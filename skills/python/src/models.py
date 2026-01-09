# ABOUTME: Pydantic v2 models for validated API data
# ABOUTME: Use for request/response models, settings, and domain objects
"""Pydantic v2 models demonstrating best practices.

Pydantic models are ideal for:
- API request/response validation
- Domain entities with business rules
- Configuration/settings management
- Data serialization/deserialization

For unvalidated dict shapes, use TypedDict instead (see contracts.py).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)


class Status(str, Enum):
    """Task status enumeration.

    Using str, Enum allows direct JSON serialization.

    Example:
        >>> Status.PENDING.value
        'pending'
        >>> Status("running")
        <Status.RUNNING: 'running'>
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Severity(str, Enum):
    """Issue severity levels.

    Example:
        >>> Severity.LOW.value
        'low'
        >>> Severity.CRITICAL.value
        'critical'
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Address(BaseModel):
    """Validated address model.

    Example:
        >>> addr = Address(street="123 Main St", city="NYC", country="USA")
        >>> addr.model_dump()
        {'street': '123 Main St', 'city': 'NYC', 'country': 'USA', 'postal_code': None}
    """

    street: str = Field(min_length=1, description="Street address")
    city: str = Field(min_length=1, description="City name")
    country: str = Field(min_length=2, max_length=100, description="Country name")
    postal_code: str | None = Field(default=None, pattern=r"^[A-Z0-9\-\s]{3,10}$")


class User(BaseModel):
    """User model with email validation and computed fields.

    Example:
        >>> user = User(id=1, email="alice@example.com", name="Alice Smith")
        >>> user.display_name
        'Alice Smith'
        >>> user.email
        'alice@example.com'
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_default=True,
    )

    id: int = Field(gt=0, description="Unique user identifier")
    email: EmailStr = Field(description="User email address")
    name: str = Field(min_length=1, max_length=100, description="Full name")
    is_active: bool = Field(default=True, description="Account active status")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize name to title case."""
        return v.strip().title()

    @computed_field
    @property
    def display_name(self) -> str:
        """Return formatted display name."""
        return self.name


class Product(BaseModel):
    """Product model with constrained numeric fields.

    Example:
        >>> product = Product(name="Widget", price=10.00, quantity=5)
        >>> product.total_value
        50.0
    """

    name: str = Field(min_length=1, max_length=200)
    price: Annotated[float, Field(gt=0, description="Price in USD")]
    quantity: Annotated[int, Field(ge=0, le=10000, description="Stock quantity")]
    sku: str | None = Field(default=None, pattern=r"^[A-Z]{3}-\d{4}$")

    @computed_field
    @property
    def total_value(self) -> float:
        """Calculate total inventory value."""
        return self.price * self.quantity


class Task(BaseModel):
    """Task model with status tracking.

    Example:
        >>> task = Task(name="Process data", status=Status.PENDING)
        >>> task.status  # use_enum_values=True returns string
        'pending'
    """

    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: Status = Field(default=Status.PENDING)
    priority: int = Field(default=0, ge=0, le=10)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (Status.COMPLETED, Status.FAILED, Status.CANCELLED)


class Order(BaseModel):
    """Order model with nested validation.

    Example:
        >>> order = Order(
        ...     order_id="ORD-001",
        ...     customer_email="alice@example.com",
        ...     items=[{"name": "Widget", "quantity": 2, "unit_price": 9.99}],
        ... )
        >>> order.total
        19.98
    """

    order_id: str = Field(pattern=r"^ORD-\d{3,10}$")
    customer_email: EmailStr
    items: list[OrderItem] = Field(min_length=1)
    discount_percent: float = Field(default=0, ge=0, le=100)

    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate order subtotal."""
        return sum(item.line_total for item in self.items)

    @computed_field
    @property
    def total(self) -> float:
        """Calculate order total after discount."""
        return self.subtotal * (1 - self.discount_percent / 100)


class OrderItem(BaseModel):
    """Order line item."""

    name: str
    quantity: int = Field(gt=0, le=1000)
    unit_price: float = Field(gt=0)

    @computed_field
    @property
    def line_total(self) -> float:
        """Calculate line item total."""
        return self.quantity * self.unit_price


class DateRange(BaseModel):
    """Date range with cross-field validation.

    Example:
        >>> dr = DateRange(
        ...     start=datetime(2024, 1, 1),
        ...     end=datetime(2024, 12, 31),
        ... )
        >>> dr.days
        365
    """

    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_range(self) -> DateRange:
        """Ensure end is after start."""
        if self.end <= self.start:
            msg = "end must be after start"
            raise ValueError(msg)
        return self

    @computed_field
    @property
    def days(self) -> int:
        """Calculate days in range."""
        return (self.end - self.start).days


class ImmutableConfig(BaseModel):
    """Immutable configuration model.

    Example:
        >>> config = ImmutableConfig(api_key="secret", base_url="https://api.example.com")
        >>> config.api_key = "new"  # Raises error
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: ...
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    api_key: str = Field(min_length=1)
    base_url: str = Field(pattern=r"^https?://")
    timeout_seconds: int = Field(default=30, gt=0, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)


# Update forward references for Order -> OrderItem
Order.model_rebuild()
