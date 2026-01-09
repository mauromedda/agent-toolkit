# ABOUTME: TypedDict contracts for external data shapes
# ABOUTME: Use when interfacing with unvalidated dict data (JSON, APIs)
"""TypedDict contracts for data interchange.

TypedDict is ideal for:
- External API responses
- JSON data before validation
- Configuration dictionaries
- Database row representations

For validated data models, use Pydantic instead (see models.py).
"""

from __future__ import annotations

from typing import NotRequired, Required, TypedDict


class UserProfile(TypedDict):
    """Data contract for user profile from external API.

    Example:
        >>> profile: UserProfile = {
        ...     "user_id": 123,
        ...     "email": "alice@example.com",
        ...     "is_active": True,
        ... }
        >>> profile["email"]
        'alice@example.com'
    """

    user_id: int
    email: str
    is_active: bool
    nickname: NotRequired[str]  # Optional key


class Address(TypedDict):
    """Address data contract.

    Example:
        >>> addr: Address = {
        ...     "street": "123 Main St",
        ...     "city": "NYC",
        ...     "country": "USA",
        ... }
    """

    street: str
    city: str
    country: str
    postal_code: NotRequired[str]


class Customer(TypedDict):
    """Customer with nested address.

    Example:
        >>> customer: Customer = {
        ...     "name": "Alice",
        ...     "email": "alice@example.com",
        ...     "address": {"street": "123 Main", "city": "NYC", "country": "USA"},
        ... }
    """

    name: str
    email: str
    address: Address


class APIResponse(TypedDict):
    """Generic API response structure.

    Example:
        >>> response: APIResponse = {
        ...     "status": "success",
        ...     "data": {"user": "alice"},
        ...     "meta": {"page": 1, "total": 100},
        ... }
    """

    status: str
    data: dict[str, object]
    meta: NotRequired[dict[str, int]]
    error: NotRequired[str]


class PaginatedResponse(TypedDict):
    """Paginated API response.

    Example:
        >>> paginated: PaginatedResponse = {
        ...     "items": [{"id": 1}, {"id": 2}],
        ...     "page": 1,
        ...     "page_size": 10,
        ...     "total_items": 100,
        ... }
    """

    items: list[dict[str, object]]
    page: int
    page_size: int
    total_items: int
    has_next: NotRequired[bool]
    has_prev: NotRequired[bool]


class ConfigDict(TypedDict, total=False):
    """Configuration dictionary with all optional keys.

    Using total=False makes all keys optional.

    Example:
        >>> config: ConfigDict = {"host": "localhost"}
        >>> config.get("port", 8080)
        8080
    """

    host: str
    port: int
    debug: bool
    timeout: float
    retries: int


class RequiredConfig(TypedDict):
    """Configuration with explicit Required/NotRequired.

    Example:
        >>> config: RequiredConfig = {
        ...     "api_key": "secret",
        ...     "base_url": "https://api.example.com",
        ... }
    """

    api_key: Required[str]
    base_url: Required[str]
    timeout: NotRequired[int]
    max_retries: NotRequired[int]


class TaskResult(TypedDict):
    """Result of an async task.

    Example:
        >>> result: TaskResult = {
        ...     "task_id": "abc123",
        ...     "status": "completed",
        ...     "result": {"processed": 100},
        ... }
    """

    task_id: str
    status: str
    result: NotRequired[dict[str, object]]
    error: NotRequired[str]
    started_at: NotRequired[str]
    completed_at: NotRequired[str]
