# GoreeCloud Location — Repository Specifications

**Lifecycle:** Forge  
**Deployment state:** Development  
**Platform Contract:** 2.0  
**Repository:** `GoreeCloud/location`  
**Canonical project record:** `GoreeCloud/Projects/Project Specification — Location`

## Product boundary

GoreeCloud Location is the first-party GoreeCloud location application/service for owner-scoped current position, tracking, history, device state, Find My, sharing, places, geofencing, trips, and related recovery workflows. It must remain an original GoreeCloud system and must not transfer sensitive-location authority to GoreeCloud Maps or another presentation consumer.

## Current implemented foundation

- Go API with authenticated user and device boundaries.
- PostgreSQL/PostGIS persistence with tested multi-user ownership isolation.
- Device enrollment, revocation, device credentials, and tracking pause enforcement.
- Device-authenticated ingestion with idempotency and validation.
- Owner-scoped live and historical reads plus bounded deletion/export controls.
- TypeScript Live, Timeline, and Development Find My surfaces.
- Native Android collector/retry foundations.
- Current stabilization candidate adds bounded Timeline ordering, accuracy/scope presentation, filtered summaries, reset controls, and screen privacy.

## Platform requirements

Platform Contract 2.0 requires explicit evaluation of exactly nine Integral Platform Systems: Manager, Privacy Shield, Wardveil Security, Everkeep, Glaze UI, Mesh, Identity, Policy, and Observability. GoreeCloud Sync remains separately governed and is not a tenth Integral Platform System.

The implemented web presentation is GLAZE UI V1.3 / 1.3.0. The current approved shared target is GLAZE UI V1.6 / 1.6.0. Location remains migration-required until a substantive source migration and fresh Location-specific rendered, accessibility, responsive/adaptive, representative-device, performance, rollback, and Human Visual Excellence evidence exist.

## Privacy and security requirements

- precise location is private by default;
- ownership derives from authenticated user/device state, never request-supplied user IDs;
- tracking pause and device revocation are server-enforced;
- raw precise coordinates, bearer credentials, and private route/history content must not enter ordinary logs;
- sharing must be explicit, scoped, revocable, and separately controllable for live/history access;
- unavailable, stale, approximate, and permission-gated states must not be presented as current/precise truth;
- Find My recovery/offline-finding features require privacy, anti-stalking, abuse-prevention, cryptographic, Wardveil, Everkeep, Policy, and Observability acceptance before Anchor;
- presentation-only privacy modes do not substitute for retention, deletion, disclosure, or OS protection controls.

## Location / Maps boundary

GoreeCloud Location owns current position, tracking, personal location history, Find My, geofences, and location-sharing policy. GoreeCloud Maps may consume explicitly approved Location capabilities but must not become a second tracking/history authority.

Map rendering/geocoding/routing remain replaceable dependencies. Provider acceptance requires privacy, licensing/provenance, security/egress, quality, attribution, reliability, degradation, and operational evidence.

## Continuity and synchronization

Everkeep is required for accepted backup, restore, recovery, preservation, portability, and clean-environment restoration. Restore must not resurrect deleted/expired location contrary to policy or reactivate revoked credentials.

GoreeCloud Sync is separately governed. Location Sync must define the authorized dataset, version/change model, conflict handling, replication, offline resume, recovery, cross-device behavior, and authorization before runtime acceptance.

## Current acceptance boundary

The repository remains Forge/Development. Passing source, build, API, database, web, or Android checks proves only those checks. It does not establish production deployment, production Identity, geographic provider acceptance, physical-device background collection, Policy/Observability completeness, anti-stalking acceptance, release, or Anchor qualification.

## Next engineering priorities

1. Consolidate and validate the current Timeline/privacy candidate on exact current-main ancestry.
2. Migrate the Location web experience substantively to GLAZE UI V1.6.
3. Complete Android encrypted queue/retry/retention/recovery and physical-device validation.
4. Advance Find My state/recovery with anti-stalking and privacy/security gates.
5. Complete production Identity, Privacy Shield, Wardveil, Everkeep, Mesh, Policy, Observability, and Sync integrations.
6. Add approved replaceable geographic-map delivery.
7. Implement sharing, geofencing, places/trips, complete export/import, retention, backup/restore, deployment, rollback, and release gates.
