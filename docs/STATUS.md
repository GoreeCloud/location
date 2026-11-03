# Implementation Status — GoreeCloud Location

**As of 3 November 2026 · 0.1.0 development foundation**

The requested 22-category specification is the **target roadmap**, not a statement that those features are already present. There are no claims of a signed mobile release, production deployment, completed GoreeCloud UI screenshot audit, security certification, or a professional emergency-response integration.

| Capability | Status | Evidence |
| --- | --- | --- |
| Self-hosted API and SQLite persistence | GitHub CI API tests pass; deployment not verified | `main.py`, `store.py`, Dockerfile |
| Local account setup; sessions; logout | API test coverage passes; deployment not verified | `cli.py`, `main.py` |
| Owner-isolated device registration and ingestion | API test coverage passes; deployment not verified | `main.py`, `tests/test_api.py` |
| Location history, last-known position | Cursor pagination and history tests passed in GitHub CI; deployment unverified | `GET /api/locations`, `GET /api/devices` |
| Circular geofences and event history | API test coverage passes; deployment not verified | `places`, `geofence_state`, `events` |
| Browser GPS capture on user action | Implemented in source, browser/device UX unverified | `static/app.js` |
| Responsive dashboard and private coordinate visualization | Implemented in source, visual acceptance unverified | `static/index.html`, `styles.css` |
| Same-origin optional tile overlays | Implemented integration point, tile server not included | `GC_TILE_TEMPLATE` |
| Full streaming GPX/GeoJSON exports | API test coverage passes; deployment not verified | `/api/export/*` |
| Native Android / iOS / Linux app | Not implemented | Future milestone |
| Family circles and consented live sharing | Not implemented | Future milestone |
| Location import pipelines, photo timeline, exploration analytics | Bounded CSV import added in development source; broader provider imports and insights not implemented | Future milestone |
| Fleet protocol adapters / specialized GPS hardware integrations | Not implemented | Future milestone |
| Driving safety scoring and crash detection | Not implemented | Future milestone |
| Emergency SOS dispatch and service-provider coordination | Not implemented | Future milestone |
| Pet/item networks and Bluetooth tracking | Not implemented | Future milestone |
| External notification gateways and automation connectors | Not implemented | Future milestone |
| Security hardening, scale, backup restore testing | Device-key rotation, owner-only database modes and manual backups in source; full hardening and production restore acceptance pending | `docs/SECURITY.md` |
| GC UI acceptance and MIPS integrations | Specification reviewed; not validated | GC UI source authority |

### Next priorities

1. Extend automated checks with browser and deployment smoke tests.
2. Perform secure external access review; add account/session rotation and additional throttling.
3. Implement additional imports, retention controls, full production recovery drills and resumable exports; keyset pagination, manual snapshots and restore-to-new-file now exist in source.
4. Complete location map tiling and geocoding integration using owner-controlled services.
5. Add private multiuser circles with explicit consent and independently reviewed authorization.
6. Add native mobile background tracking after platform-specific security review.
7. Explore GPS hardware, automation, notifications and safety workflows separately.

## Verification

- [GitHub Actions run 41602334393](https://github.com/GoreeCloud/location/actions/runs/41602334393), 3 November 2026: 8 API tests passed, Python compile passed, JavaScript syntax check passed.
- Tests cover unauthorized access, account isolation, device ingestion, location history/export, geofence transition logic, input validation, session revocation, and login rate limiting.
- Not tested: live GPS clients, browser rendering, TLS reverse proxy, dedicated hardware, full restore, load/performance, or independent penetration testing.

No real location data or credential is committed. This document should be updated only to reflect verified outcomes.

## Development cycle 2 — security and history

**Implemented in source, not yet independently accepted:**

- Device token rotation that invalidates the previous token and keeps all location history.
- Authenticated, account-scoped cursor pagination for location history.
- Complete streaming owner-scoped GPX and GeoJSON exports without the previous 10,000-point limit.
- Consistent SQLite snapshot command and owner-only database/backup file permissions.
- Device key rotation exposed in the web interface with a clear reconfiguration warning.

Verification: [GitHub Actions run 41603993957](https://github.com/GoreeCloud/location/actions/runs/41603993957) passed 12 API tests, Python compilation, and JavaScript syntax checks on 3 November 2026. Browser rendering, production exposure and restoration remain unverified. No production deployment or GPS hardware integration is implied.

## Development cycle 3 — privacy erasure

**Implemented in source and covered by passing GitHub API tests; browser and operational verification still pending:**

- Confirmed per-device erasure of points, geofence events and cached fence state while retaining device registration and upload key.
- Related events removed when an individual GPS point is deleted; fence state reset to avoid stale transitions.
- Owner-isolation and state-reset regression tests and a typed-confirmation web dialog.

Verification: [GitHub Actions push run 41604428762](https://github.com/GoreeCloud/location/actions/runs/41604428762) and [pull-request run 41604457779](https://github.com/GoreeCloud/location/actions/runs/41604457779) completed successfully on 3 November 2026, with **14 API tests passing**, Python compilation and JavaScript syntax checks. [PR #5](https://github.com/GoreeCloud/location/pull/5) was merged into main. Browser screenshot acceptance, Internet-exposure review, restore drills and independent security assessment are still unverified.

Live erasure does not automatically remove separate downloaded exports, backups, logs or offline device caches.

## Development cycle 4 — initial CSV imports

**Implemented in source and tested in GitHub CI; visual and deployed-run verification pending:**

- Owner-scoped text/csv import endpoint, explicitly restricted to a registered device.
- 2 MiB and 5,000-record limits, strict GPS/timestamp/header validation, transactional import, and duplicate skipping.
- Dedicated History interface for selecting the destination device and uploading a CSV file.
- Test cases for successful import, repeated files, unauthorized accounts and malformed data.

Verification: [GitHub Actions push run 41605059607](https://github.com/GoreeCloud/location/actions/runs/41605059607) and [PR run 41605081825](https://github.com/GoreeCloud/location/actions/runs/41605081825) passed **16 API tests**, Python compilation, and JavaScript syntax checks on 3 November 2026. [PR #6](https://github.com/GoreeCloud/location/pull/6) merged into main. Browser rendering, real GPS hardware, large-file performance, and production safety remain unverified.

Provider-specific Takeout/GPX/FIT/TCX/GeoJSON imports, large-file progress, resilient concurrency guarantees and import undo remain planned.

## CI supply-chain maintenance

The GitHub Actions workflow now pins `actions/checkout` v5 and `actions/setup-python` v6 to the verified official commit SHAs, both using Node 24, with a 12-minute job timeout. [GitHub Actions run 41605346798](https://github.com/GoreeCloud/location/actions/runs/41605346798) completed successfully on 3 November 2026: **16 API tests passed**, Python compilation and JavaScript syntax checks passed. Seven dependency/test framework deprecation warnings remain; these are not equivalent to a vulnerability audit or production acceptance.


## Development cycle 5 — backup verification and recovery

**Implemented in source; passed synthetic-data smoke and GitHub API tests. Production recovery acceptance remains pending:**

- Read-only SQLite snapshot verification: header, full integrity, foreign keys, and required GoreeCloud Location schema.
- Operator-only restore to a new path; existing files are never overwritten.
- Restored account sessions are cleared, preventing stale session replay; device ingestion credentials are preserved.
- Recovery test cases cover history restoration, authentication, corruption, incompatible schemas, permissions, symlinks, and refusal to overwrite.

Verification: [GitHub Actions push run 41606502423](https://github.com/GoreeCloud/location/actions/runs/41606502423) and [pull-request run 41606524731](https://github.com/GoreeCloud/location/actions/runs/41606524731) passed **21 API tests**, Python compilation and JavaScript syntax checks on 3 November 2026. [PR #7](https://github.com/GoreeCloud/location/pull/7) merged into main. A local smoke test also exercised snapshot, integrity verification, restore, stale-session revocation, permissions, and negative source/destination cases.

No server has been redeployed. This is a local administrative recovery tool, not automatic failover or a production disaster-recovery certification.

## Development cycle 6 — authentication protection

**Implemented and covered by passing GitHub tests; production authentication acceptance pending:**

- Bounded, thread-safe username/ASGI-peer/global attempt limits reserved before password verification.
- Unknown usernames undergo the same scrypt verifier path using an unused dummy hash.
- At most 20 live user sessions per account; older sessions are automatically revoked.
- Unit and API tests cover expiration, concurrent admissions, memory bounds, unknown-user verifier calls, username isolation, and session caps.

Verification: [push CI 41607236405](https://github.com/GoreeCloud/location/actions/runs/41607236405) and [PR CI 41607266407](https://github.com/GoreeCloud/location/actions/runs/41607266407) passed **27 automated tests**, Python compilation and JavaScript syntax on 3 November 2026; [PR #8](https://github.com/GoreeCloud/location/pull/8) merged to main. A local standalone limiter smoke test also passed.

Limitations: these counters are process-local and ASGI peer identity depends on trusted proxy configuration. They do not amount to distributed abuse prevention, MFA, or production Internet security acceptance.


## Development cycle 7 — real HTTP loopback smoke

**Implemented and verified in GitHub CI on synthetic loopback data:**

- Start the real Uvicorn CLI service on a randomly allocated loopback port against a synthetic temporary database.
- Exercise health, a private-by-default endpoint, disabled OpenAPI, static dashboard resources, login, device creation, a GPS point, paginated history and logout over real HTTP.
- Assert that the CLI refuses non-loopback binding unless the operator provides the explicit exposure-warning flag.
- Always terminate the test process and avoid live customer data.

Verification: [GitHub Actions push run 41607627558](https://github.com/GoreeCloud/location/actions/runs/41607627558) and [PR run 41607649847](https://github.com/GoreeCloud/location/actions/runs/41607649847) each passed **29 automated tests**, Python compilation, and JavaScript syntax checks on 3 November 2026. [PR #9](https://github.com/GoreeCloud/location/pull/9) merged into main.

This validates a development server's loopback startup and request wiring only. It is not a native mobile, browser screenshot, TLS, proxy, Docker, load or production deployment acceptance test.


## Development cycle 8 — manual retention controls

**Implemented in source, with GitHub CI passing; visual and production acceptance pending:**

- Owner-scoped read-only preview for GPS positions and geofence events older than a configurable number of days.
- Manual cleanup with explicit confirmation and matching preview counts rechecked inside a write transaction.
- Account-isolated deletion of old positions/events; affected geofence state resets; newer history/devices remain.
- Settings interface with preview-first flow, typed authorization, confirmation and backup warnings.
- Regression tests for privacy isolation, no-change preview, stale counts and repeat cleanup.

Verification: [push CI 41608724599](https://github.com/GoreeCloud/location/actions/runs/41608724599) and [PR CI 41608749686](https://github.com/GoreeCloud/location/actions/runs/41608749686) both passed **31 automated tests**, Python compilation and JavaScript syntax checks on 3 November 2026. [PR #10](https://github.com/GoreeCloud/location/pull/10) merged into main.

Not an automatic retention schedule, backup removal, offline-device cleanup or certified secure erasure.

## Development cycle 9 — mobile navigation and rendered browser QA

**Implemented in main; GitHub API and Chromium browser CI passed. Further visual/a11y acceptance remains open:**

- Visible mobile Privacy navigation and mobile Sign out control (the previously hidden desktop sidebar contained both).
- Playwright Chromium browser journey using a throwaway loopback API and synthetic location records.
- Desktop, tablet and phone screenshot evidence in light/dark modes, with secret tokens masked.
- Assertions for responsive navigation, sign-out, GPS capture, private network requests, console errors and horizontal document overflow.

Verification: [GitHub Actions run 41638054089](https://github.com/GoreeCloud/location/actions/runs/41638054089) passed **31 API tests**, Python and JavaScript checks, and browser journeys for 1440×900 desktop, 820×1180 tablet, and 390×844 phone using isolated synthetic accounts. Device enrollment, browser GPS capture, private retention preview, light/dark theme, navigation and sign-out passed. [PR #11](https://github.com/GoreeCloud/location/pull/11) merged into `main`.

Visual evidence: [18 synthetic screenshots, masked device tokens](https://github.com/GoreeCloud/location/actions/runs/41638054089) retained as a seven-day GitHub Actions artifact. Screenshots of desktop login/overview/settings/dialog, phone login/settings/tracked overview, and tablet settings were manually examined. The interface is visibly styled and responsive; remaining design observations include an uneven second row in the tablet/desktop settings grid, and further keyboard/screen-reader, high contrast, focus and physical-device acceptance. Do not interpret green CI as complete premium design compliance.

Even successful browser CI does not establish completed GC UI visual acceptance, keyboard/screen-reader quality, native mobile clients or production deployment.

## Development cycle 10 — settings composition

**Candidate improvement awaiting CI and screenshot review:**

- Rebalance three Privacy & settings cards to one row on wide desktop screens, a full-width final information card on tablet screens, and a vertical stack on phones.
- Include layout geometry checks in the Chromium browser regression suite for all three supported viewport sizes.
- Document observed screenshot quality and remaining acceptance criteria in [visual audit](VISUAL_AUDIT_2026-11-03.md).

No native mobile functionality or production deployment is implied. Full GC UI visual acceptance still requires further verification.
