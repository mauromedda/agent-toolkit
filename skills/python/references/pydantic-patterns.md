# ABOUTME: Detailed Pydantic v2 patterns for validation, serialization, settings
# ABOUTME: Extended reference for API models, field validation, configuration

# Pydantic v2 Patterns

## Basic Model

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

## Field Validation

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

## Computed Fields

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

## Model Configuration

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

## Enums with Pydantic

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

## Nested Models

```python
from pydantic import BaseModel

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

## Discriminated Unions

```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float

class Model(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator="pet_type")

# Automatically parses to correct type
m = Model.model_validate({"pet": {"pet_type": "cat", "meows": 4}})
```

## Settings Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
    )

    debug: bool = False
    database_url: str
    secret_key: str

# Loads from environment variables: APP_DEBUG, APP_DATABASE_URL, etc.
settings = AppSettings()
```

## Custom Validators

```python
from pydantic import BaseModel, model_validator
from typing import Self

class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
        return self
```

## Serialization Aliases

```python
from pydantic import BaseModel, Field

class APIResponse(BaseModel):
    user_id: int = Field(alias="userId")
    is_active: bool = Field(alias="isActive", serialization_alias="active")

    model_config = ConfigDict(populate_by_name=True)

# Can parse from camelCase
resp = APIResponse.model_validate({"userId": 1, "isActive": True})

# Serializes with aliases
print(resp.model_dump(by_alias=True))
```

## TypedDict vs Pydantic

| Feature | TypedDict | Pydantic |
|---------|-----------|----------|
| Validation | No (type checker only) | Yes (runtime) |
| Serialization | Manual | Built-in |
| Default values | No | Yes |
| Use Case | Type hints only | Full validation |
