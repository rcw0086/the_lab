<!-- filepath: /Users/rob/dev/projects/python/the_lab/docs/adr/adr-004.md -->

## ADR-004: Authentication & Authorization Baseline

**Status:** Accepted
**Updated:** 2026-03-20 — expanded with auth flow design (#51)

**Decision**
Auth required by default; least-privilege authorization. JWT-based stateless authentication with short-lived access tokens and longer-lived refresh tokens.

**Rationale**

- Avoid retrofitting security later
- Stateless JWT fits the REST-first API style (ADR-003) — no server-side session storage needed
- Single-user app today, but the design should not preclude multi-user without rework

---

### Authentication Flow

#### Registration (`POST /auth/register`)

1. Client submits `username` and `password`
2. Server validates uniqueness of `username`
3. Server hashes password with **bcrypt** (cost factor 12)
4. Server creates `User` record with `password_hash` column
5. Server returns `UserRead` (no tokens — user must log in)

#### Login (`POST /auth/login`)

1. Client submits `username` and `password`
2. Server looks up user by `username`
3. Server verifies password against stored `password_hash` via bcrypt
4. On success, server returns an **access token** and a **refresh token**
5. On failure, server returns `401 Unauthorized` with a generic message (do not reveal whether username or password was wrong)

#### Accessing Protected Routes

1. Client sends `Authorization: Bearer <access_token>` header
2. `get_current_user()` FastAPI dependency decodes and validates the token
3. If valid, the dependency returns the `User` record (loaded from DB by `sub` claim)
4. If invalid or expired, returns `401 Unauthorized`

#### Token Refresh (`POST /auth/refresh`)

1. Client sends the refresh token in the request body
2. Server validates the refresh token
3. On success, server issues a **new access token** (and optionally a new refresh token — rotation)
4. On failure, returns `401 Unauthorized` — client must re-authenticate

---

### JWT Token Structure

#### Access Token Claims

| Claim | Type   | Description                         |
|-------|--------|-------------------------------------|
| `sub` | `str`  | User ID (as string per JWT spec)    |
| `username` | `str` | Username for convenience          |
| `role` | `str \| null` | User role (e.g. "admin", "athlete") |
| `type` | `str` | Token type: `"access"`             |
| `exp` | `int`  | Expiration (UTC timestamp)          |
| `iat` | `int`  | Issued-at (UTC timestamp)           |

#### Refresh Token Claims

| Claim | Type   | Description                         |
|-------|--------|-------------------------------------|
| `sub` | `str`  | User ID (as string per JWT spec)    |
| `type` | `str` | Token type: `"refresh"`            |
| `exp` | `int`  | Expiration (UTC timestamp)          |
| `iat` | `int`  | Issued-at (UTC timestamp)           |

#### Token Lifetimes

| Token         | Default Lifetime | Config Key                         |
|---------------|------------------|------------------------------------|
| Access token  | 30 minutes       | `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`  |
| Refresh token | 7 days           | `JWT_REFRESH_TOKEN_EXPIRE_DAYS`    |

These are already defined in `Settings` (`config.py`).

#### Signing

- **Algorithm:** HS256 (HMAC-SHA256) — configured via `JWT_ALGORITHM`
- **Secret:** `JWT_SECRET_KEY` environment variable (required, no default)
- HS256 is appropriate for a monolithic app where the same server signs and verifies tokens. If the architecture later moves to separate services (contrary to ADR-007), switch to RS256 with a keypair.

---

### Token Refresh Strategy

**Approach: Refresh token rotation**

- Each call to `POST /auth/refresh` returns a new access token **and** a new refresh token
- The previous refresh token is invalidated
- This limits the damage window if a refresh token is leaked

**Implementation — simple approach (v1):**

Refresh tokens are stateless JWTs (same as access tokens but with longer expiry and `type: "refresh"`). No server-side token storage in v1.

**Trade-off:** Without server-side storage, individual refresh tokens cannot be revoked. This is acceptable for a single-user personal app. If multi-user or revocation becomes a requirement, add a `refresh_tokens` table with a `revoked_at` column and check it during refresh.

---

### Database Changes Required

The `users` table needs a `password_hash` column:

```sql
ALTER TABLE users ADD COLUMN password_hash VARCHAR(128) NOT NULL;
```

This will be added in the implementation tasks (#52–#56) via an Alembic migration.

---

### Public vs Protected Routes

| Route               | Auth Required |
|----------------------|---------------|
| `GET /`             | No            |
| `GET /health`       | No            |
| `GET /docs`         | No            |
| `GET /redoc`        | No            |
| `POST /auth/register` | No          |
| `POST /auth/login`  | No            |
| `POST /auth/refresh`| No (token in body) |
| All other endpoints  | **Yes**       |

Protected routes use a shared FastAPI dependency (`get_current_user`) that extracts the user from the JWT. Routes that need ownership checks (e.g. "only see your own dailies") will filter by `user_id` from the token's `sub` claim.

---

### Security Considerations

1. **Password storage:** bcrypt with cost factor 12. Never store or log plaintext passwords.
2. **Timing attacks:** Use `secrets.compare_digest` or bcrypt's built-in constant-time comparison when verifying passwords.
3. **Token leakage:** Access tokens are short-lived (30 min) to limit exposure. Refresh tokens rotate on use.
4. **Secret management:** `JWT_SECRET_KEY` has no default and must be set via environment variable. The app will fail to start without it.
5. **Error messages:** Auth failures return generic messages — never reveal whether a username exists or which credential was wrong.
6. **HTTPS:** Tokens are transmitted as Bearer headers. In production, enforce HTTPS to prevent interception. (Out of scope for app code; handled at deployment/reverse proxy layer.)
7. **CORS:** Already configured (ADR-003, `config.py`). Credentials are allowed for the configured origins only.

---

### Consequences

- Slight upfront complexity to implement auth before feature endpoints
- All future endpoints get auth "for free" via the `get_current_user` dependency
- Stateless tokens mean no session table to manage (until/unless revocation is needed)
- `password_hash` column must be added to the `users` table before auth endpoints work
