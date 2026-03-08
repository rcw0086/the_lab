# Database Scripts

This directory contains database management scripts for The Lab.

## Scripts

### `seed_db.py`

Populates the database with realistic development data for local testing and frontend development.

**Usage:**

```bash
# Seed database (adds data without clearing existing data)
uv run python scripts/seed_db.py

# Reset and seed database (clears all data first)
uv run python scripts/seed_db.py --reset
```

**What it creates:**

- **Users:** 2 users (athlete and coach roles)
- **Movement Catalog:** 12 movements, 8 implements, 11 variations across 3 types
- **Training Sessions:** 2 complete sessions with modules and sets (strength + endurance)
- **Goals:** 3 goals (mix of achieved and in-progress)
- **Cycles:** 2 training cycles (mesocycle and microcycle)
- **Injuries:** 2 injuries (one resolved, one ongoing)
- **Journal Notes:** 3 notes with entity associations
- **Daily Tracking:** 7 days of nutrition/sleep data

**Requirements:**

- Database must be running (`docker compose up -d`)
- Alembic migrations must be applied (`alembic upgrade head`)

**Features:**

- Realistic data demonstrating schema capabilities
- Proper foreign key dependency handling
- Transaction-safe (rolls back on error)
- Structured logging for visibility
- Idempotent when run without `--reset` flag

## Development Workflow

1. Start database:
   ```bash
   docker compose up -d
   ```

2. Run migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

3. Seed database:
   ```bash
   uv run python scripts/seed_db.py --reset
   ```

4. Verify data:
   ```bash
   docker compose exec postgres psql -U postgres -d the_lab -c "SELECT COUNT(*) FROM users;"
   ```
