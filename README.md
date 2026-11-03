# GoreeCloud Location

**Privacy-first, self-hosted location tracking.** GoreeCloud Location is an original early-development project for individuals, households, and future family/fleet use. The broader product plan covers GPS tracking, location history, geofences, travel intelligence, vehicles, pets, belongings, automation, and safety services. **This repository currently implements a smaller working foundation.**

> **Status: Development preview (0.1.0). Not Stable, deployed, or emergency-ready.**
> Never use the current version as an emergency dispatcher, crash response system, or safety-critical tracker.

## What works today

- Private accounts created by a local administrator; password hashes use scrypt.
- Login with short-lived, hashed-at-rest bearer sessions; logout revokes sessions.
- User-owned devices (people, vehicles, pets, items, assets) with one-time, owner-rotatable ingestion tokens.
- Authenticated HTTP location ingestion from browsers or compatible senders.
- Account-scoped, bounded raw CSV imports with all-row validation, duplicate skipping and browser file selection.
- Validated GPS latitude/longitude, accuracy, altitude, speed, heading, battery, timestamp.
- Timestamp-ordered location history and last-known positions.
- Circular places/geofences with arrival and departure events when reported GPS accuracy is sufficient.
- Responsive dark/light GoreeCloud UI dashboard with coordinate-map view, route overlays, device cards, timeline, places, and recent events.
- Explicit browser location capture (requires user permission + HTTPS or localhost).
- Owner-scoped *streaming, complete* GeoJSON and GPX exports, cursor-paginated history, individual deletion, confirmed per-device history erasure, and device/place deletion.
- Zero-dependency static browser UI and no mandatory external map requests.
- Optional relative-path tile URL pointing to a **separately hosted** private tile server.
- Docker/Compose deployment example bound to 127.0.0.1; automated API regression tests and CI configuration.

**Not implemented:** Native Android/iOS/Linux clients; always-on mobile background GPS collection; family circles and location sharing; advanced geofences; telemetry/fleet protocol adapters; driving risk analysis; offline mobile capture; pet/item integrations; email/push/SMS alerts; crash/SOS response; professional emergency dispatch; local map tile server; additional import formats and full migration utilities beyond the initial CSV endpoint; identity/financial assistance. See [features and milestones](docs/PRODUCT_SPEC.md) and [status](docs/STATUS.md).

## Quick start (Python 3.11+)

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
gclocation create-admin --username owner
gclocation serve
```

Open **http://127.0.0.1:8123**. Account setup prompts for a password of at least 14 characters, without putting credentials in shell history. No account is ever created automatically.

Location data is stored by default in `~/.local/share/goreecloud-location/location.db`. Set `GC_LOCATION_DB` to override that path. Use the built-in online backup command to capture a consistent snapshot, including committed WAL transactions; do not publish your database or tokens.

## Docker Compose (development / behind reverse proxy)

```sh
docker compose build
docker compose run --rm location gclocation create-admin --username owner
docker compose up -d
```

The example publishes only to host loopback `127.0.0.1:8123`. To access from another device, configure an **authenticated HTTPS reverse proxy** and restrict network exposure appropriately. Do not simply bind the public Internet to the service without TLS, rate limiting, firewalling, and reviewing [security](docs/SECURITY.md).

If a local map tile service is already available, set `GC_TILE_TEMPLATE=/tiles/{z}/{x}/{y}.png` and proxy `/tiles/` to that service on the same origin. GoreeCloud Location does **not** ship a tile server or silently request a third-party map provider. Without tiles, the dashboard displays a clearly labeled coordinate map.

## Record a position

1. Register a device on the **Devices** screen. **Copy the device ingestion token once**; it cannot be retrieved later.
2. Sign in to the dashboard, select the device, and choose **Capture my location** (geolocation permission and secure context required).
3. Or submit GPS positions from a compatible client:

```sh
curl -X POST 'http://127.0.0.1:8123/api/ingest/DEVICE_ID' \
  -H 'Authorization: Bearer DEVICE_INGEST_TOKEN' \
  -H 'Content-Type: application/json' \
  --data '{"latitude":35.96,"longitude":-83.92,"accuracy_m":12}'
```

The example coordinates are illustrative, not real user data. An ingestion token can only upload positions for its single associated device; it cannot read private history. Rotate the token using the **Rotate key** action in Devices, or POST `/api/devices/{id}/rotate-token`. Old tokens become invalid immediately and history is preserved; update your tracking client with the new key.

On **Devices**, **Erase history** permanently deletes the selected device's GPS points and geofence events while retaining its registration and ingestion token. The UI requires typing ERASE to confirm. Earlier backups and downloaded exports remain separate copies; handle those under your data-retention policy.

In **History**, select one device, choose a UTF-8 CSV file, and choose **Import CSV**. The CSV must contain latitude, longitude and timezone-aware recorded_at columns; optional columns are accuracy_m, altitude_m, speed_mps, heading_deg and battery_percent. A single import allows at most 5,000 rows and 2 MiB of data. All rows are checked before writing, and duplicate device/timestamp/coordinate points are skipped. Importing does not contact external providers.

The authenticated API accepts sessions through `Authorization: Bearer SESSION_TOKEN` and provides:
`/api/me`, `/api/summary`, `/api/devices`, `/api/locations`, `/api/places`, `/api/events`, `/api/export/gpx?device_id=N`, and `/api/export/geojson?device_id=N`. Exports stream the entire selected device history without a fixed point cap; use `/api/locations/page` for cursor-based history pagination. See [API reference](docs/API.md).

## Quality and scope

```sh
pip install -e '.[test]'
pytest
node --check src/goreecloud_location/static/app.js
```

This repository deliberately does not bundle proprietary Life360 code, proprietary tracking networks, commercial emergency/insurance features, or unreviewed GPS protocol implementations. Third-party integrations, if introduced, must respect licensing, user consent, and product safety requirements.

The interface follows the intent of [GoreeCloud UI](https://github.com/GoreeCloud/gc-ui)'s current design language; **pixel-perfect or cross-device visual acceptance has not been verified**. Details: [architecture](docs/ARCHITECTURE.md), [security](docs/SECURITY.md), [product specification](docs/PRODUCT_SPEC.md), and [implementation status](docs/STATUS.md).

License: [MIT](LICENSE). Copyright © 2026 GoreeCloud.

### Consistent local backup

Stop using raw file copies while SQLite is active. Instead, run:

```sh
gclocation backup --destination ~/private-location-2026-11-03.sqlite
```

The destination directory must already exist and the backup file must be new; existing files are never overwritten. The output uses owner-only file permissions. Encrypt and safeguard backups separately. A restore command and end-to-end disaster recovery verification are not yet available.
