# OwnTracks HTTP Ingestion — GoreeCloud Location

**Development preview (5 November 2026).** This is an original, server-side adapter for a subset of the OwnTracks HTTP protocol. It is not an OwnTracks app, recorder replacement, MQTT broker, production mobile-tracking deployment, or completed end-to-end Android/iOS device validation.

## Configuration

1. Create a device using the authenticated GoreeCloud Location API or **Devices** in the web dashboard. Save its **one-time** ingestion token. Account session tokens and account passwords are never used for tracker ingestion.
2. In your OwnTracks Android or iOS application, select **HTTP** connection mode.
3. Set the endpoint to `https://YOUR-PRIVATE-HOST/api/ingest/owntracks/DEVICE_ID`. This service's own development CLI binds to loopback; a publicly reachable endpoint requires independent TLS/reverse-proxy and authentication review. Avoid exposing this development preview to the internet.
4. Configure HTTP **Basic** authentication: username `owntracks`, password = the one-time **device ingestion token**. Keep the password out of public URLs, screenshots, scripts, logs and issue reports.
5. Use the normal OwnTracks JSON location payload; the server replies with HTTP **200** and `[]` when it accepts a valid location update or recognized housekeeping message.

### Local synthetic example

The command below prompts for the private device token instead of embedding it in shell history:

```sh
curl --user owntracks \
  --request POST 'http://127.0.0.1:8123/api/ingest/owntracks/1' \
  --header 'Content-Type: application/json' \
  --data '{"_type":"location","lat":35.95,"lon":-83.92,"tst":1790856000,"acc":8,"vel":18,"batt":82}'
```

The example is for a **loopback-only** development instance with synthetic GPS coordinates. On a remote device, use correctly validated **HTTPS**, not plain HTTP. A 2xx response does not guarantee delivery of alerts to other users.

## Supported mapping

| OwnTracks field | Stored GoreeCloud field | Notes |
| --- | --- | --- |
| `_type=location` | location point | Required; other recognized non-location messages are ignored |
| `lat`, `lon` | latitude, longitude | Required, numeric WGS84 coordinates |
| `tst` | recorded_at | Required strict integer Unix seconds, normalized to UTC |
| `acc` | accuracy_m | Optional; geofence updates require adequate accuracy |
| `alt` | altitude_m | Optional |
| `vel` | speed_mps | Optional km/h divided by 3.6 |
| `cog` | heading_deg | Optional |
| `batt` | battery_percent | Optional integer |

Other common OwnTracks attributes such as `topic`, `tid`, `t`, `conn`, Wi-Fi names and network identifiers are **not retained** in point records. The endpoint identifies the target tracker **only through the URL device ID and matching private token**, not through attacker-supplied topic or header labels.

## Protocol and privacy boundaries

- Body limit: **16 KiB**. Nonempty bodies must be UTF-8 JSON with `Content-Type: application/json`.
- Authentication: HTTP Basic with username `owntracks` and the registered device's write-only token. Login sessions, missing credentials, wrong device tokens, or another device's token cannot be used.
- Validation: finite GPS values, field ranges, strict integer timestamp, and no timestamps more than five minutes into the future. Invalid locations receive 422; oversized bodies receive 413; wrong content types receive 415.
- Recognized housekeeping, waypoint, and client-reported transition messages receive `[]` **without writing history or trusting client transition events**. Unknown message types and encrypted OwnTracks payloads are rejected; no remote commands or friend locations are returned.
- Empty bodies are acknowledged after successful device authentication, following OwnTracks HTTP conventions.
- The server's normal geofence logic applies to eligible, accurate, strictly newer positions under a SQLite write transaction. A conflicting equal-time fix is retained in history but does not create a false arrival or departure event.
- Device key rotation immediately invalidates the old OwnTracks Basic password. Device tokens cannot read or export location history.
- **No MQTT support, end-to-end OwnTracks app validation, client-side encryption support, native background tracking implementation, session-less public ingestion, map-provider requests, or professional emergency response** is claimed.

## References

- [OwnTracks HTTP specification](https://owntracks.org/booklet/tech/http/)
- [OwnTracks JSON location payload](https://owntracks.org/booklet/tech/json/)
- [GoreeCloud Location API](API.md)
- [Security and privacy boundaries](SECURITY.md)
