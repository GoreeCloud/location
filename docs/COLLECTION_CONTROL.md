# Per-device location collection controls

**Development preview, November 5, 2026.** This feature is a server-side privacy control for registered trackers. It is not a guarantee that physical GPS hardware, OwnTracks, or other clients stop recording coordinates locally.

## Owner control

Open **Devices** and choose **Pause collection** for an individual registered device. Confirm the action. GoreeCloud Location rejects new reports for that device until the owner explicitly chooses **Resume collection**. The device registration, upload token, previously stored GPS history, exports, and owner-created places remain intact.

The server enforces the setting across account-authenticated GPS capture, device-token ingestion, OwnTracks HTTP location reports, and the CSV/GPX/GeoJSON history import endpoints. While paused, API uploads return HTTP **409** without inserting GPS positions or generating geofence events. The dashboard also excludes paused trackers from the browser GPS capture selector.

After resuming, the server records a UTC cutoff. Live reports whose **recorded_at** timestamp is at or before that cutoff are rejected, to prevent queued fixes from silently filling a paused interval. The device's existing geofence state is reset so that the first new report establishes a baseline; it does not claim that the user crossed a boundary during the pause.

An owner may deliberately import historical CSV, GPX, or GeoJSON data **after** resuming. This is an explicit owner action, distinct from buffered live tracking. Archived points recorded before the resume cutoff are retained but cannot generate new arrival/departure notifications. Archive uploads remain blocked during a pause.

## API

`PUT /api/devices/{device_id}/collection` with a valid owner session bearer token and JSON:

```json
{"paused": true}
```

Use `{"paused": false}` to resume. Responses include `device_id`, `tracking_paused`, and `tracking_resumed_at`. Repeated requests with the existing state are idempotent. The owned `GET /api/devices` listing also includes the state and cutoff.

Only the device owner may control this endpoint. Unauthorized sessions and device ingestion keys are rejected, and another account's device is not disclosed. No account-to-account sharing is added.

## Security and safety limits

- **Default:** Newly registered and existing devices remain collection-enabled until explicitly paused, preserving existing behavior. No one is automatically enrolled in location sharing by this feature.
- **Stored history:** Pausing does **not** erase existing GPS records, geofence events, backups, exports, downloaded files, or offline caches. Use separate deliberate erasure controls when needed.
- **Client storage:** An OwnTracks client or physical tracker may keep local GPS history or continue making requests; the server rejects new collection while paused. Inspect device-side storage and permissions separately.
- **Untrusted timestamps:** This cutoff is based on client-supplied recorded timestamps, so a malicious or misconfigured client can supply false times or omit optional timestamps. It is **not** a cryptographic proof that a fix was collected after resuming.
- **Geofence semantics:** Resuming clears live fence state, not historic geofence events. The first accurate new fix re-establishes the baseline. There is no guaranteed real-time safety notification or professional emergency response.
- **Transactions:** On the existing single-node SQLite database, changes and ingestion run under writer transactions. Multi-node behavior, load/penetration testing, external tracker clients, and production TLS have not been independently accepted.
- **Database upgrade:** Existing SQLite devices acquire additive `tracking_paused` and `tracking_resumed_at` columns. Historical points, device identities and tracker credentials remain unchanged. Back up private data before any production-like software upgrade.

See [Security](SECURITY.md), [API](API.md), [Architecture](ARCHITECTURE.md), and [Implementation status](STATUS.md).

## Owner-only collection activity

Each actual change between paused and resumed records an action and server UTC timestamp in the same SQLite transaction as the collection setting. Repeating the same request does not create a duplicate. The service keeps at most **100** recent changes per registered device and shows the newest **50** account-owned records in **Privacy**. An authenticated owner can query `GET /api/privacy/collection-activity?limit=50` with optional `device_id`; limits range from 1 to 100. An ingestion-only token cannot read the records, and the SQL query verifies account ownership on each read.

The table stores only a device reference, action (`paused` or `resumed`) and server timestamp. Device names are joined from the owner's current device listing at read time; no GPS coordinates, network addresses, user agents, or tokens are written to this activity table. Reverse proxies may have separate access logs under their own policies. Clearing GPS history does **not** clear these privacy-control decisions; deleting a device removes its activity through database foreign-key cascade. Older entries are pruned on later setting changes; no scheduler or offsite replication is implied. These records are not forensic-proof or tamper-evident logs.
