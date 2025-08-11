# Performance Test Report

## Scope & Targets (per guidelines)
- Listing endpoints must complete within 5 seconds: `/`, `/clubs`, `/showSummary` (POST), `/book/<comp>/<club>`
- Update actions must complete within 2 seconds: `/purchasePlaces` (POST)

## Methodology
- Locust headless tests with 6 users (default) for 1 minute.
- Script: `tests/perf/locustfile.py` with response time checks using `catch_response`.

## Commands
- Start app: `make start`
- Run headless perf: `make perf` (CSV in `reports/locust*`)
- Optional UI: `make perf-ui` (Web UI at http://localhost:8089)

## Metrics Collected
- Request count, failures, average/median/95th percentile response times, throughput (RPS), CSV export.

## Acceptance Criteria
- No response time failures against thresholds.
- Small failure rate (< 1%) due to race conditions is acceptable for POC; otherwise investigate.

## Notes
- Data is in-memory; restarts reset state. For stable perf baselines, seed endpoints or fixtures are recommended.
