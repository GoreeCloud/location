# API Reference — GoreeCloud Location 0.1.0

All routes below use JSON unless otherwise noted. There are **no public location data endpoints**. `Authorization: Bearer SESSION_TOKEN` authenticates all read/write operations except a dedicated device ingestion endpoint.

| Method | Route | Access | Function |
| --- | --- | --- | --- |
| GET | `/api/health` | Public | Non-sensitive service status |
| GET | `/api/config` | Public | Local map tile configuration only |
| POST | `/api/auth/login` | Username/password | Create 8-hour user session |
| POST | `/api/auth/logout` | User session | Revoke session |
| GET | `/api/me` | User session | Current user |
| GET | `/api/summary` | User session | Counts of devices, points, places, events |
| GET | `/api/devices` | User session | Owner devices with last positions |
| POST | `/api/devices` | User session | Create device; receive ingestion token once |
| POST | `/api/devices/{id}/rotate-token` | Owner session | Issue new device upload token, revoke previous token, preserve history |
| DELETE | `/api/devices/{id}/history` | Owner session | Delete device points, events and fence state; retain device/key |
| DELETE | `/api/devices/{id}` | Owner session | Delete device and all its positions/events |
| GET | `/api/locations?device_id=N&limit=300` | User session | Latest positions (max 1,000); backwards-compatible list |
| GET | `/api/locations/page?device_id=N&limit=100&cursor=...` | User session | Keyset history page with `items`, `has_more`, and `next_cursor` |
| POST | `/api/locations` | User session | Record point for owner device |
| POST | `/api/devices/{id}/import/csv` | Owner session | Raw UTF-8 CSV import, max 2 MiB / 5,000 data rows, atomic validation |
| DELETE | `/api/locations/{id}` | Owner session | Delete point and matching timestamp events; reset fence state |
| POST | `/api/ingest/{device_id}` | Device token | Upload point only, never read |
| GET | `/api/places` | User session | Owner circular geofences |
| POST | `/api/places` | User session | Create circular geofence |
| DELETE | `/api/places/{id}` | Owner session | Delete geofence and its events |
| GET | `/api/events?limit=40` | User session | Geofence transition log |
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

This endpoint is an initial CSV-only utility. Google Takeout, GPX and other provider-specific imports are not implemented.
