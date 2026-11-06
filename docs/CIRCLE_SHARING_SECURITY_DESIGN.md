# Circle Location Sharing — Security and Consent Design Gates

**Status: PROPOSED DESIGN ONLY — 6 November 2026. No location-sharing capability, grant table, endpoint, or feature flag is implemented or enabled.** This document is a reviewable security contract for a future, explicitly approved phase of GoreeCloud Location. Circle membership is currently limited to invitation metadata; it does not expose another account's GPS, device, history, geofences, exports, or live map.

## Purpose and authority

GoreeCloud is a private, self-hosted ecosystem. **GoreeShield** owns privacy and consent requirements; **Wardveil** owns threat modeling, technical security controls, and incident response; **GoreeCloud Mesh** may later integrate scoped events without bypassing privacy/security; **GoreeCloud UI** must present accessible, clear consent and revocation states using verified design-system tokens.

The account that owns a GPS device controls whether its positions may be shared. The prospective viewer must separately agree to receive the location feed. Neither a circle owner, administrator, tracker device token, invitation code, nor merely accepting circle membership may silently create a sharing grant. No default public audience, emergency override, third-party advertising, paid entitlement, or cross-product token reuse is permitted.

## Non-negotiable privacy invariants

1. **Deny by default.** No live, last-known, or historical positions are visible to another account without a separately approved and active per-device, per-viewer grant. Newly created circles, accepted memberships, device registrations, and migration/upgrades retain zero sharing.
2. **Separate two-party approval.** The device/account owner makes a specific offer; the intended accepted circle member must affirmatively accept that offer. Both parties see the device label, data category, intended recipient, expiry, and exact access limits before acceptance. No prechecked permission controls.
3. **No automatic history.** Live position access never unlocks the entire historical database. History and exports require an independent, narrower grant and explicit future approval. A live grant should return at most a bounded recent observation, not a timestamp cursor or complete replay.
4. **Per-device, per-recipient, per-purpose.** A grant identifies the source account and exact device, one accepted recipient, one circle, one scope, and expiry. It cannot mean all future devices, everyone in the circle, every account, or all external integrations.
5. **Revocation is an immediate authorization failure.** Both source and recipient can end their side of consent at any time. Circle membership removal, circle deletion, owner deletion, device deletion, device collection pause, account session revocation, grant expiry, and denial of either party must be evaluated on every protected read.
6. **Existing owner routes stay owner-only.** Current `/api/locations`, `/api/locations/page`, `/api/devices`, `/api/events`, and `/api/export/*` must not be widened to accept a circle ID or a membership as authorization. Any future shared-view endpoint must have a separate narrow query/serializer and deny by default.
7. **No sensitive URL leakage.** Browser maps and imagery remain same-origin/private. No private coordinates in URLs, access logs, analytics events, crash telemetry, email, notifications, query-string tokens, or public referrers. Shared responses require no-store cache controls.
8. **Pause remains controlling.** Pausing server-side collection prevents publication of fresh positions. Do not serve stale location as if it were live; show a clearly labeled paused/stale state without coordinates unless a separately approved historical access scope permits them.
9. **Membership is not identity proof.** Circle invitation and username are not a substitute for MFA, emergency services, device attestation, or independent identity verification. Coercion, stalking, account takeover, false GPS reports, and recipient screenshots remain threat considerations.
10. **No silent activation.** The feature remains absent/disabled until the founder separately approves the precise access semantics and production implications after security/privacy review.

## Proposed authorization model (not implemented)

A later design may introduce an explicit `location_share_grants` table only after approval. Proposed keys: immutable grant ID; source account; device ID; intended recipient account; circle ID; narrow data scope; created time; absolute expiry; consent state; source and recipient decision times; revocation time. Avoid storing coordinates in a grant/audit table. The referenced accepted circle membership must still exist on **each** read; checking it only at grant creation is insufficient.

Proposed state machine:

```text
No grant -> Source proposed -> Recipient accepted -> Active
                       |              |               |
                       v              v               v
                  Cancelled        Declined     Revoked / Expired
```

No transition from declined/revoked/expired back to active. A new consent cycle requires a distinct grant ID and fresh explicit decisions. Record only the minimal consent action, actor/account IDs, source device ID, scope and UTC time. Apply a bounded retention policy under GoreeShield rather than retaining unlimited social graphs. Do not copy one-time invitation codes into grants or activity logs.

### Future read gate

A hypothetical shared-current-position request must succeed only if **all** predicates hold at query time:

- The requesting bearer session belongs to the intended recipient (not to a GPS upload token).
- The selected circle exists; both accounts retain accepted membership, and the source is still owner of the exact device.
- The source and recipient both explicitly consented to this exact immutable grant ID and scope; the grant is active, unexpired, and not revoked.
- Device collection is unpaused and the position is sufficiently current, accurate and not contradicted by a newer owner privacy setting.
- The request returns only the minimal allowlisted fields for its scope. Arbitrary metadata, exact history timestamps, export links, geofence events, usernames not needed for display, and device tokens are not emitted.
- The database authorizes every read using a single coherent snapshot/transaction. Changing membership or revoking a grant must prevent the **next** request; stale async responses must not render data after a revocation or account switch.

Never accept a client-supplied source account ID as proof of ownership. Never join two accounts' positions through a broad unrestricted query. Prefer time-limited, purpose-bound grants over perpetual access.

## Threat model and mandatory mitigations

| Threat | Required treatment |
| --- | --- |
| Guessing circle, grant, user or device IDs | Server-side account + recipient + exact-grant checks; 404 on unauthorized resources; negative enumeration tests |
| Owner grants sharing without viewer's knowledge | Independent affirmative recipient acceptance; clear pre-consent summary |
| Recipient sees an entire history from a live grant | Separate serializers, strict query bounds, no cursor/export endpoints in live scope |
| Permission persists after leave/removal/deletion | On-read membership and grant checks; revocation and cascade tests |
| Consent revoked while a fetch is in flight | Versioned or session-bound UI results, no-store headers; no rendering of stale post-revocation result |
| Malicious/replayed GPS timestamps | Treat trackers as untrusted; age and accuracy policies; do not claim physical verification |
| Lost device, compromised account or shared credentials | MFA/identity-provider design, bounded sessions, device key rotation, audit and incident plan |
| Location leaked through third-party tile or error reporting | Enforce same-origin imagery/CSP; never send coordinates to external telemetry |
| Circle owner or server operator becomes abusive | No silent override; visible revocation and export audit; least privilege; documented operator trust limits |
| Mobile/offline caches retain prior locations | Explicit client cache invalidation and offline deletion behavior; document unavoidable prior copies |

## Proposed limited rollout sequence

**Gate A — privacy review:** Founder approval of exact purpose, data fields, default expiry, recipient acceptance, history exclusion, minors/safety considerations, coercion risks, and retention. Confirm that GoreeShield and Wardveil obligations are satisfied.

**Gate B — test-only implementation:** Implement a disabled-by-default prototype on isolated synthetic accounts. Do not modify production or distribute actual location data. Use an owner-only source dataset and a separate recipient test account.

**Gate C — automated adversarial acceptance:** Add at least the following tests before any merge that could expose location data: unauthenticated/device-token denial; unaccepted and declined invitation; accepted circle with no grant; grant for wrong recipient/device/circle; source and recipient consent missing independently; expired/revoked grant; source pauses collection; member leaves or owner removes member; owner deletes device/circle; owner revokes sessions; stale browser response after revoke; no GPX/GeoJSON/CSV/history/export access through a live grant; cross-account pagination and SQL injection attempts; external tile/CSP leakage; real-world disabled-by-default migration.

**Gate D — client and UX acceptance:** Validate accessible consent dialogs and interruption handling at phone/tablet/desktop, plus authorized native apps if built. Explicitly label stale/paused position states. No background polling without a visible, revocable user preference.

**Gate E — production authorization:** Separate affirmative founder approval after TLS/reverse-proxy verification, identity/session hardening, backups and recovery, independent security review, privacy impact assessment, and a rollback plan. Publishing a PR, successful CI, or membership acceptance is **not** deployment authorization.

## Evidence and current boundaries

The existing code already separates account-owned device/history endpoints from circle metadata. The circles foundation implements invite-code issuance, invitation acceptance, member revocation, and unused-code revocation, **without cross-account GPS grants**. The per-device collection pause and owner-only collection activity controls likewise do not create sharing. These are useful prerequisites, not proof that the proposed future sharing design has been built or independently accepted.

Reference documentation: [Circles](CIRCLES.md), [Security](SECURITY.md), [Collection controls](COLLECTION_CONTROL.md), [API](API.md), [Product specification](PRODUCT_SPEC.md), and [Implementation status](STATUS.md).
