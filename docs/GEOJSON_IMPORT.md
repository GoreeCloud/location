# GeoJSON Point History Import — GoreeCloud Location

**Development preview (5 November 2026).** GoreeCloud Location imports bounded RFC 7946 GeoJSON `FeatureCollection` documents into a single existing account-owned device. It does **not** import polygons, lines, saved places, network resources, arbitrary user profiles, or shared/public location feeds.

## Import in History

Sign in, open **History**, select a registered device, choose a `.geojson` file with the shared **Import file** chooser, and submit. The same import control accepts `.csv` and `.gpx` files, selecting the appropriate server validator from the filename extension. No file is uploaded until the user explicitly selects Import.

## API

`POST /api/devices/{device_id}/import/geojson`

- Authorization: authenticated account bearer token. A device's write-only tracking key cannot read or import archives. Target device ownership is verified before reading the body and inside the write transaction.
- Content-Type: `application/geo+json` or `application/json`; raw JSON body (not multipart form).
- Maximum body: **2 MiB**, maximum **5,000** features; entirely validated before any database insert.
- Root: `{"type":"FeatureCollection","features":[...]}`; each feature must have `"type":"Feature"`, a `"Point"` geometry, `coordinates` of two or three finite numbers in **longitude, latitude** order, and an explicit timezone-aware `properties.recorded_at` ISO 8601 timestamp. A third coordinate is optional altitude in meters.
- Recognized properties: `recorded_at`, `accuracy_m`, `altitude_m`, `speed_mps`, `heading_deg`, and `battery_percent`. Other properties—including identifiers, Wi-Fi metadata, titles, URLs and profile details—are **ignored rather than retained**.
- Timestamps more than five minutes in the future, invalid coordinates/telemetry and unsupported geometry types fail validation of the **entire** file.
- Validated points are sorted chronologically and written through the same SQLite transaction, duplicate detection, ownership checks and geofence guards used for CSV and GPX imports.
- HTTP 201 returns `device_id`, `imported`, `skipped_duplicates` and `geofence_events`; device registration and private key are unchanged.

### Synthetic example

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [-83.92, 35.95]},
      "properties": {"recorded_at": "2026-10-01T10:00:00Z", "accuracy_m": 8}
    }
  ]
}
```

An owner may import a GeoJSON file previously produced by GoreeCloud Location's own `GET /api/export/geojson?device_id=N`, selecting a different registered device to perform a round trip.

## Boundaries and safety

No remote URLs, script fragments, tracking network identifiers, geofence configuration or profile information are fetched or persisted from the imported metadata. Invalid or malformed JSON produces an error without partial history writes. Imported points do not prove someone was physically present; geofence changes are subject to the same accuracy and chronological constraints as live GPS ingestion. Backups and previously exported copies are not changed.

This is a bounded **Point** importer, not a general GeoJSON geometry processor, map-editor import, arbitrary schema translator, automatic migration workflow, or a certified privacy/safety service. Independent hostile-input fuzzing, production load, physical-device and operator HTTPS acceptance remain outstanding.

References: [RFC 7946 GeoJSON](https://www.rfc-editor.org/rfc/rfc7946), [API](API.md), [GPX import](GPX_IMPORT.md), [security](SECURITY.md), [status](STATUS.md).
