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
| DELETE | `/api/devices/{id}` | Owner session | Delete device and all its positions/events |
| GET | `/api/locations?device_id=N&limit=300` | User session | Latest positions (max 1,000); optional owner device |
| POST | `/api/locations` | User session | Record point for owner device |
| DELETE | `/api/locations/{id}` | Owner session | Delete individual point |
| POST | `/api/ingest/{device_id}` | Device token | Upload point only, never read |
| GET | `/api/places` | User session | Owner circular geofences |
| POST | `/api/places` | User session | Create circular geofence |
| DELETE | `/api/places/{id}` | Owner session | Delete geofence and its events |
| GET | `/api/events?limit=40` | User session | Geofence transition log |
| GET | `/api/export/geojson?device_id=N` | Owner session | GeoJSON export, capped 10,000 |
| GET | `/api/export/gpx?device_id=N` | Owner session | GPX export, capped 10,000 |

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

The returned `ingest_token` is only shown once. This token has **write-only scope for the one registered device** and is not a user session token.

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

The GPX endpoint returns `X-GoreeCloud-Export-Truncated: true` when more than 10,000 positions exist. The GeoJSON endpoint returns `truncated: true` in the response body. Exports are intentionally **not** represented as complete when truncated.

All example coordinates are fictitious documentation data.
