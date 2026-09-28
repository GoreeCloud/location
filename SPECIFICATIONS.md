# GoreeCloud Location — Repository Specifications

**Lifecycle:** Forge  
**Deployment state:** Development  
**Platform Contract:** 2.0  
**Canonical project specification:** [PROJECT-SPECIFICATIONS.md](PROJECT-SPECIFICATIONS.md)  
**Project history:** [PROJECT-RECORD.md](PROJECT-RECORD.md)  
**Repository:** `GoreeCloud/location`

This file is the implementation-focused repository companion to the canonical project specification. It must not compete with `PROJECT-SPECIFICATIONS.md`.

## Accepted implementation boundary

The accepted repository baseline contains a Go API, PostgreSQL/PostGIS persistence with multi-user/device isolation tests, device enrollment/revocation, device-scoped credentials, tracking pause enforcement, authenticated location ingestion, owner-scoped live/history reads, bounded Timeline deletion/export behavior, Development Find My device state/recovery gating, and native Android collection/retry foundations.

The current clean stabilization candidate contains the Timeline ordering/accuracy/scope/privacy improvements, Platform Contract 2.0 declaration, and repository-local GLAZE UI V1.6 / 1.6.0 source mapping. Those changes remain candidate-only until protected promotion.

## Authority boundaries

GoreeCloud Location owns approved current-position services, tracking, personal location history, device location state, Find My, geofences, and location-sharing policy. GoreeCloud Maps may consume approved Location capabilities but must not become a second tracking/history authority.

Precise location is private by default. Ownership derives from authenticated user/device state, never request-supplied user IDs. Tracking pause and credential revocation are server-enforced.

## Platform requirements

Platform Contract 2.0 evaluates exactly nine Integral Platform Systems: Manager, Privacy Shield, Wardveil Security, Everkeep, Glaze UI, Mesh, Identity, Policy, and Observability.

GoreeCloud Sync remains separately governed and is not a tenth Integral Platform System.

The current approved presentation target is GLAZE UI V1.6 / 1.6.0. Application-specific rendered/accessibility, representative-device, performance, battery, rollback, and Human Visual Excellence acceptance remains separately required.

## Data and recovery

PostgreSQL/PostGIS is the first-party authoritative geospatial state foundation. Export, deletion, retention, backup, restore, preservation, migration, and clean-environment recovery must preserve ownership/authorization and must not resurrect deleted/expired data or revoked credentials.

## Provider boundary

Geographic map rendering, geocoding, and routing remain replaceable dependencies. Production provider acceptance requires licensing/provenance, privacy/security, network/egress, quality, attribution, reliability, monitoring, degradation, and rollback evidence.

## Acceptance boundary

Passing source, build, API, database, web, or Android checks proves only those checks. It does not establish production deployment, background tracking reliability, geographic-provider acceptance, production Identity, anti-stalking acceptance, Find My recovery authority, platform-system completeness, release, or Anchor qualification.
