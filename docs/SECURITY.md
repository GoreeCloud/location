# Security and Privacy — GoreeCloud Location

**This is a development preview. Do not expose it as a production location service without an independent security review.**

## Sensitive data

Precise location history reveals home/work routines and sensitive activities. Avoid collecting any person's positions without their informed consent. Do not capture or publish real GPS traces, password secrets, API tokens, or database snapshots in this public repository. Accounts and devices are isolated by ownership checks. The API intentionally has no public signup or public location-sharing endpoints.

## Existing controls

- scrypt password hashing with 16-byte per-user salt; 14-character minimum password.
- Random 256-bit-class session and device tokens; only SHA-256 digests stored in SQLite.
- Eight-hour sessions, explicit session revocation and in-memory per-username login throttling; device-specific token rotation without deleting history.
- Separate owner-session and device-upload token scopes.
- Pydantic validation, strict request schemas, bounded GPS numeric fields and timestamp checks.
- Private-by-default API endpoints, account-scoped database queries.
- Security response headers: CSP, no-sniff, no-referrer, deny framing, no-store API caching.
- No embedded CDN scripts, analytics, advertising, remote geolocation calls, or default tile requests.
- Docker Compose loopback-only host binding, non-root service user, dropped capabilities.
- No first-run default credentials or network-accessible bootstrap user creation.

## Not yet hardened for Internet exposure

- Sessions are held in browser sessionStorage (XSS-sensitive); do not treat them as persistent MFA sessions.
- Rate limiting is local-process only. Reverse proxies must enforce request limits and TLS.
- No password reset, MFA, OIDC integration, IP allow-listing, distributed account lockout or user-session token rotation. Device ingestion token rotation exists.
- No independent audit of proxy headers or shared tenant safety at scale.
- No automated at-rest encryption. SQLite DB and manual snapshot files use mode 0600; use OS volume encryption and protected backups.
- Database schemas have not yet been migrated under release controls.
- No penetration test, native mobile client audit, or production load/recovery validation.
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
- **Data loss:** an operator-run WAL-consistent backup command exists; automated encrypted backups, tested restore drills and migrations remain planned.

### Vulnerability reporting

Use a private security channel with the repository owner rather than publishing sensitive exploit details or credentials in a public issue.

## Erasure semantics

The owner-authenticated device history erase operation deletes all positions, geofence events and current fence state for the selected device without removing its registration or ingestion token. The browser requires typing ERASE. Individual point deletion also removes same-time geofence events and resets the device's fence-state. Deleted live records may still exist in snapshots, logs, external exports and offline device caches. Automated purge of those residual copies is not implemented.
