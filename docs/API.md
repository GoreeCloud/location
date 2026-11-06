# API Reference — GoreeCloud Location 0.1.0

All routes below use JSON unless otherwise noted. There are **no public location data endpoints**. `Authorization: Bearer SESSION_TOKEN` authenticates all read/write operations except a dedicated device ingestion endpoint.

| Method | Route | Access | Function |
| --- | --- | --- | --- |
| GET | `/api/health` | Public | Non-sensitive service status |
| GET | `/api/config` | Public | Local map tile configuration only |
| POST | `/api/auth/login` | Username/password | Create 8-hour user session |
| POST | `/api/auth/logout` | User session | Revoke one session |
| POST | `/api/auth/logout-all` | User session | Revoke every existing login session owned by this account; device keys unaffected |
| GET | `/api/me` | User session | Current user |
| POST | `/api/circles` | User session | Create private named circle (no location sharing) |
| GET | `/api/circles` | User session | List circles owned or explicitly accepted |
| POST | `/api/circle-invite-code` | User session | Generate one-time 30-minute recipient code; hashed at rest |
| POST | `/api/circles/{id}/invite` | Circle owner | Consume recipient code; pending 7-day invitation |
| GET | `/api/circle-invitations` | User session | Only invitations addressed to current account |
| POST | `/api/circle-invitations/{id}/respond` | Invitee session | Explicitly accept or decline |
| GET | `/api/circles/{id}/members` | Circle owner/accepted member | View authorized member identities |
| DELETE | `/api/circles/{id}/members/{account_id}` | Circle owner | Revoke member/invitation |
| DELETE | `/api/circles/{id}/membership` | Accepted member | Leave a circle |
| DELETE | `/api/circles/{id}` | Circle owner | Remove a circle and memberships |
| GET | `/api/summary` | User session | Counts of devices, points, places, events |
| GET | `/api/devices` | User session | Owner devices with last positions |
| POST | `/api/devices` | User session | Create device; receive ingestion token once |
| PUT | `/api/devices/{id}/collection` | Owner session | Pause or resume new GPS collection without erasing history |
| GET | `/api/privacy/collection-activity?device_id=N&limit=50` | User session | Recent owner-only pause/resume actions (up to 100) without GPS positions |
| POST | `/api/devices/{id}/rotate-token` | Owner session | Issue new device upload token, revoke previous token, preserve history |
| DELETE | `/api/devices/{id}/history` | Owner session | Delete device points, events and fence state; retain device/key |
| DELETE | `/api/devices/{id}` | Owner session | Delete device and all its positions/events |
| GET | `/api/locations?device_id=N&limit=300` | User session | Latest positions (max 1,000); backwards-compatible list |
| GET | `/api/locations/page?device_id=N&limit=100&cursor=...` | User session | Keyset history page with `items`, `has_more`, and `next_cursor` |
| POST | `/api/locations` | User session | Record point for owner device |
| POST | `/api/devices/{id}/import/csv` | Owner session | Raw UTF-8 CSV import, max 2 MiB / 5,000 data rows, atomic validation |
| POST | `/api/devices/{id}/import/gpx` | Owner session | Defused GPX 1.0/1.1 timestamped track import, max 2 MiB / 5,000 points |
| POST | `/api/devices/{id}/import/geojson` | Owner session | Bounded owner-only GeoJSON FeatureCollection Point import, max 2 MiB / 5,000 features |
| DELETE | `/api/locations/{id}` | Owner session | Delete point and matching timestamp events; reset fence state |
| POST | `/api/ingest/{device_id}` | Device token | Upload point only, never read |
| POST | `/api/ingest/owntracks/{device_id}` | HTTP Basic device key | OwnTracks JSON location ingestion; always returns `[]` on 200; never reads history |
| GET | `/api/places` | User session | Owner circular geofences |
| POST | `/api/places` | User session | Create circular geofence |
| DELETE | `/api/places/{id}` | Owner session | Delete geofence and its events |
| GET | `/api/events?limit=40` | User session | Geofence transition log |
| GET | `/api/retention/preview?older_than_days=N` | User session | Non-destructive owner-scoped count preview |
| POST | `/api/retention/purge` | User session | Explicit confirmed, preview-count-matched purge of old account history |
| GET | `/api/export/geojson?device_id=N` | Owner session | Complete streaming GeoJSON export |
| GET | `/api/export/gpx?device_id=N` | Owner session | Complete streaming GPX export |

## Authentication

```sh
curl -X POST http://127.0.0.1:8123/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"owner","password":"YOUR_PASSWORD"}'
```

The response contains `access_token`, `expires_at`, and account metadata. Store it securely; never paste it into a repository, public issue, log, or URL.

## Register a device

```sh
curl -X POST http://127.0.0.1:8123/api/devices \
  -H 'Authorization: Bearer SESSION_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Personal phone","kind":"person"}'
```

Valid kinds: `person`, `vehicle`, `pet`, `item`, `asset`, `other`.

The returned `ingest_token` is only shown once. This token has **write-only scope for the one registered device** and is not a user session token. `POST /api/devices/{id}/rotate-token` immediately invalidates the previous ingestion token without deleting historical points; its response includes a one-time replacement.

## Upload location

```sh
curl -X POST http://127.0.0.1:8123/api/ingest/1 \
  -H 'Authorization: Bearer DEVICE_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"latitude":35.95,"longitude":-83.92,"accuracy_m":10,"battery_percent":88}'
```

`recorded_at` is an optional ISO 8601 timestamp **with timezone offset**; future timestamps beyond five minutes are rejected. Accepted fields include latitude (-90..90), longitude (-180..180), accuracy_m (0..10000), altitude_m, speed_mps, heading_deg, and battery_percent (0..100). Unknown fields are rejected.

## OwnTracks HTTP location clients

Configure the OwnTracks app in HTTP mode with URL `https://PRIVATE-HOST/api/ingest/owntracks/DEVICE_ID`, Basic username `owntracks`, and Basic password equal to that registered device's private ingestion token. Native location JSON uses `_type=location`, `lat`, `lon` and integer epoch `tst`; optional fields `acc`, `alt`, `vel` (km/h), `cog`, `batt` are mapped and validated. The response on success is JSON `[]`. Other recognized non-location messages are acknowledged without persisting or applying their untrusted transitions. Payloads are limited to 16 KiB, and encrypted messages and MQTT are not supported. [Detailed setup](OWNTRACKS_HTTP.md).

## Create a place

```json
{"name":"Home","latitude":35.95,"longitude":-83.92,"radius_m":150}
```

Only circular geofences exist today. Geofence transitions require sufficiently accurate position reports, and initial state does not produce an artificial arrival.

## Export limits

GPX and GeoJSON exports stream **every** point for the authenticated owner's requested device. The old 10,000-record cutoff and truncation indicators have been removed. Exports are not resumable in this development preview; keep backup copies of large downloads. History pagination uses an opaque `next_cursor` returned by `/api/locations/page`; supply it as `cursor` for the next page, keep the same device filter, and do not use the cursor as a permission token.

All example coordinates are fictitious documentation data.

## Initial CSV import

Send raw UTF-8 bytes with Content-Type: text/csv and a valid owner session to POST /api/devices/{id}/import/csv. Do not use a multipart upload for this endpoint. Required columns: latitude, longitude, recorded_at. Optional columns: accuracy_m, altitude_m, speed_mps, heading_deg, battery_percent. Other columns are rejected. Every recorded_at must have a timezone offset, and coordinates and telemetry use the same validation bounds as the single-point API.

A successful response provides imported, skipped_duplicates and geofence_events counts. The operation first validates the entire file (maximum 2 MiB, 5,000 records) then writes within one transaction; a malformed file does not partially import. Rows are sorted by timestamp before processing. Duplicate device/timestamp/latitude/longitude combinations are skipped as a best-effort deduplication strategy; concurrent ingestion and large migrations require additional controls.

CSV, GPX and GeoJSON Point imports are available as bounded, account-scoped development utilities. Google Takeout, FIT/TCX/KML, other provider-specific archives, and large resumable imports are not implemented. See [GPX import](GPX_IMPORT.md).


## Manual history retention preview and purge

GET /api/retention/preview?older_than_days=90 returns read-only counts of the current user's positions, place events and affected devices older than the server's UTC cutoff. Days must be a whole number between 1 and 36,500. Preview alone does not delete records.

A subsequent POST /api/retention/purge requires JSON:

```json
{
  "older_than_days": 90,
  "expected_points": 100,
  "expected_events": 4,
  "confirmation": "DELETE_OLD_HISTORY"
}
```

Counts must match the server's new transactional check; otherwise HTTP 409 is returned without deletion. The API deletes eligible points and events only for the authenticated account, resets affected geofence state and preserves newer history and device registrations. This is manual logical deletion, not an automatic retention schedule or secure wiping of exports, SQLite remnants, logs, offline devices or backups.

## Account-wide session revocation

Send an authenticated POST to `/api/auth/logout-all` to revoke all currently existing login sessions for the signed-in account, including the token making the request. The response is HTTP 204. Other accounts remain signed in. Registered GPS device ingestion keys use a separate credential scope and are **not** rotated or revoked by this action; rotate device keys separately when compromised. The Settings interface requires an explicit confirmation before calling this endpoint. New sign-ins after revocation are permitted and create fresh sessions. This is not multi-factor authentication or a distributed identity provider integration.

## GPX track import

POST `/api/devices/{id}/import/gpx` with an account bearer token and raw GPX XML (`Content-Type: application/gpx+xml`), not a multipart file. The importer accepts GPX 1.0/1.1 track points with explicit timezone-aware timestamps and optional elevation, rejects unsafe XML through `defusedxml`, bounds body size to 2 MiB and track count to 5,000, validates all points before writing, and shares the CSV import's duplicate/transaction logic. Returns 201 plus `imported`, `skipped_duplicates`, and `geofence_events`. Waypoints, routes, extensions, contacts and user-defined geofence events are never imported. [Setup and boundaries](GPX_IMPORT.md).

## GeoJSON Point history import

POST `/api/devices/{id}/import/geojson` with the account bearer session and raw GeoJSON (`Content-Type: application/geo+json`). Accepts RFC 7946 `FeatureCollection` containing timestamped `Point` features with longitude/latitude coordinates, optional altitude and only supported GPS properties. Rejects malformed/non-finite JSON, unsupported geometries, absent timezone-aware timestamps and oversized files before writing. Limits: 2 MiB and 5,000 features, shared duplicate/transaction semantics with CSV and GPX. Additional features/metadata are ignored, never used for account sharing or saved places. [Configuration and limitations](GEOJSON_IMPORT.md).

## Per-device collection pause

`PUT /api/devices/{id}/collection` requires an account bearer token and JSON `{"paused":true}` or `{"paused":false}`. Only a strict Boolean is accepted. The owner-specific response provides `device_id`, `tracking_paused`, and `tracking_resumed_at`; the device listing includes the same state. While paused, `/api/locations`, device bearer ingestion, OwnTracks location uploads and all owner archive import routes return HTTP 409 without adding points. Resuming sets a UTC cutoff that rejects queued live locations recorded before or at the cutoff, while allowing deliberately imported older history after resuming. Resumption resets the geofence baseline, not existing events. Tokens are retained and exports/erasure remain available. [Setup and caveats](COLLECTION_CONTROL.md).

## Browsing history beyond the recent map

The History dashboard loads `GET /api/locations/page?limit=100` for the initial 100 account-owned positions, and follows its `next_cursor` only after the user selects **Load older positions**. With a `device_id` filter, all pages remain restricted to that account-owned device. Selecting a different device resets the cursor. The endpoint returns `items`, `has_more` and `next_cursor`; a cursor is not a credential and the server independently authorizes every request. The overview map uses a separate bounded request for recent positions, while exports can stream complete owned histories.

## Owner-only collection activity

`GET /api/privacy/collection-activity` returns up to 50 most recent collection setting changes, with an optional owned `device_id` and a `limit` of 1–100. Fields are `id`, `device_id`, `device_name`, `action` and `changed_at` (server UTC). The endpoint requires a user session; device upload keys cannot read it. The database keeps at most 100 changes per device and cascades them on device deletion, while ordinary GPS-history clearing leaves them intact. [Privacy behavior](COLLECTION_CONTROL.md).

## Invitation-only circles (metadata, not GPS sharing)

All circle endpoints require an authenticated account session. An intended invitee must actively generate a short-lived, one-time code and communicate it to a circle owner; the owner uses that code to invite and the recipient must separately accept. Invitations expire after 7 days. Circle metadata access requires ownership or accepted membership; owners can revoke and members can leave. **No endpoint grants cross-account GPS/history/device access to a member.** No public directory, anonymous links or external messages. [Workflow and privacy boundaries](CIRCLES.md).
