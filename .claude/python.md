# Python Rules

## Type Hints

- **ALWAYS use type hints** for function parameters and return types
- Use type hints for class attributes
- Use `from __future__ import annotations` for forward references (Python 3.7+)
- Run `mypy` with strict mode for type checking

```python
from __future__ import annotations

def get_user_by_id(user_id: str) -> User | None:
    ...

def process_items(items: list[Item]) -> dict[str, int]:
    ...
```

## Type Organization

### For Simple Projects

- Store types in a `types.py` file

### For Complex Projects

- Create a `/types` package:
  ```
  /types
    __init__.py    # Re-export all types
    models.py      # Domain models
    api.py         # API types
    common.py      # Shared types
  ```

## Data Classes and Models

### Use dataclasses for Simple Data Structures

```python
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str
    is_active: bool = True
```

### Use Pydantic for Validation and Serialization

```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    email: EmailStr
    is_active: bool = True

    model_config = ConfigDict(frozen=True)  # Immutable
```

### Prefer Pydantic for API Models

- Use Pydantic for request/response models in FastAPI/APIs
- Use `model_validator` for complex validation
- Use `Field` for constraints and documentation

## Code Style (PEP 8)

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Private attributes**: `_single_leading_underscore`
- **Module-level private**: `__double_leading_underscore` (rare)

### Line Length

- Maximum 88 characters (Black's default)
- Use implicit line continuation inside parentheses

### Imports

- Order: standard library, third-party, local
- Use absolute imports
- One import per line for clarity
- Use `isort` for automatic sorting

```python
import os
from pathlib import Path

from fastapi import FastAPI, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.services.user import UserService
```

## Error Handling

### Use Specific Exceptions

```python
# Good
try:
    user = get_user(user_id)
except UserNotFoundError:
    logger.warning(f"User {user_id} not found")
    raise
except DatabaseConnectionError as e:
    logger.error(f"Database error: {e}")
    raise ServiceUnavailableError from e
```

### Create Custom Exceptions

```python
class DomainError(Exception):
    """Base class for domain errors."""
    pass

class UserNotFoundError(DomainError):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")
```

### Never Use Bare Except

```python
# Bad
try:
    something()
except:
    pass

# Good
try:
    something()
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

## Functions

### Use Keyword Arguments for Clarity

```python
# Good
create_user(name="John", email="john@example.com", is_admin=False)

# Use * to force keyword-only arguments
def create_user(*, name: str, email: str, is_admin: bool = False) -> User:
    ...
```

### Return Early

```python
def process_user(user: User | None) -> str:
    if user is None:
        return "No user"

    if not user.is_active:
        return "User inactive"

    return f"Processing {user.name}"
```

## Async/Await

- Use `async/await` for I/O-bound operations
- Use `asyncio.gather()` for concurrent operations
- Use `asyncio.TaskGroup` (Python 3.11+) for structured concurrency
- Never mix sync and async code without proper handling

```python
async def fetch_all_users(user_ids: list[str]) -> list[User]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_user(uid)) for uid in user_ids]
    return [task.result() for task in tasks]
```

## Context Managers

- Use `with` statements for resource management
- Create custom context managers with `@contextmanager` or `__enter__/__exit__`

```python
from contextlib import contextmanager

@contextmanager
def database_transaction():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

## Logging

- Use the `logging` module, not `print()`
- Use structured logging for production
- Include context in log messages

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User created", extra={"user_id": user.id, "email": user.email})
```

## Testing

- Use `pytest` as the test framework
- Use fixtures for setup/teardown
- Use `pytest-asyncio` for async tests
- Mock external dependencies with `unittest.mock` or `pytest-mock`

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_user_repo():
    return Mock(spec=UserRepository)

def test_create_user(mock_user_repo: Mock):
    service = UserService(mock_user_repo)
    user = service.create_user(name="Test", email="test@test.com")

    assert user.name == "Test"
    mock_user_repo.save.assert_called_once()
```

## Tools

- **Formatter**: Black (or Ruff formatter)
- **Linter**: Ruff (replaces flake8, isort, and more)
- **Type checker**: mypy with strict mode
- **Dependency management**: Poetry or uv
- **Virtual environments**: Always use them (`venv`, Poetry, or uv)

## Project Structure

```
/project
  /src
    /app
      __init__.py
      main.py
      /api          # API routes/controllers
      /core         # Config, security, dependencies
      /models       # Database models
      /schemas      # Pydantic schemas
      /services     # Business logic
      /repositories # Data access
  /tests
  pyproject.toml
  .python-version
```
