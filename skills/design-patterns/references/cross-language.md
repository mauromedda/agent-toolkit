# ABOUTME: Cross-language architectural patterns for Go, Python, Bash, and Terraform
# ABOUTME: Covers DI, error handling, testing, config, logging, and common anti-patterns

# Cross-Language Architectural Patterns

Common patterns implemented consistently across Go, Python, Bash, and Terraform.

---

## 1. Dependency Injection

### Go

```go
// Define interface at consumer site
type UserStore interface {
    Get(ctx context.Context, id string) (*User, error)
}

// Constructor injection
type UserService struct {
    store  UserStore
    logger *slog.Logger
}

func NewUserService(store UserStore, logger *slog.Logger) (*UserService, error) {
    if store == nil {
        return nil, errors.New("store is required")
    }
    if logger == nil {
        logger = slog.Default()
    }
    return &UserService{store: store, logger: logger}, nil
}
```

### Python

```python
from typing import Protocol
from collections.abc import Callable

class UserStore(Protocol):
    """Interface for user storage."""
    def get(self, user_id: str) -> User | None: ...

class UserService:
    """User service with injected dependencies."""

    def __init__(
        self,
        store: UserStore,
        logger: logging.Logger | None = None,
    ) -> None:
        if store is None:
            raise ValueError("store is required")
        self.store = store
        self.logger = logger or logging.getLogger(__name__)
```

### Bash

```bash
# Function injection via variables
process_file() {
    local -r file="${1}"
    local -r processor="${FILE_PROCESSOR:-default_processor}"

    "${processor}" "${file}"
}

# Override for testing
FILE_PROCESSOR=mock_processor process_file "test.txt"
```

### Terraform

```hcl
# Module inputs as dependency injection
variable "vpc_id" {
  description = "VPC ID for resource placement"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the service"
  type        = list(string)
}

# Consumer provides dependencies
module "service" {
  source     = "./modules/service"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}
```

---

## 2. Error Handling

### Go

```go
// Wrap errors with context
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    user, err := s.store.Get(ctx, id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            return nil, fmt.Errorf("user %s not found: %w", id, err)
        }
        return nil, fmt.Errorf("failed to get user %s: %w", id, err)
    }
    return user, nil
}

// Sentinel errors for expected conditions
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// Check with errors.Is/As
if errors.Is(err, ErrNotFound) {
    return http.StatusNotFound
}
```

### Python

```python
class UserNotFoundError(Exception):
    """Raised when user is not found."""
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")

class UserService:
    def get_user(self, user_id: str) -> User:
        try:
            return self.store.get(user_id)
        except StoreError as e:
            raise UserNotFoundError(user_id) from e  # Chain exceptions
```

### Bash

```bash
# Exit codes
declare -ri EXIT_SUCCESS=0
declare -ri EXIT_FAILURE=1
declare -ri EXIT_NOT_FOUND=10

get_user() {
    local -r user_id="${1}"

    result=$(query_store "${user_id}" 2>&1)
    rc=$?
    if [[ ${rc} -ne 0 ]]; then
        log_error "Failed to get user ${user_id}: ${result}"
        return "${EXIT_FAILURE}"
    fi

    if [[ -z "${result}" ]]; then
        log_warn "User ${user_id} not found"
        return "${EXIT_NOT_FOUND}"
    fi

    echo "${result}"
    return "${EXIT_SUCCESS}"
}
```

### Terraform

```hcl
# Validation blocks for input errors
variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid CIDR block."
  }
}

# Preconditions in resources
resource "aws_instance" "app" {
  lifecycle {
    precondition {
      condition     = data.aws_ami.app.architecture == "x86_64"
      error_message = "AMI must be x86_64 architecture."
    }
  }
}
```

---

## 3. Configuration

### Go

```go
// Config struct with env parsing
type Config struct {
    Host     string `env:"APP_HOST" envDefault:"localhost"`
    Port     int    `env:"APP_PORT" envDefault:"8080"`
    LogLevel string `env:"LOG_LEVEL" envDefault:"info"`
    DBUrl    string `env:"DATABASE_URL,required"`
}

func LoadConfig() (*Config, error) {
    var cfg Config
    if err := env.Parse(&cfg); err != nil {
        return nil, fmt.Errorf("parsing config: %w", err)
    }
    return &cfg, nil
}
```

### Python

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings from environment."""

    host: str = Field(default="localhost", alias="APP_HOST")
    port: int = Field(default=8080, alias="APP_PORT")
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    database_url: str = Field(..., alias="DATABASE_URL")  # Required

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### Bash

```bash
# Environment with defaults
readonly HOST="${APP_HOST:-localhost}"
readonly PORT="${APP_PORT:-8080}"
readonly LOG_LEVEL="${LOG_LEVEL:-info}"

# Required variable check
if [[ -z "${DATABASE_URL:-}" ]]; then
    die "DATABASE_URL environment variable is required"
fi

# Config file loading
load_config() {
    local -r config_file="${1:-${SCRIPT_DIR}/.env}"
    if [[ -f "${config_file}" ]]; then
        # shellcheck source=/dev/null
        source "${config_file}"
    fi
}
```

### Terraform

```hcl
# terraform.tfvars for environment-specific values
# dev.tfvars
environment = "dev"
instance_type = "t3.small"

# prod.tfvars
environment = "prod"
instance_type = "t3.large"

# Variables with defaults
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

# Usage: terraform apply -var-file="dev.tfvars"
```

---

## 4. Logging

### Go

```go
import "log/slog"

// Structured logging
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("request processed",
    slog.String("method", r.Method),
    slog.String("path", r.URL.Path),
    slog.Duration("latency", elapsed),
    slog.Int("status", status),
)

// With context
logger.InfoContext(ctx, "user action",
    slog.String("user_id", userID),
    slog.String("action", action),
)
```

### Python

```python
import logging
from typing import Any

# Configure structured logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Structured logging with extra
logger.info(
    "Request processed",
    extra={
        "method": request.method,
        "path": request.path,
        "latency_ms": latency,
        "status": status,
    },
)
```

### Bash

```bash
# Logging functions to stderr
log_debug() {
    if [[ "${VERBOSE:-false}" == true ]]; then
        echo "[DEBUG] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
    fi
}

log_info() {
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
}

log_warn() {
    echo "[WARN] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
}

log_error() {
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") ${*}" >&2
}

# Usage
log_info "Processing file: ${filename}"
log_error "Failed to connect: ${error_message}"
```

---

## 5. Testing Heuristics

### Observable Design

> "Make small production changes to improve testability when test code becomes overcomplicated."

If your tests require excessive mocking, consider:
- Breaking dependencies
- Extracting interfaces
- Using dependency injection

### Multiple Test Cases

> "Well-designed code typically has multiple behaviors worth testing."

A single test case often indicates:
- Incomplete coverage
- Missing edge cases
- Overly coupled code

### Avoid Change Detectors

> "Tests should verify business outcomes, not implementation details."

```go
// BAD: Tests internal implementation
func TestProcessUser_CallsValidate(t *testing.T) {
    mock := &MockValidator{}
    svc := NewService(mock)
    svc.ProcessUser(user)
    assert.True(t, mock.ValidateCalled)  // Tests HOW, not WHAT
}

// GOOD: Tests observable behavior
func TestProcessUser_RejectsInvalidEmail(t *testing.T) {
    svc := NewService(realValidator)
    err := svc.ProcessUser(User{Email: "invalid"})
    assert.ErrorIs(t, err, ErrInvalidEmail)  // Tests WHAT happens
}
```

### Real Over Mocks

Prefer real implementations:
- Use test databases (SQLite in-memory)
- Use real HTTP clients with test servers
- Use real file systems with temp directories

```go
// Prefer
func TestUserStore_Get(t *testing.T) {
    db := setupTestDB(t)  // Real database
    store := NewUserStore(db)
    // ...
}

// Over
func TestUserStore_Get(t *testing.T) {
    mockDB := &MockDB{}
    mockDB.On("Query", mock.Anything).Return(...)
    // ...
}
```

---

## 6. Background Jobs

### Go (Worker Pool)

```go
func ProcessItems(ctx context.Context, items []Item, workers int) error {
    g, ctx := errgroup.WithContext(ctx)
    sem := make(chan struct{}, workers)

    for _, item := range items {
        item := item
        g.Go(func() error {
            select {
            case sem <- struct{}{}:
                defer func() { <-sem }()
            case <-ctx.Done():
                return ctx.Err()
            }
            return processItem(ctx, item)
        })
    }
    return g.Wait()
}
```

### Python (Celery/Background)

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task(bind=True, max_retries=3)
def process_item(self, item_id: str) -> dict:
    """Process item asynchronously.

    Jobs should:
    - Be idempotent
    - Pass IDs, not objects
    - Handle retries gracefully
    """
    try:
        item = Item.get(item_id)
        return item.process()
    except TransientError as e:
        raise self.retry(exc=e, countdown=60)
```

### Bash (Background with Control)

```bash
process_parallel() {
    local -r -a files=("${@}")
    local -r max_jobs=4
    local -i job_count=0

    for file in "${files[@]}"; do
        process_single "${file}" &

        (( job_count++ ))
        if (( job_count >= max_jobs )); then
            wait -n  # Wait for any job to finish
            (( job_count-- ))
        fi
    done

    wait  # Wait for all remaining
}
```

---

## 7. Common Anti-Patterns

### Go

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Naked error return | No context | Wrap with `fmt.Errorf` |
| Global mutable state | Race conditions | Pass as dependency |
| Large interfaces | Weak abstraction | Define at consumer |
| Panic in libraries | Unrecoverable | Return errors |

### Python

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Mutable defaults | Shared state bugs | Use `None` + assignment |
| Bare except | Hides bugs | Catch specific exceptions |
| `eval()`/`exec()` | Security risk | Use safe alternatives |
| No type hints | Runtime errors | Add type annotations |

### Bash

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| No `set -euo pipefail` | Silent failures | Add safety headers |
| Using `[ ]` | Word splitting issues | Use `[[ ]]` |
| Unquoted variables | Word splitting | Quote: `"${var}"` |
| Backticks | Nesting issues | Use `$(command)` |

### Terraform

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded secrets | Security risk | Use Secrets Manager |
| Local state | No collaboration | Use remote backend |
| No version pins | Breaking changes | Pin provider versions |
| `count` for resources | Index-based issues | Use `for_each` |

---

## 8. Naming Conventions

### Go

```go
// Packages: short, lowercase, no underscores
package user
package httputil

// Exported: PascalCase
func ProcessRequest() {}
type UserService struct {}

// Unexported: camelCase
func processInternal() {}
type userCache struct {}

// Interfaces: -er suffix for single method
type Reader interface { Read() }
type Processor interface { Process() }
```

### Python

```python
# Modules: lowercase_snake_case
# user_service.py

# Classes: PascalCase
class UserService:
    pass

# Functions/methods: lowercase_snake_case
def process_user(user_id: str) -> User:
    pass

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRIES = 3

# Private: leading underscore
def _internal_helper():
    pass
```

### Bash

```bash
# Script files: lowercase-kebab-case.sh
# process-data.sh

# Functions: lowercase_snake_case
process_file() { ... }

# Variables: lowercase_snake_case
local -r input_file="${1}"

# Constants: SCREAMING_SNAKE_CASE
readonly MAX_RETRIES=3
declare -ri EXIT_SUCCESS=0
```

### Terraform

```hcl
# Resources: provider_resource_purpose
resource "aws_instance" "web_server" {}
resource "aws_s3_bucket" "logs" {}

# Variables: lowercase_snake_case
variable "instance_type" {}
variable "vpc_cidr_block" {}

# Outputs: lowercase_snake_case
output "instance_public_ip" {}

# Locals: lowercase_snake_case
locals {
  name_prefix = "${var.project}-${var.environment}"
}
```

---

## 9. When to Use Each Language

| Use Case | Language | Reason |
|----------|----------|--------|
| API services | Go | Performance, concurrency |
| Data processing | Python | Libraries, expressiveness |
| Quick automation | Bash | Available everywhere |
| Infrastructure | Terraform | Declarative, state management |
| Build orchestration | Make | Universal, dependency tracking |
