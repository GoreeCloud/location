# GoreeCloud Location

GoreeCloud Location is GoreeCloud's privacy-first, first-party location application and service for live tracking, location history, device state, and the staged path toward sharing, geofencing, trips, places, Find My recovery, and location analytics.

## Status

**Forge / Development — not production-ready or Anchor-qualified.**

The accepted repository baseline contains a validated PostgreSQL/PostGIS runtime, authenticated multi-user/device foundations, native device-authenticated sample ingestion, owner-scoped history/live reads, server-enforced tracking pause/resume, a bounded Timeline surface with deletion/export controls, a Development Find My device-state surface, and a server-authoritative recovery-capability gate. The current clean stabilization candidate adds the consolidated Timeline ordering/accuracy/scope/privacy work, Platform Contract 2.0 governance, and a repository-local GLAZE UI V1.6 / 1.6.0 source mapping.

Source/CI validation does not establish production deployment, production identity, geographic map delivery, background tracking acceptance, recovery command authority, anti-stalking acceptance, release, or Anchor qualification.

## Project authority

- [PROJECT-SPECIFICATIONS.md](PROJECT-SPECIFICATIONS.md) — authoritative project requirements, architecture, privacy/security obligations, accepted scope, and lifecycle gates.
- [PROJECT-RECORD.md](PROJECT-RECORD.md) — significant project history, governance transitions, migration evidence, and dated acceptance evidence.
- [IMPLEMENTED-FEATURES.md](IMPLEMENTED-FEATURES.md) — evidence-backed implemented capability inventory.
- [PLANNED-FEATURES.md](PLANNED-FEATURES.md) — open, planned, partial, blocked, and acceptance-gated feature work.
- [CHANGELOGS.md](CHANGELOGS.md) — repository and release-oriented change history.

Project specifications are maintained in GitHub. The former Google Drive specification is a frozen migration source only and is not a parallel project authority.

## Governing principles

- Location data is private by default.
- Every accepted sample has an explicit owning user and source device.
- Administration does not automatically grant access to ordinary users' location histories.
- Sharing must be explicit, revocable, and independently scoped when implemented.
- Device credentials are distinct from interactive user sessions.
- Raw precise coordinates must not be written to ordinary application logs.
- Tracking pause and device revocation are server-enforced boundaries.
- No advertising, behavioral advertising, or sale of location data is permitted.
- Mapping, geocoding, and routing dependencies must remain replaceable.
- Data must remain exportable through documented accepted formats when portability features are implemented.
- Find My Anchor qualification requires dedicated privacy, recovery, abuse-prevention, security, continuity, and anti-stalking acceptance.

## Current architecture

```text
Web / Android / future approved clients
          |
          v
     Location API v1
          |
   +------+------+----------------+
   |             |                |
Ingestion   History/Live    Find My capability state
   |             |                |
   +-------------+----------------+
                 |
          PostgreSQL + PostGIS
```

Current implementation direction:

- **Web:** TypeScript. Current approved target is GLAZE UI V1.6 / 1.6.0; the current stabilization candidate contains the repository-local V1.6 source mapping, which remains candidate-only until promotion.
- **API/services:** Go.
- **Android:** native Kotlin direction/current foundation where implemented.
- **Database:** PostgreSQL + PostGIS.
- **Maps:** replaceable MapLibre-compatible provider architecture; production geographic delivery is not yet accepted.
- **Deployment:** controlled self-hosted GoreeCloud infrastructure when production gates are satisfied.

## Current authenticated web experience

The Development web client can use an interim session-scoped user credential to access owner-scoped state. The credential is stored in browser `sessionStorage` and removed at sign-out. This is not the final production GoreeCloud Identity session design.

The Live experience supports authenticated identity, live/last-known device state, sample age, accuracy, optional battery information, stale/no-location states, manual refresh, periodic automatic refresh, and server-enforced tracking pause/resume.

The Timeline reuses the authenticated owner-scoped history API and renders at most 50 persisted samples per request. Device and Past hour / Past 24 hours / Past 7 days selections issue bounded `device_id`, `from`, `to`, and `limit=50` history queries to the existing server contract rather than treating a previously loaded 50-row snapshot as complete history. The server remains authoritative for owner scope. A failed filter request preserves the previously rendered Timeline instead of presenting failure as an empty history.

Timeline history deletion is an explicit control, not an inference from the visible 50 rows. A deletion request requires browser confirmation and calls the existing owner-scoped server deletion contract for one bounded batch of at most 500 matching samples. The server re-checks ownership, cutoff, and optional device scope. The browser never auto-repeats when more history may remain.

The browser can also download the **currently loaded** bounded Timeline view as CSV or GeoJSON without making another history request. CSV applies spreadsheet-formula hardening to text cells. GeoJSON emits independent Point features with `[longitude, latitude]` coordinates and the current sample metadata. Neither format connects samples into a route or infers visits, stays, trips, transport modes, geofences, or movement.

The browser never supplies an authoritative user ID; the server derives ownership from the authenticated credential.

### Geographic map boundary

Coordinates are available from the native API and persisted in PostGIS, but the current web surface does not claim production geographic map delivery. Map tiles remain gated until the replaceable provider adapter and its privacy/security/operational acceptance are complete.

## Current Find My Development surface

Find My is a first-party GoreeCloud Location capability. The merged Development source includes an owner-scoped device discovery/state surface rather than only a planned navigation destination.

Current implemented presentation includes:

- owner-scoped device search/listing;
- responsive device state cards;
- explicit Live / Recent / Stale / Offline / Unavailable presentation;
- last-location age and accuracy when available;
- optional battery information;
- sanitized diagnostic state; and
- server-authoritative recovery capability state.

`GET /api/v1/find-my/recovery-capabilities` is authenticated through the existing user boundary and returns capability state only for the authenticated owner's enrolled devices. Lost Mode, Play Sound, and Mark Found are currently denied server-side. Active enrollments report `recovery_authority_unavailable`; revoked enrollments report `device_enrollment_revoked`. The web client keeps controls disabled if the capability response is missing or unavailable.

Current source does **not** establish Lost Mode execution, remote erase, nearby finding, offline finding, Find My Network, trusted-place recovery, anti-stalking runtime acceptance, or production recovery authority. `Offline` is a Development state derived from available sample/device recency, not proof of a real-time network connectivity probe.

## API boundary

The first-party API is versioned under `/api/v1/`. Ownership comes from authenticated user/device credentials, never request-supplied user identifiers.

Current Development endpoints include health/readiness, authenticated identity, owner-scoped device listing/enrollment/revocation, owner preferences/tracking pause, authenticated device identity, device-authenticated location ingestion, owner-scoped location history/deletion, owner-scoped live state, and owner-scoped Find My recovery capability state.

The owner-scoped history endpoint accepts bounded device/time/range filters and limit constraints. Those filters narrow an already authenticated owner's history; they do not grant access to another user's samples. Local export reuses only responses that have already passed this authenticated boundary.

The ingestion path validates bounded sample data, derives ownership from the device credential, rejects user-session credentials for device ingestion, enforces idempotency, rechecks revocation, enforces tracking pause in the transaction, and stores location through the PostGIS ownership schema.

## Security, privacy, and platform systems

Platform Contract 2.0 evaluates exactly nine Integral Platform Systems:

- **GoreeCloud Manager** — lifecycle, administration, inventory, operational control, approvals, remediation, and management-plane visibility.
- **Privacy Shield** — privacy, consent/permission, minimization, retention, sharing, tracking privacy, and disclosure controls.
- **Wardveil Security** — protection, trust, anti-abuse, anti-stalking, recovery-security, threat handling, and response evidence.
- **Everkeep** — export, backup, restore, recovery, preservation, portability, migration readiness, and succession.
- **Glaze UI** — presentation, accessibility, adaptive behavior, status/evidence presentation, and resilience.
- **GoreeCloud Mesh** — governed first-party coordination, dependency awareness, events, and evidence routing.
- **GoreeCloud Identity** — production user/device/account/session and credential authority.
- **GoreeCloud Policy** — policy representation, evaluation, decisions, precedence, enforcement coordination, explanation, freshness, and evidence.
- **GoreeCloud Observability** — health, metrics, logs/events/traces, diagnostics, dependency health, correlation, freshness, and collection-gap truth.

GoreeCloud Sync remains separately governed and is not a tenth Integral Platform System.

Passing source tests does not constitute production acceptance of these systems.

## Current limitations

Still incomplete or separately gated:

- production GoreeCloud Identity browser/device integration;
- production geographic map/geocoding/routing provider deployment;
- Android background collection and representative-device acceptance;
- encrypted offline queue/synchronization;
- general sharing/public links;
- complete-account export/import, broader retention-policy management, route inference, trips, places, geofences, and insights;
- production Find My recovery commands and offline/nearby finding;
- anti-stalking runtime acceptance;
- full portability/backup/restore acceptance;
- production deployment, signed release, and Anchor qualification.

## Documentation

- [USER-MANUAL.md](USER-MANUAL.md)
- [PROJECT-SPECIFICATIONS.md](PROJECT-SPECIFICATIONS.md)
- [PROJECT-RECORD.md](PROJECT-RECORD.md)
- [FEATURES.md](FEATURES.md)
- [BENEFITS.md](BENEFITS.md)
- [COMPETITIVE-OBJECTIVES.md](COMPETITIVE-OBJECTIVES.md)
- [docs/development-runtime.md](docs/development-runtime.md)
- [docs/authentication.md](docs/authentication.md)
- [docs/tracking.md](docs/tracking.md)
- [docs/live-web-experience.md](docs/live-web-experience.md)
- [docs/timeline-development-surface.md](docs/timeline-development-surface.md)
- [docs/find-my-development-surface.md](docs/find-my-development-surface.md)
- [docs/security.md](docs/security.md)
- [docs/privacy.md](docs/privacy.md)

## License

GNU Affero General Public License v3.0. See `LICENSE`.