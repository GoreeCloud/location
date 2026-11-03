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
- Automated encrypted backups, full restore drills, retention and schema migrations; consistent online SQLite snapshots are supported via `gclocation backup`.
- Map server deployment, local routing, geocoding, and provider terms.
- MIPS (Identity, GoreeShield, Wardveil, Mesh) integrations only after verified interfaces and gates.

## Development and rollback

No database migrations exist beyond initial idempotent schema creation. Treat schema changes as potentially destructive; take a consistent backup and test migration/rollback on a copy before upgrades. Keep initial user data private. Repository publication does not imply a service has been deployed.

## Follow-up interfaces

- `POST /api/devices/{id}/rotate-token` atomically revokes a prior device-upload token while preserving the device ID, positions, and event history.
- `GET /api/locations/page` performs keyset ordering on `(recorded_at DESC, id DESC)` with a cursor and per-request owner restrictions.
- GPX and GeoJSON exports use streaming responses with separate owner-scoped SQLite reads instead of holding unbounded result arrays in RAM.
- The `gclocation backup --destination NEW_FILE` command uses SQLite's live backup API, exclusive destination creation, and owner-only permissions. No automatic restore or scheduled backup is included.
