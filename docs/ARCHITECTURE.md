# GoreeCloud Location — Architecture and Operations

**Status: Development preview, 3 November 2026.** This describes the actual initial implementation and its boundaries, not a deployed production system.

## Components

1. **Web client:** HTML, CSS and browser JavaScript in `src/goreecloud_location/static`. No CDN, analytics tracker, or third-party JavaScript. The UI calls the local API, maintains an in-tab login token, and requests a one-time GPS fix only after a user click.
2. **API:** FastAPI in `main.py` served by Uvicorn. The service binds to loopback by default. Requests are protected by account sessions or restricted per-device upload tokens.
3. **Storage:** SQLite under `GC_LOCATION_DB` (default XDG data home). Tables: accounts, sessions, devices, points, places, geofence_state, events. User ownership is enforced through every query joining a device or a place.
4. **Maps:** Native coordinate plotting in the web UI. The optional `GC_TILE_TEMPLATE` only permits same-origin relative URLs. A separate operator-managed tile server can be reverse-proxied.
5. **Deployment:** Dockerfile uses a non-root account. Compose binds to 127.0.0.1, drops Linux capabilities, sets read-only root filesystem and persistent database volume.

## Trust boundaries

- **Account admin:** local terminal access required; no public setup endpoint and no auto-generated default passwords.
- **Session:** scrypt-hashed passwords, random session token returned once, SHA-256 token hash in database, 8-hour expiry, explicit logout. Stored in sessionStorage by the browser; any script injection would be a high-severity risk, so CSP and text-only insertion are part of the design.
- **Device:** independently generated ingestion token returned once, SHA-256 stored at rest. Device token permits only HTTP position writes to the matching device.
- **User scope:** authenticated API queries restrict device/point/place/event records by account ownership. No cross-account family sharing currently exists.
- **Network:** operator must provide TLS and additional abuse protection before exposure beyond localhost. No public sharing endpoints exist.

## Request flow

```text
Browser / compatible tracker
        | HTTPS (recommended remote) or localhost
        v
FastAPI authentication / validation
        |
        v
Owner-scoped SQLite transaction
        |               |
        |               +--> circular geofence transitions / events
        v
History API --> authenticated web dashboard / exports
```

## Geofence semantics

Each location point is checked against the owner's saved circular places using Haversine distance. A state is initialized without an arrival event (avoids an invented transition); later inside/outside transitions generate events. Points with missing or insufficient accuracy do not trigger transitions. Older out-of-order uploads are recorded but do not mutate current geofence state. This is an initial algorithm, not a guaranteed safety notification system.

## Limitations requiring engineering work

- Additional pagination/date filters and resumable downloads; keyset pagination and full streaming GPX/GeoJSON are implemented.
- Session rotation, persistent distributed rate limiting, MFA and external identity integration; device-key rotation is implemented.
- Authentication/session design review for native apps; verify the already implemented device-token rotation with external tracking clients.
- Multiuser family circles with explicit per-user consent, sharing grants, revocation and audit trails.
- Recalculation of geofence state when existing history/places are edited.
- GPS telemetry pipelines, dedicated protocol adapters and service observability.
- Background mobile collection and OS-specific power-management behavior.
- Queue-based notifications with provider success/failure and delivery safeguards.
- High-volume PostgreSQL/PostGIS or other spatial storage after evidence warrants migration.
- Automated encrypted backups, production restore drills, retention and schema migrations; consistent online snapshots and verified restore-to-new-file are available via the local CLI.
- Map server deployment, local routing, geocoding, and provider terms.
- MIPS (Identity, GoreeShield, Wardveil, Mesh) integrations only after verified interfaces and gates.

## Development and rollback

Individual point deletion removes that device's geofence events for the same recorded timestamp and resets fence state. Full device-history erasure deletes points, all events and fence state while preserving the registered device and upload key. Erasure from the live database does not remove downloaded exports or offline backups.

No database migrations exist beyond initial idempotent schema creation. Treat schema changes as potentially destructive; take a consistent backup and test migration/rollback on a copy before upgrades. Keep initial user data private. Repository publication does not imply a service has been deployed.

## Follow-up interfaces

- `POST /api/devices/{id}/rotate-token` atomically revokes a prior device-upload token while preserving the device ID, positions, and event history.
- `GET /api/locations/page` performs keyset ordering on `(recorded_at DESC, id DESC)` with a cursor and per-request owner restrictions.
- GPX and GeoJSON exports use streaming responses with separate owner-scoped SQLite reads instead of holding unbounded result arrays in RAM.
- The `gclocation backup --destination NEW_FILE` command uses SQLite's live backup API, exclusive destination creation, and owner-only permissions. `gclocation verify-backup --source SNAPSHOT` validates integrity, foreign keys and expected schema read-only. `gclocation restore --source SNAPSHOT --destination NEW_DB` restores only to a new file and invalidates copied user sessions. No automatic failover, scheduled backup, production restore test or data migration is included.

## CSV import path

An account owner can submit a raw text/csv body to a registered device. The API bounds request streaming to 2 MiB and validates required headers, timestamp timezone and GPS bounds for up to 5,000 data rows before starting a SQLite write transaction. Validated points are processed chronologically with duplicate checks. A failed row aborts before any write; write-stage exceptions roll back the transaction. This initial importer is not suitable for unbounded historical migrations and does not ingest arbitrary CSV columns or external provider-specific archives.

## Login and session resource budgets

The authentication module uses a bounded, process-local sliding-window limiter with separate username, ASGI peer and global budgets. The initial limits are 5/40/300 attempts in five minutes, with an LRU cap on memory buckets. A random in-memory dummy scrypt hash prevents unknown-user requests from skipping the expensive password verifier. Successful login clears a username's attempt bucket, but peer/global throttles continue to apply. Expired sessions are purged on successful login; no more than 20 active sessions per user are retained. This is not a multi-worker or multi-server rate limit, nor a replacement for TLS, trusted proxy configuration, MFA or a security review.


## Manual retention workflow

The owner-scoped API offers read-only counts before an explicitly confirmed UTC cutoff deletion. An immediate SQLite write transaction rechecks the counts to reject stale previews. Old GPS positions/events are removed and affected devices' geofence state is reset. The process is not scheduled and does not purge backed-up or exported copies. Fresh location points and device credentials remain.
