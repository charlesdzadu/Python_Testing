# Test Report (Functional + Coverage)

## Scope
- Phase 1: Login, list competitions, book places with constraints, logout.
- Phase 2: Public read-only scoreboard of club points.

## Methodology
- TDD-first edits: unit tests for validation and constraints, integration for end-to-end flow.
- Pytest with coverage enforced at >= 80% for `server.py`.
- Separation of unit and integration tests under `tests/units` and `tests/integrations`.

## Test Cases (Happy and Sad Paths)
- Login
  - Happy: valid email renders summary.
  - Sad: unknown email -> flash error and redirect to index.
- Booking page
  - Happy: valid club and competition renders booking form.
  - Sad: invalid club/competition -> redirect to index.
- Purchase constraints
  - Happy: successful booking deducts places and points, confirms booking.
  - Sad: invalid input (non-integer, <=0), over 12, over availability, insufficient points.
- Public scoreboard
  - Happy: accessible without login.
- Logout
  - Happy: redirects to index.

## Commands
- Unit/integration: `make test`
- Coverage: `make coverage` (outputs `reports/htmlcov` and `reports/junit.xml`)

## Coverage Target
- Enforced via `--cov-fail-under=80`. Current run target: >= 80%.

## Artifacts
- `reports/htmlcov/` HTML coverage report
- `reports/junit.xml` JUnit report for CI

## Notes
- Tests reset in-memory JSON data between tests to avoid cross-test interference.
- For cumulative per-club-per-competition booking caps (12 total), additional state tracking would be required and can be added with extra tests.

