# Security and Privacy — GoreeCloud Location

**This is a development preview. Do not expose it as a production location service without an independent security review.**

## Sensitive data

Precise location history reveals home/work routines and sensitive activities. Avoid collecting any person's positions without their informed consent. Do not capture or publish real GPS traces, password secrets, API tokens, or database snapshots in this public repository. Accounts and devices are isolated by ownership checks. The API intentionally has no public signup or public location-sharing endpoints.

## Existing controls

- scrypt password hashing with 16-byte per-user salt; 14-character minimum password.
- Random 256-bit-class session and device tokens; only SHA-256 digests stored in SQLite.
- Eight-hour sessions, explicit logout revocation, 20-session per-account cap, bounded username/peer/global login attempt budgets, and device-specific token rotation without deleting history.
- Separate owner-session and device-upload token scopes.
- Pydantic validation, strict request schemas, bounded GPS numeric fields and timestamp checks.
- Private-by-default API endpoints, account-scoped database queries.
- Security response headers: CSP, no-sniff, no-referrer, deny framing, no-store API caching.
- No embedded CDN scripts, analytics, advertising, remote geolocation calls, or default tile requests.
- Docker Compose loopback-only host binding, non-root service user, dropped capabilities.
- No first-run default credentials or network-accessible bootstrap user creation.

## Not yet hardened for Internet exposure

- Sessions are held in browser sessionStorage (XSS-sensitive); do not treat them as persistent MFA sessions.
- Rate limiting is process-local only: 5 attempts/username, 40 attempts/network peer and 300 attempts/service within 5 minutes. Budgets count successful logins and have an in-memory cap. Proxy configuration and shared multi-instance rate limits are **not** implemented; enforce TLS and independent reverse-proxy protection.
- No password reset, MFA, OIDC integration, IP allow-listing, distributed account lockout or user-session token rotation. Device ingestion token rotation exists; logging in beyond 20 active sessions revokes the account's oldest sessions.
- No independent audit of proxy headers or shared tenant safety at scale.
- No automated at-rest encryption. SQLite DB and manual snapshot files use mode 0600; use OS volume encryption and protected backups.
- Database schemas have not yet been migrated under release controls.
- No penetration test, native mobile client audit, or production load/recovery validation. Local synthetic-fixture recovery testing does not certify disaster recovery.
- The API may accept historical GPS points; never treat API-reported positions as proof of a person's physical presence.

## Deployment checklist

1. Run behind an HTTPS reverse proxy with strong TLS settings and a firewall.
2. Restrict network access to trusted users or a private VPN.
3. Create the first account locally using `gclocation create-admin`.
4. Configure unique credentials; protect device tokens; do not commit secrets.
5. Keep `GC_LOCATION_DB`, SQLite WAL/SHM, service logs, and backups inaccessible to untrusted users.
6. Limit storage retention and obtain informed consent before tracking others.
7. Review dependency provenance, GitHub Actions, vulnerability reports and release artifacts.
8. Use consistent encrypted backups; restore-test before calling a deployment reliable.
9. Verify geofences and emergency notification paths independently before relying on them.
10. Do not advertise professional emergency response as integrated until contractual and runtime proof exists.

## Threat model

- **Unauthorized tracking:** require user consent, explicit device enrollment, and access isolation; no covert discovery.
- **Credential compromise:** short sessions, strong password hashing, user-session logout and device-token rotation without losing history; MFA and user-session rotation planned.
- **Cross-account access:** test positive/negative ownership checks across every new endpoint.
- **Location exfiltration:** avoid third-party map requests by default; opt in only to owner-controlled tile services.
- **Web injection:** never use untrusted values as markup; use textContent, CSP, input validation, and no scripts from untrusted origins.
- **Data loss:** WAL-consistent backup, read-only verification and restore-to-new-file commands are provided. Production restoration drills, automated encrypted backups, retention and migrations remain planned.

### Vulnerability reporting

Use a private security channel with the repository owner rather than publishing sensitive exploit details or credentials in a public issue.

## Erasure semantics

The owner-authenticated device history erase operation deletes all positions, geofence events and current fence state for the selected device without removing its registration or ingestion token. The browser requires typing ERASE. Individual point deletion also removes same-time geofence events and resets the device's fence-state. Deleted live records may still exist in snapshots, logs, external exports and offline device caches. Automated purge of those residual copies is not implemented.

## Import trust boundary

CSV uploads require the owning user's authenticated session and a device ID that belongs to the account. Requests are bounded by byte size and record count; unknown fields, malformed coordinates and timestamp formats are rejected. No raw uploaded contents or imported GPS coordinates are included in API errors. Imports run only against the owner's SQLite data. The duplicate check is best-effort and is not a substitute for concurrency locking or a future storage uniqueness policy. Avoid uploading files from untrusted sources without review.

## Authentication attempt controls

Online password checks use a memory-bounded, thread-safe, process-local sliding-window budget reserved **before** the scrypt operation. It has independent per-username (5), per-ASGI-peer (40) and service-wide (300) limits during each five-minute window. When the bucket count reaches its configured cap, expired buckets are reclaimed first; if capacity remains exhausted, new attempts are rejected without evicting active counters or consuming a login budget. This is fail-closed resource protection, not a distributed rate limiter. Success clears the username-specific bucket but not peer/global counters. The peer identity comes from ASGI, not an arbitrary request header. In deployments using a reverse proxy, verify trusted-proxy configuration and apply additional gateway-side controls: this mechanism alone is not safe against distributed attacks.

Unknown usernames are checked against a random dummy scrypt hash to reduce account-existence timing differences, but network/database effects remain and this is not a guarantee of constant-time operation. Generic authentication errors avoid disclosing which usernames exist. Per-account active sessions are capped at 20, automatically revoking the oldest token after additional sign-ins. MFA, persistent shared limits, recovery workflows and external identity require independent work.


## Manual retention cleanup safeguards

An authenticated user can preview deletion counts without changing records. Actual cleanup requires the exact confirmation phrase and matching preview counts inside an immediate SQLite write transaction. The UI requires an additional explicit confirmation. The action is account-scoped and removes old GPS points and events, resets affected geofence state and retains newer history and registered devices. It does not automatically purge backups, downloads, logs or offline caches and does not certify secure physical erasure or regulatory compliance.

## Geofence chronology and false-alert limits

Live geofence state changes only for a device point whose normalized UTC recorded timestamp is strictly greater than that device’s latest stored timestamp. Older and equal-timestamp reports remain in the private history for review/export but cannot generate new arrival/departure events. This prevents a same-instant conflicting or reordered report from inventing a transition. The rule applies to account-authenticated uploads, device ingestion tokens, and bounded CSV imports.

**Limitations:** timestamps are supplied by clients and can be erroneous or malicious. This rule does not prove presence, detect spoofing, remove duplicates, make alerts timely, or solve concurrent multi-writer ordering without a storage-level concurrency design. GoreeCloud Location is not an emergency or safety-critical response service.

## Concurrent location ingestion

Ingestion through owner sessions, registered-device tokens and CSV imports reserves the SQLite writer lock before querying the latest device position, then commits the point and its geofence state/event updates in one transaction. This is a single-database concurrency safeguard; it reduces contradictory alerts under simultaneous uploads and maintains a 15-second lock timeout. High load may still lead to rejected requests, and this should not be described as guaranteed delivery or reliable emergency response. Multi-server deployments, retries, queueing and broader transaction boundaries remain unverified and require dedicated design and stress tests.

## Map tile network isolation

The optional `GC_TILE_TEMPLATE` setting is restricted to a same-origin absolute path beginning with a single `/`. The API rejects scheme/host URLs, leading double-slash paths, backslashes and control characters. Browsers may otherwise normalize `/\host` to `//host`, making an apparently local tile template contact a third party. The frontend also resolves each resulting tile URL and checks that its origin matches the application origin before creating an image request. The Content Security Policy restricts images to `'self'` and `data:`, rather than allowing arbitrary external HTTPS image hosts.

**Limits:** The same-origin tile server or reverse proxy remains an operator-controlled deployment dependency and can itself log or redirect requests. Protect its access logs, reject external redirects at the proxy, and independently verify production network behavior. These checks do not install any tile data or make an external map provider available.

## Account-wide login session revocation

`POST /api/auth/logout-all` requires a valid owner account login session. It deletes every session entry belonging to that account, including the caller's current session, while leaving other users and registered GPS device ingestion credentials untouched. The Privacy & settings interface requires an additional confirmation. All prior session tokens fail on their next authenticated API request; a new login can create a new session immediately. This is useful after an account session is suspected to be exposed, but it does not rotate device keys, revoke downloaded exports, or replace MFA, an identity provider, and a centralized session audit.

## OwnTracks HTTP compatibility and trust boundaries

`POST /api/ingest/owntracks/{device_id}` accepts a narrow OwnTracks location JSON subset for one explicitly registered device. The OwnTracks app uses HTTP Basic: a fixed username `owntracks` and the **one-time device upload token** as the password. The endpoint does not accept user login passwords, query-string tokens, or anonymous submissions. HTTP Basic is only appropriate across a properly protected **HTTPS** connection; do not run this development preview over public plaintext HTTP or place private tokens in URLs and configuration examples.

Requests are bounded to 16 KiB and validated before any database writes. The device token is checked again inside a SQLite write transaction, so a key rotation cannot race a tracking write. The server discards unnecessary OwnTracks metadata and does not trust client-reported transition/waypoint messages as server geofence events. Valid locations use the existing monotonic timestamp and accuracy gates; malicious GPS data or timestamps can still be fabricated, and no device attestation, MQTT broker, encrypted OwnTracks payload, mobile background collection or emergency service is included. An HTTP 200 response (`[]`) acknowledges ingestion and does **not** confirm a safety notification or professional response.

## GPX XML history import safety

`POST /api/devices/{device_id}/import/gpx` is available only to an authenticated owner session; device write-only keys cannot read or import history. Requests have a 2 MiB raw body and 5,000 track point limit. The `defusedxml` parser rejects DTD, entity expansion and external resource references. Only supported GPX 1.0/1.1 namespaces, timestamped track points and safe numerical location fields are admitted. Every record is validated before any insert; database writes share the CSV import's serialized, owner-scoped transaction and duplicate handling. Do not upload unknown archives without review; a small bounded XML file can still use processing resources, and this feature has not completed external hostile-fixture, fuzzing or production load tests. Backups/exports are not changed by an import.

## GeoJSON history import isolation

The account-session-only GeoJSON importer reads a maximum 2 MiB body containing at most 5,000 RFC 7946 `Point` features. It rejects invalid and non-finite JSON, wrong geometry or coordinate ordering/type, missing timezone-aware timestamps, and malformed telemetry without partially writing history. It stores only validated location/telemetry fields; arbitrary identity, URL, Wi-Fi, map-provider and custom properties are ignored, never rendered or fetched. User-supplied FeatureCollection data cannot create places, groups, notifications or any cross-account sharing. The same owner-scoped SQLite transaction and duplicate checks apply as CSV and GPX imports. Real-world hostile-file fuzzing and production load/security acceptance remain unverified.

## In-tab session isolation and private browser state

When a user signs out, the web dashboard clears its in-memory account/device arrays, selected device, map coordinates and pins, rendered history, forms, open one-time key dialog and transient notification text. It also deletes the session token from `sessionStorage`. A completed or delayed API refresh is applied only if its original session token still matches the active session; a late 401 from a prior session cannot sign out a newly authenticated user.

This prevents accidental carryover of a prior account's GPS display within a reused browser tab. It does **not** prove forensic erasure from JavaScript heap memory, browser caches, screenshots, downloaded exports, developer tools, device storage or backups. Operators should use isolated trusted browser profiles for sensitive multiuser environments. Sensitive GPS responses remain marked no-store and server-side owner checks still enforce access boundaries.

## Per-device server-side collection pause

An authenticated owner can use `PUT /api/devices/{id}/collection` with a strict JSON Boolean to pause or resume new location writes. Device tokens and other account sessions cannot change this setting. The pause is checked inside the SQLite writer transaction before accepting live GPS or owner archive imports; a 409 means no point was written. Resume stores a UTC cutoff, rejects live fixes with earlier or equal client-supplied timestamps, and resets current geofence state to avoid inferring travel during the pause. Previously stored GPS and exports remain accessible and are not erased. Server refusal is **not** a guarantee that a hardware device or third-party client stopped recording locally or that client timestamps are trustworthy. Production TLS, native device acceptance, consent and threat-model review remain separate. [Detailed behavior](COLLECTION_CONTROL.md).

## Session-bound browser History pagination

The History interface now uses the account-checked cursor page endpoint rather than client-only filtering of the map's latest 1,000 points. Device ownership is enforced in SQL for every page regardless of cursor. The browser clears historical pages and cursor state on sign-out, and does not apply delayed responses after the session or selected device changes. A cursor confers no rights; exported archives, downloaded data, screenshots and offline copies must be protected separately.

## Private collection-control activity records

The server records genuine owner-driven collection pauses/resumptions for transparency. Each row contains only a device reference, an action and server UTC time. A single transaction updates the pause flag, writes the activity row and prunes the device history to 100 events; repeated requests that leave the state unchanged do not create records. The owner-only read API verifies the account on every query and returns current device names but **no GPS positions, passwords, device-upload keys, IP addresses or user agents**. Reverse-proxy access logs are independently governed. Clearing ordinary GPS history leaves these control records intact; device deletion cascades them. The records are not tamper-evident, legally certified audit trails and do not establish informed consent by themselves.

## Circle invitations do not grant location access

The new invite-only membership foundation has no public account directory. A prospective member generates a 256-bit random, 30-minute one-time code, stored as a hash. A circle owner consumes it to create a pending invitation; the recipient separately accepts or declines within 7 days. Account-scoped circle APIs reject ingestion-only device credentials, guessed IDs, unauthorized invite responses and role escalation. Owners may revoke a member and accepted members may leave. A member obtains circle metadata only, not another user's GPS, devices, geofence events, exports or private history. Membership is **not** authorization for location sharing. Future live/history grants must have distinct explicit consent, expiry and immediate revocation, and require independent security review before release. These membership records are not a safety/identity verification service, nor are they end-to-end encrypted messaging. See [circles model](CIRCLES.md).

## Circle UI does not bypass consent or sharing boundaries

The dedicated Circles screen is account-authenticated and does not render other members' GPS, devices, history, exports, or geofence events. One-time invite codes appear in a transient secret dialog, are never stored in browser persistence by this UI, and are cleared when the dialog closes or the user signs out. Explicit confirmation precedes accepting, leaving, removing members and deleting a circle. The page uses the same no-external-requests/CSP restrictions as the private location dashboard. All membership and expiry decisions are enforced again by the server; frontend controls do not authorize location sharing. Account switches discard in-memory circle lists and member rosters; offline browser caches/screenshots and user-copied codes require separate protections.
