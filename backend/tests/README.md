# Database Testing Infrastructure

This directory contains the database testing infrastructure for The Lab backend.

## Overview

The testing infrastructure provides:

1. **Separate test database** (`the_lab_test`)
2. **Fast transaction-based test isolation** (no schema recreation per test)
3. **Factory fixtures** for creating test data
4. **Assertion helpers** for verifying database state
5. **Example tests** demonstrating best practices

## Quick Start

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=the_lab --cov-report=html

# Run specific test file
uv run pytest tests/test_fixtures_example.py

# Run with verbose output
uv run pytest -v

# Run tests matching a pattern
uv run pytest -k "test_constraint"
```

### Test Database Setup

The test infrastructure automatically:
- Uses `the_lab_test` database (separate from development)
- Creates schema once at session start
- Uses transaction rollback for test isolation (very fast)
- Cleans up after test session completes

**Important:** Ensure the `the_lab_test` database exists:

```bash
# Create test database (one-time setup)
docker compose exec postgres psql -U postgres -c "CREATE DATABASE the_lab_test;"

# Or connect to postgres and run:
# CREATE DATABASE the_lab_test;
```

## Directory Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and base fixtures
├── test_settings.py             # Test-specific settings
├── fixtures/
│   ├── __init__.py
│   ├── factories.py             # Factory functions for creating test data
│   └── assertions.py            # Helper functions for assertions
└── test_fixtures_example.py     # Example tests demonstrating usage
```

## Key Components

### 1. Test Settings (`test_settings.py`)

Overrides production settings to use test database:

```python
from tests.test_settings import get_test_settings

settings = get_test_settings()
# Uses the_lab_test database
```

### 2. Database Session Fixture (`conftest.py`)

Provides isolated database session using transaction rollback:

```python
def test_something(db_session: Session):
    user = create_user(db_session, username="test")
    db_session.commit()
    # Changes automatically rolled back after test
```

**How it works:**
- Creates a database connection
- Begins a transaction
- Creates a nested transaction (SAVEPOINT)
- Allows `commit()` in tests (commits to SAVEPOINT)
- Rolls back transaction after test (undoes all changes)

**Benefits:**
- Tests run in complete isolation
- No test pollution between tests
- 10-100x faster than recreating schema per test
- Can use `commit()` normally in tests

### 3. Factory Fixtures (`fixtures/factories.py`)

Convenient functions for creating test data:

```python
from tests.fixtures.factories import (
    create_user,
    create_daily,
    create_training_session,
    create_complete_strength_set,
)

def test_example(db_session: Session):
    # Create user with defaults
    user = create_user(db_session)

    # Create user with custom values
    athlete = create_user(db_session, username="athlete123", role="athlete")

    # Create related entities
    daily = create_daily(db_session, user=user, protein=180)
    session = create_training_session(db_session, user=user)

    # Create complex entities
    module = create_module(db_session, session, order_in_session=1)
    set_obj, details, movement, implement = create_complete_strength_set(
        db_session,
        module=module,
        movement_name="Squat",
        implement_name="Barbell",
        reps=5,
        load=Decimal("225"),
    )
```

**Available factories:**

Core entities:
- `create_user()`
- `create_daily()`
- `create_cycle()`
- `create_goal()`
- `create_injury()`

Journal:
- `create_note()`

Session:
- `create_training_session()`
- `create_module()`

Catalog:
- `create_movement()`
- `create_implement()`
- `create_variation_type()`
- `create_variation()`

Sets:
- `create_set()`
- `create_strength_set_details()`
- `create_endurance_set_details()`

Complex scenarios:
- `create_complete_strength_set()`
- `create_complete_endurance_set()`

### 4. Assertion Helpers (`fixtures/assertions.py`)

Convenient assertion functions for verifying database state:

```python
from tests.fixtures.assertions import (
    assert_count,
    assert_exists,
    assert_not_exists,
    assert_field_value,
    assert_relationship_count,
    assert_cascade_deleted,
    assert_unique_constraint_violated,
    assert_check_constraint_violated,
)

def test_example(db_session: Session):
    user = create_user(db_session, username="test")
    db_session.commit()

    # Verify count
    assert_count(db_session, User, 1)

    # Verify existence
    assert_exists(db_session, User, username="test")
    assert_not_exists(db_session, User, username="nonexistent")

    # Verify field values
    assert_field_value(db_session, User, user.id, "username", "test")

    # Verify relationships
    assert_relationship_count(db_session, user, "dailies", 0)

    # Verify constraints
    create_user(db_session, username="test")  # Duplicate
    with pytest.raises(IntegrityError) as exc:
        db_session.commit()
    assert_unique_constraint_violated(exc.value)
```

## Writing Tests

### Basic Test Structure

```python
from sqlalchemy.orm import Session
from tests.fixtures.factories import create_user

def test_user_creation(db_session: Session):
    """Test creating a user."""
    # Arrange
    username = "test_athlete"

    # Act
    user = create_user(db_session, username=username)
    db_session.commit()

    # Assert
    assert user.id is not None
    assert user.username == username
```

### Testing Constraints

```python
import pytest
from sqlalchemy.exc import IntegrityError
from tests.fixtures.assertions import assert_check_constraint_violated

def test_protein_must_be_positive(db_session: Session):
    """Test that protein must be >= 0."""
    user = create_user(db_session)
    create_daily(db_session, user=user, protein=-10)

    with pytest.raises(IntegrityError) as exc:
        db_session.commit()

    assert_check_constraint_violated(exc.value)
```

### Testing Relationships

```python
from tests.fixtures.assertions import assert_relationship_count, assert_cascade_deleted

def test_user_has_dailies(db_session: Session):
    """Test user can have multiple daily records."""
    user = create_user(db_session)

    for i in range(5):
        create_daily(db_session, user=user, date_value=date.today() - timedelta(days=i))

    db_session.commit()

    assert_relationship_count(db_session, user, "dailies", 5)

def test_cascade_delete(db_session: Session):
    """Test that deleting user cascades to dailies."""
    user = create_user(db_session)
    daily = create_daily(db_session, user=user)
    db_session.commit()

    daily_id = daily.id

    db_session.delete(user)
    db_session.commit()

    assert_cascade_deleted(db_session, Daily, daily_id)
```

### Testing Complex Scenarios

```python
def test_complete_training_session(db_session: Session):
    """Test creating a full training session with sets."""
    # Create user and session
    user = create_user(db_session)
    session = create_training_session(db_session, user=user)

    # Create module
    module = create_module(db_session, session, order_in_session=1)

    # Create complete strength set
    set_obj, details, movement, implement = create_complete_strength_set(
        db_session,
        module=module,
        movement_name="Squat",
        implement_name="Barbell",
        reps=5,
        load=Decimal("225"),
    )

    db_session.commit()

    # Verify structure
    assert_count(db_session, TrainingSession, 1)
    assert_count(db_session, Module, 1)
    assert_count(db_session, Set, 1)
    assert_count(db_session, StrengthSetDetails, 1)
    assert details.reps == 5
    assert details.external_load_value == Decimal("225")
```

## Best Practices

### 1. Use Factories

**Good:**
```python
user = create_user(db_session, username="athlete")
```

**Avoid:**
```python
user = User(username="athlete")
db_session.add(user)
db_session.flush()  # Easy to forget
```

### 2. Use Assertion Helpers

**Good:**
```python
assert_count(db_session, User, 1)
assert_exists(db_session, User, username="test")
```

**Avoid:**
```python
assert db_session.query(User).count() == 1
assert db_session.query(User).filter_by(username="test").first() is not None
```

### 3. Test Isolation

Each test should be independent:

```python
# Good: Each test creates its own data
def test_feature_a(db_session: Session):
    user = create_user(db_session)
    # Test feature A

def test_feature_b(db_session: Session):
    user = create_user(db_session)
    # Test feature B
```

### 4. Commit When Needed

You can call `commit()` in tests - it commits to a SAVEPOINT that gets rolled back:

```python
def test_something(db_session: Session):
    user = create_user(db_session)
    db_session.commit()  # OK - commits to SAVEPOINT

    # Modify user
    user.role = "admin"
    db_session.commit()  # OK - commits to SAVEPOINT

    # All changes rolled back after test
```

### 5. Test Both Happy and Error Paths

```python
def test_valid_data(db_session: Session):
    """Test valid data succeeds."""
    user = create_user(db_session, username="valid")
    db_session.commit()
    assert_exists(db_session, User, username="valid")

def test_invalid_data(db_session: Session):
    """Test invalid data fails."""
    create_user(db_session, username="test")
    db_session.commit()

    create_user(db_session, username="test")  # Duplicate
    with pytest.raises(IntegrityError):
        db_session.commit()
```

## Performance

### Why Transaction Rollback is Fast

Traditional approach (SLOW):
```python
# Per test:
# 1. DROP SCHEMA CASCADE
# 2. CREATE SCHEMA
# 3. Create all tables
# 4. Create all indexes
# 5. Create all constraints
# 6. Run test
# 7. DROP SCHEMA CASCADE
```

Transaction rollback (FAST):
```python
# Once per session:
# 1. Create all tables

# Per test:
# 1. BEGIN transaction
# 2. Run test
# 3. ROLLBACK transaction
```

**Result:** 10-100x faster test execution.

### Benchmarks

Approximate test execution times:

- Creating 100 dailies: ~50ms
- Creating complex session with sets: ~100ms
- Testing constraint violation: ~10ms

## Troubleshooting

### Test database doesn't exist

```bash
# Create the test database
docker compose exec postgres psql -U postgres -c "CREATE DATABASE the_lab_test;"
```

### Changes persisting between tests

This shouldn't happen with transaction rollback. If it does:
1. Check that you're using the `db_session` fixture
2. Verify no test is calling `connection.commit()` directly
3. Check for threading issues

### Slow test execution

If tests are slow:
1. Verify you're using transaction rollback (not schema recreation)
2. Minimize unnecessary `commit()` calls
3. Use bulk operations for large datasets
4. Check database connection pooling

### Import errors

```python
# Make sure to import from correct modules
from tests.fixtures.factories import create_user  # Good
from the_lab.db.models.core import User  # For model reference only
```

## Examples

See `test_fixtures_example.py` for comprehensive examples of:
- Basic model creation
- Constraint validation
- Relationship testing
- Complex scenarios
- Transaction isolation
- Performance considerations

## References

- [SQLAlchemy Testing Docs](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [The Lab ADR-005: Testing Strategy](../../docs/adr/)
