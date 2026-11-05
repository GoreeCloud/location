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
