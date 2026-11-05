# GPX Track Import — GoreeCloud Location

**Development preview (5 November 2026).** This API imports historical track points from an existing GPX 1.0 or GPX 1.1 file into a device owned by the signed-in account. It does not connect to remote map providers or automatically share location histories.

## Import through the browser

Open **History**, select a specific registered device, choose a `.gpx` file and select **Import GPX**. The History page reports the number of imported and skipped duplicate points. This action changes only the chosen account-owned device's live SQLite history. Create an independently protected backup first if you may need to reverse the change.

## HTTP endpoint

`POST /api/devices/{device_id}/import/gpx`

- Authentication: account's valid bearer session. A GPS device's write-only ingestion token is **not** authorized to import historical files.
- Content-Type: `application/gpx+xml`, `application/xml` or `text/xml`. Send raw XML, not a multipart form.
- Maximum raw request body: **2 MiB**; maximum track points: **5,000**.
- Source: **GPX 1.0 and 1.1** documents using the official Topografix XML namespace. Only `trk / trkseg / trkpt` elements are imported. Waypoints, route points, photos, extension fields, place names and remote links are not imported.
- Every track point must have valid WGS84 `lat`, `lon` attributes and a timezone-aware ISO 8601 `time` child. Optional `ele` is mapped to altitude in meters. Invalid, absent, naive or future timestamps cause the **entire** import to fail.
- The XML parser uses `defusedxml` with DTD, entity and external references forbidden; malformed or unsafe XML is rejected. No remote URL or file resolution is performed.
- The server parses and validates the complete bounded file before beginning a write transaction. Validated points are sorted by timestamp; identical device/timestamp/latitude/longitude points are skipped using the existing CSV importer’s best-effort duplicate logic.
- Historical points already superseded by newer device observations do not rewrite the current geofence state. An eligible chronological transition still follows the device’s normal accuracy rules; plain GPX does not include the accuracy needed to generate geofence events by default.
- Success response: HTTP **201** with `device_id`, `imported`, `skipped_duplicates`, and `geofence_events` counts. Existing device registration and key remain unchanged.

## Synthetic local API example

```sh
curl --request POST 'http://127.0.0.1:8123/api/devices/1/import/gpx' \
  --header 'Authorization: Bearer YOUR_ACCOUNT_SESSION_TOKEN' \
  --header 'Content-Type: application/gpx+xml' \
  --data-binary '@synthetic-route.gpx'
```

The example is suitable only for a private loopback development service. Keep account/session tokens out of shell history, public scripts and logs. Do not ingest other people’s location histories without permission.

## Limitations and acceptance

This import is **not** a full GPX editing suite, cloud migration service, FIT/TCX/KML importer or GPS hardware adapter. Input metadata other than track point positions/elevation/time is discarded. The 2 MiB / 5,000 point caps deliberately bound server resource use; larger archives require a future reviewed, resumable ingestion design. Deleting live records does not erase copies in backups, exports or offline caches.

The API tests cover account isolation, import/export round trips, chronological deduplication, invalid track points, missing timestamps, unsafe DTD/entities, file limits and timeouts. Browser tests exercise synthetic GPX upload at three viewport sizes. **Real GPS archive compatibility, load testing, production TLS and usability/accessibility acceptance remain separate gates.**

References: [GPX 1.1 schema](https://www.topografix.com/GPX/1/1/), [defusedxml documentation](https://pypi.org/project/defusedxml/), [API reference](API.md), [security](SECURITY.md), [implementation status](STATUS.md).
