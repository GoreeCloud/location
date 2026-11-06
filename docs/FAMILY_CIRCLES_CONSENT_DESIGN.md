# Family Circles — Consent and Authorization Design Gate

**Status:** Proposed architecture, **not implemented**. Reviewed against the existing [product specification](PRODUCT_SPEC.md), [security boundaries](SECURITY.md), and [issue #3](https://github.com/GoreeCloud/location/issues/3) on November 6, 2026. This document does not authorize deployment, activate sharing, or change any existing account's location permissions.

## Purpose and non-negotiable invariants

Family circles should help a person coordinate with trusted people without weakening GoreeCloud Location's existing owner-only GPS records.

1. **Default deny.** Creating a circle, joining one, accepting an invitation, owning its administrative role, or registering a tracker grants **zero** location-reading permissions by itself.
2. **Independent personal consent.** Every sharing grant is initiated and approved by the account that owns the exact device. Circle administrators may invite or remove members but may not silently enable a member's GPS disclosure.
3. **Live and history are separate.** A live-only grant never permits the older points, exports, imported files, geofence events, or saved places. A history grant must name an explicit device, recipient, allowed date range, and expiration. New devices never inherit old grants.
4. **Immediate server-side revocation.** Authorization is checked against committed current state on *every* shared-location read, without granting powers through a cache, signed URL, historical cursor, bearer tracker token, or stale browser state.
5. **Pause suppresses disclosure.** Pausing a device's collection or its sharing mode must suppress all shared reads for that device, including its last-known fix, until the owner deliberately re-enables permitted visibility. Pausing does not erase private history.
6. **No public sharing surfaces.** No anonymous links, search engines, invitations that expose account existence, emergency overrides, unsolicited notifications, third-party trackers, or public maps in the initial implementation.
7. **No safety guarantees.** Shared locations can be stale, inaccurate, delayed, spoofed or absent. A family circle is not an emergency dispatch, crash detection, child monitoring, or location-attestation service.

## Proposed data boundaries

All identifiers below are internal, unguessable or account-scoped where practical; no data structure becomes authoritative without reviewed migration and tests.

| Proposed record | Minimal fields | Privacy rules |
| --- | --- | --- |
| Circle | id, creator account, display name, created time | No GPS and no automatic sharing |
| Circle membership | circle id, account id, member role, accepted time, removed time | Only explicit accepted members; administrative rights cannot grant other members' GPS |
| Invitation | target existing account, inviting account, circle, hashed random token, issued/expiry/redeemed times | One-time use, short expiry, generic response on unknown target, per-user issuance limits |
| Device sharing grant | exact owner/device, exact recipient, circle context, scope (live or history), valid-from/expiry, created/revoked times | No wildcard recipient, no automatic inheritance, grant never copied across circle membership |
| History scope | corresponding grant ID, inclusive allowed time window and read granularity | Explicit narrow authorization, distinct from latest-location access and full export |
| Consent activity | actor, scope, recipient, action, UTC time | No location coordinates, network identifiers or secrets; protect from broad visibility and bound retention |

Device GPS positions, geofence events, existing private exports and backup files remain within the owning account's database authorization boundary. A sharing grant references a device; it does **not** move, copy or re-owner the points.

### Circle membership versus location permissions

Membership is a relationship/communication permission, not a data-access permission. Creating a circle should never cause existing members, invited people, or its administrator to see a device's historical/current coordinates. The owner must initiate a separate, prominent sharing action for an exact recipient and device. Grant requests from recipients should be *requests for consent*, not auto-accepted permissions.

Avoid circle-wide wildcard grants in the first release: automatic membership changes could silently enlarge the audience. If circle-wide grants are considered later, they require a separate threat model, active-owner disclosure of the complete recipient roster and new-consent behavior for each added recipient.

## Proposed application flow

1. An authenticated user creates a private circle. No location-sharing endpoint is available yet.
2. An owner issues a short-lived invitation to a known, existing account. The invited person must review the circle name, inviter and scope, and explicitly accept or decline. Invitation enumeration should be blocked and invitation activity bounded.
3. The device owner sees an **unambiguous opt-in screen** describing the selected device, exact recipient, live versus historical scope, optional location approximation, end time, and revocation control. There is no prechecked consent.
4. The server validates the owner session, exact device ownership, both accepted circle memberships, role limitations, expiration and current pause state before inserting a grant.
5. A recipient requests only the authorized scope. On **every request**, the backend checks membership, grantor/grantee identities, non-revoked grant, valid time and device-sharing pause. The response carries `Cache-Control: no-store`, does not expose tracker keys, and contains only the minimum approved GPS fields.
6. A grant can be revoked by the device owner immediately, and ceases to authorize subsequent reads in the same committed SQLite transaction. The owner may also pause all sharing for a device independently of collection, leave the circle, or remove a recipient. These changes must have clearly defined fail-closed semantics.
7. An owner can review and erase appropriate consent records subject to a documented retention policy. Clearing a position, changing retention, rotating a tracker key, or removing a device must not accidentally resurrect shares.

### UI acceptance

Use existing **GoreeCloud UI** design tokens/components after verifying the [gc-ui repository](https://github.com/GoreeCloud/gc-ui); do not invent branding. Provide accessible invitation, accept, decline, consent grant, expiry, pause and revoke dialogs with keyboard/screen-reader labels, no misleading live/stale badges, and clear differentiation between collection and disclosure. An owner's sharing screen must show **exactly who can see what and until when**. The recipient's screen must never imply emergency reliability.

## Server authorization requirements

- Existing `/api/locations`, `/api/locations/page`, `/api/export/*`, `/api/places`, `/api/events`, import and deletion endpoints **remain owner-only**. Do not widen their account query filters to include circle members.
- Introduce distinct shared-read endpoints after test approval. Explicitly parameterize and SQL-bind both the requesting account and grant/device; verify scope and time at query execution, not only at authentication middleware.
- Grant IDs, membership IDs, invitation tokens and cursor values must never be treated as bearer authorization. Deny requests with guessed IDs, old grants, impersonated recipients and invalid roles.
- Every read after revocation must fail closed, including after concurrent membership removal and across multiple sessions. SQLite writer serialization alone does not guarantee device/client cache invalidation; client caches and browser state need separate controls.
- Trackers' **write-only** credentials must not create invitations, inspect memberships, accept grants or read another person's location.
- Avoid returning complete geofence event logs or downloadable unbounded history under a live-only grant. Server-filter precise coordinates to the approved precision; any coarse-location promise requires a tested quantization model, not display-only rounding.
- Treat all timestamps and GPS readings as untrusted, including when defining a live-fix freshness window. Consider a conservative maximum age and a visible stale indication before any live sharing is released.
- Consent audit trails and membership lists are private account data. Do not publish them to remote analytics, public issue reports, server logs, ad providers or unrestricted cloud backups.

## Threats and negative tests required before a shared-read API exists

| Threat | Required fail-closed test |
| --- | --- |
| Guessing another device/grant/circle ID | HTTP denial, no coordinates or metadata disclosed |
| Invited but not accepted | No shared reads before the recipient accepts |
| Accepted membership but no device grant | All shared-location endpoints deny |
| Administrator escalates a grant | Admin cannot share another owner's tracker |
| Live grant used for history/export | Historical points and full exports denied |
| Expired/revoked grant reused | Immediate denial; no stale cursor or cached response |
| Concurrent revoke/read | Defined commit ordering with revocation winning all later reads |
| Circle membership removed | Associated sharing grants cease authorizing immediately |
| Owner pauses collection/sharing | No display of the last-known shared position |
| Attacker changes time, device, recipient or precision | Server revalidates approved device/scope and explicit range |
| Device deletion, reassignment or key rotation | No orphaned/accidentally inherited share permissions |
| Cross-circle request and account switch | No cross-circle data, no browser residue, no server-side token confusion |
| Unknown invitation recipient or brute-force redemption | No username enumeration, bounded attempts, short-lived one-time tokens |
| Telemetry, logs, snapshots, exports, backups | No secret/location leakage into unrelated services |

Additional gates: database migration on an isolated copy, atomic consent updates, negative tests for role escalation, property-based authorization test matrices, full browser keyboard and three-viewport journeys, accessibility review, independent privacy/security review, production TLS/reverse proxy analysis, and an approved data retention/erasure policy.

## Sequenced implementation checkpoints

**Gate A — no location sharing:** Implement circles, invitations, member acceptance/exit, private owner-only membership read, and denial tests. Keep GPS reads unmodified and sharing disabled. Review schemas, consent wording and tests first.

**Gate B — explicitly granted live sharing:** Add per-recipient, per-device, expiring live grants and a distinct latest-location read endpoint, fail-closed pause/revocation, stale/accuracy labels and auditable consent. Verify exhaustive negative authorization tests before enabling any shared read in a development environment.

**Gate C — separately consented historical access:** Add explicitly bounded history ranges and separate expiry, revocation and export controls only after acceptance of Gate B. Preserve source ownership, retention, private-backup policies and individual erasure.

**Gate D — readiness review:** Validate real devices, multi-session revocation, supported deployments, performance, visual accessibility and independently reviewed privacy/security. Do not call circles production-ready or use them for emergency response before this gate.

**Current state:** Only the design gate is proposed here. GoreeCloud Location has owner-only positions, pause/resume collection and owner-visible collection-setting activity, but **no circle membership or cross-account GPS grant endpoints** as of this review.
