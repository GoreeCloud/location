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

**Implemented and verified through GitHub CI and inspected Chromium screenshots:**

- Rebalance three Privacy & settings cards to one row on wide desktop screens, a full-width final information card on tablet screens, and a vertical stack on phones.
- Include layout geometry checks in the Chromium browser regression suite for all three supported viewport sizes.
- Document observed screenshot quality and remaining acceptance criteria in [visual audit](VISUAL_AUDIT_2026-11-03.md).

Verification: [GitHub Actions run 41638709939](https://github.com/GoreeCloud/location/actions/runs/41638709939) passed **31 API tests**, JavaScript syntax and real Chromium browser journeys at desktop/tablet/mobile widths, including CSS geometry assertions. All 18 synthetic screenshots were generated, and corrected desktop/tablet light-settings screenshots were inspected to confirm balanced layout. [PR #12](https://github.com/GoreeCloud/location/pull/12) merged to main. Remaining browser engines, accessibility and native application verification are still open.

No native mobile functionality or production deployment is implied. Full GC UI visual acceptance still requires further verification.

## Development cycle 11 — keyboard and modal accessibility

**Implemented, with API and Chromium browser CI passing:**

- Give the one-time device-token modal and history-erasure dialog explicit accessible names and descriptions.
- Use real keyboard Enter activation for Settings navigation, dialog Done action and Sign out.
- Assert Escape safely dismisses the erasure dialog without deleting data, and token text is cleared after closing.
- Verification: [GitHub Actions run 41639265596](https://github.com/GoreeCloud/location/actions/runs/41639265596) passed the **31 API tests** plus real Chromium keyboard/dialog interaction journeys at desktop, tablet and phone sizes; [PR #13](https://github.com/GoreeCloud/location/pull/13) merged to main. The tests check accessible dialog names/descriptions and safe Escape dismissal; no production data was changed.

Retain explicit limits: this is an automated Chromium keyboard smoke check, not a complete screen-reader or WCAG audit.

## Development cycle 12 — geofence chronology correctness

**Implemented in `main`, verified by automated tests on 5 November 2026; production acceptance remains open:**

- Only strictly newer recorded GPS timestamps can update a device's current geofence state.
- Preserve equal-timestamp/conflicting positions and older backfill as account-private history without generating contradictory arrival/departure events.
- Apply the same safeguard to account-authenticated uploads, GPS hardware-token uploads and chronological CSV imports.
- Regression tests exercise equal-time conflicts, historical backfill, authentic later transitions, account separation and upload-channel consistency.

Verification: [PR #15](https://github.com/GoreeCloud/location/pull/15) merged into `main` after [CI run 42102244038](https://github.com/GoreeCloud/location/actions/runs/42102244038) passed **35 API tests** (7 dependency/framework warnings), Python compilation and JavaScript syntax checks, and Playwright Chromium desktop/tablet/phone journeys. No real location data was changed.

**Not verified:** concurrent-writer ordering, clock spoofing, native tracking hardware, emergency-response reliability, and any production deployment or acceptance.

## Development cycle 13 — atomic GPS ingestion

**Implemented in `main`; GitHub CI passed 5 November 2026:**

- Reserve SQLite's immediate writer lock before latest-location checks during account, device-token and CSV ingestion.
- Update points, geofence state and related events together in one rollback-capable transaction.
- Add a concurrent real-API regression test with mixed owner and device-token clients, asserting one arrival and one departure per chronological batch without lock errors.

Verification: [PR #16](https://github.com/GoreeCloud/location/pull/16) merged after [CI run 42103124834](https://github.com/GoreeCloud/location/actions/runs/42103124834) passed **36 automated API tests** (7 dependency/framework warnings), Python compilation, JavaScript syntax and three-viewport Chromium browser journeys. The concurrency test used synthetic credentials and GPS coordinates; no real location data or running service was modified.

**Limits:** single SQLite database only, no distributed queue, load certification or production tracking acceptance. A simultaneous-uploads test is not proof of reliability under all levels of contention.

## Development cycle 14 — same-origin map tile privacy

**Implemented in `main`; GitHub CI passed 5 November 2026:**

- Reject external host, protocol-relative, slash-backslash and control-character map tile templates in the public configuration endpoint.
- Verify each resolved browser tile URL is same-origin before creating an image request.
- Tighten Content Security Policy image origins to self and data only.
- Include API regressions for safe/unsafe templates and a hostile browser configuration interception with third-party request detection.

Verification: [PR #17](https://github.com/GoreeCloud/location/pull/17) merged after [CI run 42105167224](https://github.com/GoreeCloud/location/actions/runs/42105167224) passed **46 automated API tests**, Python compilation, JavaScript syntax checks and three-viewport Chromium browser journeys, including hostile tile-configuration interception. All tests use synthetic data and a loopback-only server.

**Limitations:** does not include a tile server, redirect-policy audit for a future reverse proxy, native client audit, or a production data privacy certification.

## Development cycle 15 — account-wide session revocation

**Implemented and verified in `main`, 5 November 2026:**

- Provide an authenticated `POST /api/auth/logout-all` endpoint for owner-scoped account session invalidation.
- Add a confirmed account-wide Sign out action in Privacy & settings while retaining standard single-session logout.
- Keep other accounts' sessions and independent device ingestion keys intact.
- Add API tests for account separation, repeated revoked-token rejection, device-token scope and new login, plus a Chromium confirmation journey.

Verification: [PR #18](https://github.com/GoreeCloud/location/pull/18) merged after [CI run 42106102664](https://github.com/GoreeCloud/location/actions/runs/42106102664) passed **48 API tests**, Python compilation, JavaScript syntax and desktop/tablet/phone Chromium browser journeys (including both cancellation and confirmation). No real account sessions or live tracking service were modified.

**Limits:** no MFA/OIDC, trusted-device inventory, token replay detection, distributed session policy or account recovery.

## Development cycle 16 — OwnTracks-compatible HTTP ingestion

**Merged in `main`; synthetic GitHub API and Chromium CI passed 5 November 2026; real-client acceptance remains open:**

- Authenticate HTTP Basic clients against each registered device's one-time, write-only ingestion token, with a fixed `owntracks` username.
- Accept bounded OwnTracks JSON location reports, convert Unix-seconds timestamps and speed units, and use existing per-device SQLite/geofence processing.
- Acknowledge recognized non-location housekeeping records without persisting untrusted user/device metadata or client-reported geofence transitions; reject malformed, encrypted and oversized requests.
- Add synthetic API regression tests for location telemetry, chronology, owner isolation, Basic/Bearer separation, key rotation and malformed payloads.
- Document setup, HTTPS requirements, and unsupported MQTT/encryption/native-device acceptance in [OwnTracks HTTP](OWNTRACKS_HTTP.md).

Verification: [PR #19](https://github.com/GoreeCloud/location/pull/19) merged after [GitHub CI run 42108927294](https://github.com/GoreeCloud/location/actions/runs/42108927294) passed **65 automated API tests** (7 dependency/framework warnings), Python compilation, JavaScript syntax, and Playwright Chromium desktop/tablet/phone journeys. Tests used synthetic location data and device tokens only.

**Remaining gates:** Native OwnTracks Android/iOS validation on authorized devices, reverse-proxy/TLS review and actual recovery testing. This is not proof of background mobile tracking or production readiness.

## Development cycle 17 — privacy-first GPX history import

**Merged in `main`; synthetic API and Chromium CI passed 5 November 2026; production acceptance remains open:**

- Import owner-selected GPX 1.0 and 1.1 track point history with strict timestamp validation, optional elevation and chronological ordering.
- Use `defusedxml` to block DTD, entities and external references; limit requests to 2 MiB and 5,000 points; reject malformed files before writing.
- Reuse the CSV importer's owner-scoped SQLite write transaction and duplicate handling; preserve existing private GPS and geofence semantics.
- Add browser History GPX file input and desktop/tablet/phone synthetic interaction testing, plus API regressions for round-trip compatibility, isolation, limits, unsafe XML and atomicity.
- Document supported GPX scope and operator precautions in [GPX import](GPX_IMPORT.md).

Verification: [PR #20](https://github.com/GoreeCloud/location/pull/20) merged after [CI run 42110306429](https://github.com/GoreeCloud/location/actions/runs/42110306429) passed **71 automated API tests** (7 dependency/framework warnings), Python compilation, JavaScript syntax and desktop/tablet/phone Chromium browser journeys with synthetic GPX uploads. The first review run identified a mistaken expectation of an arrival event for GPX points without accuracy; the test was corrected to enforce the existing privacy/safety behavior. No real GPS records were used.

**Remaining gates:** Independent hostile XML and large-file tests, real-world archive compatibility, production TLS and external security review. This is not a general-purpose import service.

## Development cycle 18 — GeoJSON import and unified History upload

**Merged into `main`; synthetic GitHub API and Chromium CI passed 5 November 2026; production acceptance remains open:**

- Import owner-scoped GeoJSON RFC 7946 `FeatureCollection` data containing timestamped `Point` features, with optional GPS metadata and third-coordinate altitude.
- Validate longitude/latitude, timezone-aware times, numerical fields, feature structure, 2 MiB body limit and 5,000-record cap before using the shared atomic CSV/GPX transaction.
- Keep foreign identity/URLs/metadata, non-Point geometries and missing time information out of the stored history.
- Consolidate CSV, GPX and GeoJSON History file upload into one accessible file chooser and document format selection.
- Add synthetic API regressions for export/import round trips, account isolation, invalid data, idempotency and malformed uploads, plus three-viewport browser journeys.

Verification: [PR #21](https://github.com/GoreeCloud/location/pull/21) merged after [CI run 42111279069](https://github.com/GoreeCloud/location/actions/runs/42111279069) passed **77 automated API tests** (7 framework/dependency warnings), Python compilation, JavaScript syntax and desktop/tablet/phone Chromium browser journeys exercising both GPX and GeoJSON imports using the unified History control. Tests used synthetic data only.

**Remaining gates:** Real external GeoJSON archive interoperability, independent hostile-input fuzzing, accessibility/visual review of the unified controls, and production security acceptance.

## Development cycle 19 — unified History importer regression

**Merged in `main`; GitHub API and Chromium CI passed 5 November 2026:**

- Exercise synthetic CSV, GPX and GeoJSON imports through the one History file chooser on desktop, tablet and phone.
- Assert each format increases the owner’s point count as expected.
- Verify an unsupported file extension is rejected before any import HTTP request is sent.
- Preserve synthetic-only location data, masked tracker tokens, and private loopback service boundaries.

Verification: [PR #22](https://github.com/GoreeCloud/location/pull/22) merged after [GitHub CI run 42111807749](https://github.com/GoreeCloud/location/actions/runs/42111807749) passed **77 API tests**, Python compilation, JavaScript syntax, and Playwright desktop/tablet/phone journeys uploading CSV, GPX and GeoJSON. The browser also rejected a `.txt` file before any HTTP import request. All data was synthetic.

This is not full external-file interoperability, screen-reader acceptance, physical-device testing or production deployment.

## Development cycle 20 — browser session privacy isolation

Verification: https://github.com/GoreeCloud/location/actions/runs/42119520716

**Merged through PR #23, verified by passing 77 API tests and Chromium desktop/tablet/phone journeys on 5 November 2026:**

- Clear in-tab GPS history, device/places/event arrays, selected device, map markers, coordinate labels, transient messages and private forms on sign-out.
- Prevent a slow refresh or late 401 from an old session from overwriting or signing out a different account.
- Add desktop/tablet/phone Chromium regression journeys that switch between two synthetic accounts in one tab and verify no previous user's location remains in DOM or application state.
- No API, SQLite schema or real user location data is modified.

**Limits:** Browser memory garbage collection, downloaded/exported files, screenshots, offline caches, server sessions and TLS acceptance require separate controls and review.

## Development cycle 21 — owner-controlled device collection pause

**Merged into `main` and verified with synthetic API and Chromium CI (5 November 2026):**

- Add persisted owner-scoped pause and resume timestamps to registered devices using an additive, serialized SQLite migration that preserves existing records and keys.
- Add `PUT /api/devices/{id}/collection` with strict Boolean validation, transactional ownership checks and idempotent state changes.
- Reject new owner, tracker-token, OwnTracks and CSV/GPX/GeoJSON device writes while paused. Resume rejects queued live fixes recorded before the server cutoff; deliberate owner archive imports remain possible after resume without retroactive alerts.
- Reset live geofence baseline on resume. Add UI controls and disable browser GPS capture for paused devices.
- Add API tests for account isolation, all ingestion routes, old timestamps, post-resume fences and existing-database migration, plus synthetic Chromium journeys at desktop/tablet/mobile widths.

Verification: [PR #24](https://github.com/GoreeCloud/location/pull/24) merged after [CI run 42127934586](https://github.com/GoreeCloud/location/actions/runs/42127934586) passed **81 API tests** (7 framework/dependency warnings), Python compilation, JavaScript checks, and desktop/tablet/mobile Chromium journeys after reconciling the prior browser-session privacy changes. Existing-database migrations, authorization boundaries, post-resume cutoff behavior and geofence reset are covered by the new tests. No live tracking or production services were altered.

**Limits:** Client GPS hardware may continue local recording, timestamps are untrusted, no family/third-party consent workflow exists, and no production deployment is authorized.
