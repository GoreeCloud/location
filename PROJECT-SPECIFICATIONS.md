# GoreeCloud Location — Project Specifications

**Repository:** `GoreeCloud/location`  
**Project type:** First-party GoreeCloud location application and service  
**Lifecycle:** Development  
**License:** AGPL-3.0-only  
**Canonical authority:** This file is the authoritative project specification once accepted on the default branch.  
**Migration source:** `Project Specification — Location.docx`, Drive file `131KmxfjQM4gFq4XXunJFECfEY623c_Ox`, v0.4, last updated September 15, 2026.  
**Drive status:** Frozen migration input only. The Drive source must not be edited or maintained as the project specification and must be permanently removed after verified repository migration.  
**Archive rule:** If a separate historical specification archive is required, use the appropriate Dropbox archive directory rather than Google Drive.

## Migration and precedence

This migration preserves the complete substantive Drive project specification while moving current project-specification authority into GitHub.

Verified repository implementation, accepted commits, tests, CI, releases, and runtime evidence control claims about what is currently implemented. The migrated Drive material below preserves requirements, approved scope, architecture, privacy/security expectations, recovery obligations, and dated candidate evidence. Unmerged pull requests remain candidate evidence only and must not be represented as accepted implementation.

The former root `SPECIFICATIONS.md` is incorporated below as the repository implementation boundary that existed on `main` when this migration branch was created. It is retired by this migration to avoid a competing canonical specification.

## Current repository implementation boundary at migration

# GoreeCloud Location — Repository Specifications

Status: Development  
Canonical project specification: `PROJECT-SPECIFICATIONS.md`  
Repository: `GoreeCloud/location`

## Product boundary

GoreeCloud Location is the first-party GoreeCloud location platform for owner-scoped location history, live device tracking, Find My, sharing, places, geofencing, trips, and related recovery workflows. It is a native GoreeCloud application/service, not a permanent fork of another location product.

## Current implemented foundation

- Go HTTP service with authenticated user and device boundaries.
- PostgreSQL/PostGIS persistence and tested multi-user ownership isolation.
- Device enrollment, revocation, device-scoped credentials, and tracking pause enforcement.
- Device-authenticated location ingestion with idempotency and validation.
- Owner-scoped live and historical location reads.
- TypeScript web Live surface and Development Find My device/recovery-state surface.
- Native Android collector/retry foundations present in the repository.

## Required platform integration

Applicable surfaces must integrate the current approved GoreeCloud platform systems, including GoreeCloud Identity, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, and Glaze UI. The current UI design target is Glaze UI 2.0.0 Stable or newer. Rendered conformance is an acceptance gate and is not implied by source labels alone.

## Privacy and security requirements

- Precise location is private by default.
- Authorization must derive ownership from authenticated identity/device state, never request-supplied user IDs.
- Tracking pause and device revocation are server-enforced.
- Raw precise coordinates must not be written to ordinary application logs.
- Sharing must be explicit, scoped, revocable, and separately controllable for live/history access.
- Find My recovery and offline-finding features require anti-stalking, abuse-prevention, cryptographic, Privacy Shield, Wardveil, and Everkeep acceptance before Stable promotion.

## Current acceptance boundary

The repository remains Development. Passing source/build/database tests does not establish production deployment, rendered browser acceptance, production Identity integration, anti-stalking acceptance, geographic map-provider deployment, sharing acceptance, or production readiness.

## Next engineering priorities

1. Complete rendered Glaze UI 2.0 acceptance for Live/Find My surfaces.
2. Complete browser-session integration with GoreeCloud Identity.
3. Add replaceable geographic map-provider integration without weakening privacy boundaries.
4. Continue native Android collection/offline synchronization acceptance.
5. Implement sharing, retention, export, recovery, anti-stalking, and production security gates.

## Migrated Drive project specification — v0.4

The following material is migrated from the verified portable DOCX source. Dated implementation checkpoints remain historical/candidate evidence where newer GitHub state exists.

Project Specification — Location
## Migrated source metadata
Document Title: Project Specification — Location
Document Owner: LaDamian Goree
Version: v0.4
Status: Draft
Created: Aug 22, 2026
Last Updated: September 15, 2026
Classification: Internal
Document Type: Software Project Specification and Implementation Blueprint
Project Name: GoreeCloud Location
Repository: GoreeCloud/goreecloud-location
Development Model: Original GoreeCloud-owned software development
Release Lifecycle: Development
License: AGPL-3.0-only
Initial Deployment Model: Self-hosted web application and location service with native Android client
Long-Term Environment: GoreeCloud Family Services VM
Planned Product Address: https://location.goreecloud.com
Design Language: GLAZE UI V1.4.1 / 1.4.1 is the current Official Stable required target; the active Location source candidate remains mapped to V1.3 / 1.3.0 pending migration and Location-specific acceptance.
Security Identity: Wardveil Security by GoreeCloud
Privacy Identity: GoreeCloud Privacy Shield
Resilience and Preservation Identity: Everkeep
Authoritative Record: Yes
## 1. Purpose
I will build GoreeCloud Location as the first-party GoreeCloud application and service for private location history, real-time location tracking, family and multi-user location sharing, geofencing, trips, places, maps, device tracking, and location analytics.
My objective is to provide one coherent GoreeCloud-owned location platform instead of requiring users to understand or operate separate products for live tracking and historical location history. The product is heavily inspired by the complementary strengths of Dawarich, Google Timeline, and Traccar while remaining governed by GoreeCloud requirements for ownership, privacy, self-hosting, portability, recoverability, security, and technology independence.
## 2. Product Role and Governing Direction
I will treat real-time tracking and long-term location history as separate technical capability domains behind one user-facing application.
The governing product direction is:
Real-time tracking answers where an approved user or device is now.
Location history answers where an approved user or device has been over time.
GoreeCloud Location unifies both capabilities without weakening their data, privacy, operational, or security boundaries.
I will not make Dawarich or Traccar permanent user-facing dependencies of the final product. I may use them as transitional reference, compatibility, migration, validation, or data-source systems while the native GoreeCloud implementation reaches feature and reliability parity.
## 3. Competitive Inspiration
Dawarich provides the primary inspiration for long-term history, interactive maps, timeline views, visits, travel analysis, heat maps, trips, imports and exports, family location sharing, and preservation of location records.
Traccar provides the primary inspiration for real-time GPS tracking, device and account management, geofencing, alarms, notifications, route awareness, reports, vehicle-style tracking, and compatibility with dedicated GPS tracking devices.
Google Timeline provides the primary experience inspiration for a unified personal chronology organized around days, places, visits, trips, routes, and historical review.
I will use these products as capability references rather than as permanent architectural authorities. GoreeCloud Location must eventually own its data model, application behavior, clients, APIs, migration tools, security boundaries, and release lifecycle.
## 4. Product Identity and User Experience
The user-facing application name is GoreeCloud Location.
The primary web address is https://location.goreecloud.com.
I will design the application with Glaze UI and preserve a consistent experience across the web application and native clients.
The primary navigation model should include:
Live
Timeline
Places
Trips
Geofences
Devices
Insights
Sharing
Imports and Exports
Settings
The interface must remain useful for ordinary family users while allowing advanced controls to remain available when needed.
## 5. Multi-User Architecture
Multi-user support is a foundational requirement and must exist from the first database migration onward.
Each person must receive an independent user identity. Each device must have a distinct device identity. Location records must always have an explicit owning user and source device.
Service administration and location-data ownership are separate privileges. Administrative authority over the application must not automatically grant unrestricted access to another user's private location history.
I will implement explicit authorization checks at the API and data-access layers. The user interface must not be the only isolation mechanism.
## 6. Location Ownership and Sharing Model
Location information is private by default.
A user may explicitly share location information with another approved user through a sharing relationship. A sharing policy may independently control:
precise or approximate location
live location only, historical location only, or both
selected devices or all eligible devices
temporary or continuing access
expiration time
revocation
visibility of routes, places, trips, and visit details
A user must be able to stop sharing immediately. A recipient must lose access when a sharing relationship expires or is revoked.
The platform must never assume that all members of one household automatically have access to every other member's location history.
## 7. Core Data Model
The initial native data model should include:
User
Device
DeviceCredential
Position
LocationSample
Place
Visit
Trip
TripSegment
Geofence
GeofenceEvent
SharingRelationship
SharingPolicy
LocationSnapshot
ImportJob
ExportJob
NotificationRule
RetentionPolicy
UserPreference
AuditEvent
Every Position and LocationSample record must be associated with an owning user and source device.
I will use schema-level and application-level protections to prevent orphaned or ambiguously owned location data.
## 8. Location Ingestion
The server must expose an authenticated versioned ingestion API for approved clients and adapters.
The ingestion pipeline should support:
native GoreeCloud Android client reports
future GoreeCloud iOS client reports
Dawarich migration or compatibility adapters
Traccar migration or compatibility adapters
OwnTracks-compatible inputs where practical
GPX imports
GeoJSON imports
CSV imports where a documented schema exists
Google location-history migration formats when practical
other open location formats that materially improve portability
The ingestion service must validate timestamps, coordinates, accuracy, user ownership, device identity, authorization, duplicate records, and malformed payloads before accepting data.
## 9. Live Tracking
The Live experience must provide current or most-recent approved location information for the user and any explicitly shared users or devices.
The live model should support:
current location
last update time
reported accuracy
movement state where available
device battery state where voluntarily reported
stale-device indication
map following
recent movement trail
per-device visibility
user-selected precision
Live tracking must make stale information visibly distinguishable from current information.
## 10. Timeline and Historical Review
The Timeline experience must provide chronological review by day, week, month, and custom date range.
The historical view should support:
location paths
stops and visits
travel segments
duration
distance
places
trip boundaries
manual corrections
confirmed and unconfirmed inferred visits
history playback
device filtering
map-layer filtering
Users must be able to correct their own historical records without silently destroying the original audit context where preservation is required.
## 11. Places and Visits
GoreeCloud Location should identify meaningful stops from location samples and allow users to confirm, reject, merge, split, rename, or otherwise correct inferred visits.
Places may include:
home
work
favorites
frequently visited places
custom named places
temporary travel locations
user-defined private locations
Place inference must remain editable because automated geospatial inference can be incorrect.
## 12. Trips
A trip may be created manually or inferred from a date range and movement history.
Trips should support:
start and end times
route
distance
duration
cities and countries visited where resolvable
stops
notes
related photos through approved GoreeCloud Photos integration
historical playback
export
Trip records must remain portable and must not require a third-party mapping provider to preserve their underlying location data.
## 13. Maps and Visualization
The web application should use an open and replaceable mapping stack. Map rendering and map-data providers must remain swappable so GoreeCloud is not permanently dependent on one vendor.
Map capabilities should include:
live position markers
historical points
route lines
heat maps
geofences
privacy zones
trip overlays
place markers
date and device filters
history playback
optional Fog of War or explored-area visualization
The authoritative location record is the stored geospatial data, not a rendered map tile.
## 14. Geofencing and Location Events
Users must be able to create geofences using circles and, when supported, polygons.
The event engine should support:
enter events
exit events
dwell events
arrival events
departure events
scheduled geofence rules
temporary geofences
user-specific rules
device-specific rules
Geofence events may trigger GoreeCloud Notify through an approved integration.
## 15. Devices
Supported device classes should include:
Android phones
future iOS devices
tablets where practical
vehicles
dedicated GPS trackers
other approved location-reporting devices
Each device should have its own credentials, owner, display identity, last-seen state, tracking settings, retention controls, and revocation path.
The loss or compromise of one device credential must not require replacing every user's location credential.
## 16. Native Android Client
The first native mobile client should be Android and should use Kotlin.
The Android client should eventually support:
background location collection
foreground-service behavior required by Android
adaptive reporting intervals
battery-aware tracking modes
offline buffering
delayed synchronization
network-change recovery
device enrollment
tracking pause and resume
sharing status visibility
permission-state diagnostics
boot recovery where permitted
user-visible data-collection state
The application must respect Android permission and background-execution requirements instead of attempting to bypass them.
## 17. Future iOS Client
A future iOS client should use Swift unless later architecture establishes a stronger reason to use another approved approach.
The iOS client must follow Apple platform restrictions for background location access, user consent, and location permissions.
No iOS implementation is considered complete merely because the web application works on an iPhone browser.
## 18. Privacy Controls
GoreeCloud Privacy Shield requirements apply directly to this project.
The application should provide:
tracking pause
delete selected date ranges
export before deletion
retention controls
approximate-location sharing
precise-location sharing
privacy zones
hidden places
device-specific tracking settings
per-user sharing policies
clear indicators when sharing is active
clear indicators when background tracking is active
minimal telemetry
no advertising identifiers
no behavioral advertising
no sale of location data
Location collection must be necessary, visible, controllable, and limited to the user's approved purpose.
## 19. Security Requirements
Wardveil Security requirements apply to the application, clients, APIs, background jobs, database, deployment, and administrative interfaces.
Security requirements include:
authenticated APIs
authorization on every user-owned resource
device-specific credentials
least privilege
rate limiting
input validation
secure secret handling
session protection
audit logging for privileged actions
credential revocation
protection against insecure direct object references
secure transport
dependency and vulnerability management
security testing before production approval
Reusable credentials, tokens, private keys, signing material, and sensitive configuration must not be stored in ordinary project documentation or committed to source control.
## 20. Data Storage
I prefer PostgreSQL with PostGIS for the authoritative location database.
PostGIS is appropriate because the application will need spatial indexes, distance calculations, geofence queries, radius searches, bounding-box queries, route analysis, geographic clustering, and other geospatial operations.
The database must support per-user isolation, durable migrations, backup and restore, export, and future schema evolution.
## 21. API Architecture
The application should expose a versioned first-party API under an explicit namespace such as /api/v1/.
The API should support:
authentication
user profile and preferences
device enrollment and management
location ingestion
live location reads
historical location queries
places
visits
trips
geofences
sharing
imports
exports
notifications
administrative operations within authorized scope
Real-time user experiences may use authenticated WebSocket or Server-Sent Events channels when appropriate.
## 22. GoreeCloud Integrations
GoreeCloud Location should integrate with other GoreeCloud applications where the relationship has a clear purpose.
Planned integration directions include:
GoreeCloud Photos for geotagged trip and memory views without duplicating the authoritative photo library
GoreeCloud Notify for approved location and geofence notifications
GoreeCloud Monitor for service health and observability
GoreeCloud Identity for future centralized authentication and single sign-on
Everkeep for backup, restore, recovery, preservation, and migration requirements
GoreeCloud Network for private connectivity and device-access context where appropriate
GoreeCloud DNS for approved private service discovery where appropriate
Integrations must use explicit APIs and authorization boundaries rather than direct cross-application database access unless a separately approved architecture requires it.
## 23. Import and Migration
The project must provide a controlled path to import existing location history so users do not lose historical records when adopting GoreeCloud Location.
Priority migration sources include:
Dawarich
Traccar
Google location-history exports
OwnTracks
GPX
GeoJSON
CSV where a supported schema can be defined
Import jobs must be restartable where practical, report errors clearly, avoid silent record loss, detect duplicates where possible, and provide reconciliation information.
## 24. Export and Portability
Users must be able to export their own data in open and documented formats.
Export targets should include:
GPX
GeoJSON
CSV
a documented GoreeCloud archival format capable of preserving relationships that simpler formats cannot represent
A complete account export should preserve enough information to migrate location history to another system without requiring continued access to GoreeCloud Location.
## 25. Transitional Dawarich and Traccar Role
The existing Dawarich and Traccar strategy remains useful as a transitional architecture, but it is not the intended final product boundary.
During transition:
Dawarich may remain the historical-location reference and migration source.
Traccar may remain the real-time tracking and dedicated-device reference or migration source.
GoreeCloud Location becomes the single user-facing target as native capabilities mature.
I will not retire either transitional service until the native replacement has passed data reconciliation, import validation, user-isolation testing, functional acceptance, backup and restore testing, and rollback review for the capabilities being replaced.
## 26. Deployment Architecture
The initial service architecture should use:
GoreeCloud Location web application
Go API and background services
PostgreSQL with PostGIS
native Android client
Docker and Docker Compose where appropriate
Caddy for approved HTTPS publication
NetBird for private access where required
GoreeCloud Monitor for health visibility
GoreeCloud Notify for approved event notifications
No backend database or administrative service port should be exposed directly to the public internet.
## 27. Repository Structure
The repository is GoreeCloud/goreecloud-location.
The repository should contain the canonical application source, documentation, migrations, API contracts, tests, deployment definitions, release workflows, and official application artwork.
A possible top-level structure is:
apps/web
apps/android
services/api
services/worker
packages/contracts
packages/glaze
database/migrations
deploy
docs
tests
assets
The exact structure may evolve as implementation evidence becomes available.
## 28. Recommended Technology Stack
Web interface: React, TypeScript, Vite, and Glaze UI.
Primary API and long-running services: Go.
Database: PostgreSQL with PostGIS.
Android: Kotlin.
Future iOS: Swift.
Map rendering: an open MapLibre-compatible stack.
Real-time updates: authenticated WebSocket or Server-Sent Events where appropriate.
Container deployment: Docker and Docker Compose.
Technology choices remain subject to GoreeCloud programming-language, open-source, security, and technology-independence requirements.
## 29. Milestones
Milestone 0 — Foundation
Create the repository, license, CI, Glaze UI shell, API foundation, PostgreSQL/PostGIS integration, migrations, Docker development environment, and security baseline.
Milestone 1 — Users and Devices
Implement authentication, authorization, user isolation, devices, device credentials, user preferences, and device enrollment.
Milestone 2 — Native Tracking
Implement the position-ingestion API, Android collection prototype, offline queue, synchronization, and initial live map.
Milestone 3 — History
Implement historical queries, daily Timeline, map paths, distance calculations, date filtering, and device filtering.
Milestone 4 — Places and Visits
Implement stop detection, visit inference, place management, confirmation, rejection, editing, and corrections.
Milestone 5 — Sharing
Implement explicit user-to-user sharing policies, live sharing, history sharing, approximate sharing, expiration, and revocation.
Milestone 6 — Geofencing
Implement geofence definitions, event evaluation, enter, exit, dwell, arrival, departure, and GoreeCloud Notify integration.
Milestone 7 — Trips and Insights
Implement trips, statistics, heat maps, travel summaries, historical playback, and additional personal insights.
Milestone 8 — Migration
Implement validated migration paths for Dawarich, Traccar, Google location-history exports, OwnTracks, GPX, and GeoJSON.
Milestone 9 — Portability and Recovery
Implement full exports, import/export round-trip tests, backup and restore verification, and historical-integrity checks.
Milestone 10 — Native Client Maturity
Move the Android client toward production readiness and establish the approved future iOS foundation.
Milestone 11 — Competitive Expansion
Add advanced tracker support, vehicle tracking, dedicated GPS-device compatibility, reports, deeper analytics, and additional capabilities required to exceed the reference products where practical.
Milestone 12 — Native Cutover
Perform a controlled migration of location.goreecloud.com to the native GoreeCloud Location application and retire transitional dependencies only after acceptance and rollback requirements are satisfied.
## 30. Production-Readiness Gates
GoreeCloud Location must not be classified as Stable or production-ready solely because tracking data appears on a map.
Production approval requires, at minimum:
server-side multi-user isolation
authorization tests
location-ingestion validation
privacy controls
sharing revocation tests
device credential revocation
migration validation
export validation
backup and restore proof
database migration proof
monitoring and observability
security review
dependency review
accessibility review
Glaze UI conformance
Android background-tracking acceptance on supported devices
stale-data handling
recovery and rollback documentation
no unresolved critical or high-severity security defects
no undocumented direct public backend exposure
## 31. Data Preservation and Recovery
Location history may represent years of personal history and must be treated as durable personal data.
I will protect the authoritative database and required supporting state under GoreeCloud backup, restore, recovery, and Everkeep requirements.
Restore validation must prove that users, devices, location samples, places, visits, trips, sharing policies, and relevant audit records remain correctly associated after recovery.
## 32. Observability
Operational monitoring should cover:
API availability
web application availability
database health
ingestion failures
background-job failures
queue backlog
import failures
export failures
notification-delivery failures
unexpected authentication failures
storage growth
backup status
Observability must avoid turning private location history into ordinary application logs.
## 33. Competitive Objective
I intend GoreeCloud Location to become a first-party location platform that can replace the combined user-facing roles of Dawarich, Traccar, and Google Timeline for approved GoreeCloud users.
The competitive objective is not simple feature counting. The application should exceed reference products where practical through stronger ownership, self-hosting, multi-user isolation, explicit sharing controls, portability, recovery, GoreeCloud integration, privacy-by-default design, and long-term maintainability.
## 34. Initial Open Decisions
The following decisions remain intentionally open until implementation work provides better evidence:
exact map-tile and geocoding providers
initial reverse-geocoding implementation
final trip-inference algorithm
final visit-clustering algorithm
exact Android sampling profiles
whether dedicated tracker protocol support is implemented natively or through a compatibility gateway during early releases
future iOS delivery schedule
final retention defaults
whether public internet access is required for any client workflow or whether the initial deployment remains private-network-first
## 35. Initial Acceptance Definition
The first meaningful native acceptance target is reached when two independent users can enroll separate devices, report test location data, view only their own history by default, explicitly share approved location data with each other, revoke that sharing, and successfully export and restore their own history without cross-user data leakage.
## 36. Final Governing Principle
I will build GoreeCloud Location as one privacy-first, self-hosted, multi-user location platform with clear internal capability boundaries for live tracking, historical preservation, sharing, geofencing, trips, maps, analytics, devices, migration, and recovery.
The long-term authority is GoreeCloud Location itself. Dawarich and Traccar may assist the transition, but the final product must remain independently maintainable, portable, secure, recoverable, and under GoreeCloud control.
## 37. Current Implementation State
I established the public GoreeCloud/goreecloud-location repository under the approved AGPL-3.0-only license and now have the Foundation and Users and Devices source milestones merged to main through Pull Requests #1 through #3. Pull Request #1 established the native repository foundation. Pull Request #2 established the validated development PostgreSQL/PostGIS and Docker runtime foundation. Pull Request #3 established the authenticated multi-user user/device boundary.
The current development runtime includes an ownership-first PostgreSQL/PostGIS schema, digest-pinned development PostGIS service, safe environment-based database configuration, schema-aware API readiness, database integration acceptance, and a first-party repeat-safe location-migrate command. The migration command uses the same pgx connection configuration as the API, skips already-recorded migrations, and verifies that each newly executed migration records its own version before CI proceeds.
Pull Request #3, “Milestone 1: establish authenticated users and devices,” reached exact candidate head bdec712c96c430db5186adcadf00041382202242. GitHub Actions CI run 32606075939 passed on that exact head. The gate covered Go dependency verification, canonical formatting, vet, unit tests, API/admin/migration-tool compilation, TypeScript/Vite build, PostgreSQL/PostGIS migrations, ownership and geospatial checks, schema-aware readiness, repeat-safe migration execution, and authenticated two-user/device isolation and credential-revocation acceptance. I merged that validated candidate with expected-head protection as GitHub-signed main commit b687f0e3c66733ee840562d9491648a4ec69e003. Its two parents are prior main ee1c1e7d5a9ca22549dba3359e4df0d5149b85e9 and the validated candidate bdec712c96c430db5186adcadf00041382202242.
Milestone 1 now implements high-entropy opaque user access credentials with persisted hashes, separately scoped and revocable device credentials, local administrative user bootstrap, authenticated user identity, owner-scoped device enrollment/list/revocation, user preferences, authenticated device identity, and server-side ownership enforcement derived from the authenticated credential rather than a client-supplied user identifier. Cross-user device operations are rejected without disclosing another user's object, and device revocation invalidates its credentials. Plaintext credentials are returned only at issuance, and ordinary logs do not record bearer tokens or private location coordinates.
Milestones 0 and 1 remain implemented and exact-head validated as development source. The first Milestone 2 — Native Tracking source slice is now implemented and merged through Pull Request #4. Exact head b36a6a1c5b3cf78bfab96173bd720f4e69cb9a52 passed CI run 32607652917 and entered main as merge commit bb6f6d6dd2d6118c2a41112804bd02e5a73fc143. This slice provides device-authenticated native location ingestion, explicitly required and bounded coordinates, owner- and device-derived authorization, idempotent sample handling, transactional tracking-pause and revocation checks, owner-scoped history queries, owner-scoped most-recent live reads, PostGIS-backed persistence, and two-user tracking-isolation acceptance. Milestone 2 is not complete: the native Android collection prototype, foreground-service and permission-state UX, encrypted or otherwise approved offline queue, delayed synchronization, adaptive collection profiles, initial Glaze UI live map, authenticated live-update transport, and later Timeline, places, sharing, geofencing, migration, export, recovery, packaging, deployment, and production acceptance remain future work unless separately recorded as completed.
Release Lifecycle remains Development. The source merges do not constitute a release, packaged artifact, deployment, production acceptance, or Stable promotion. No location.goreecloud.com native cutover, DNS, Caddy, NetBird, firewall, production database, monitoring target, backup configuration, user location collection, or transitional-service retirement is claimed. The connected GitHub status surfaces available during the Pull Request #3 merge did not expose a separate push-triggered Actions run for the merge commit, so the authoritative evidence recorded here is the successful exact-head Pull Request #3 CI plus the verified signed merge ancestry; I do not infer additional post-merge CI evidence that was not observable.
Superseding Native-Build and Platform Integration Mandate
This specification is governed by the platform-wide requirement that this application be built natively from the ground up as original GoreeCloud-owned software. Earlier maintained-fork or upstream-product implementation language is transitional only. Narrow critical foundations may be retained only when independently replacing them would materially increase security, cryptographic, protocol, standards, codec, rendering, operating-system, runtime, or interoperability risk; WireGuard and mature cryptographic or encryption primitives are canonical examples. Such exceptions must remain limited to the minimum technical foundation and must not preserve upstream product architecture, UI, branding, workflows, or general application logic.
This application must remain current with the latest applicable Stable Glaze UI contract and the latest approved Wardveil Security, Privacy Shield, and Everkeep contracts. All four are mandatory. Missing, incomplete, superseded, outdated, unverified, or unaccepted integration with any required platform system blocks Stable qualification.
## 38. Find My System — Core Platform Capability
GoreeCloud Location includes a first-party Find My system as a core platform capability. Find My is integrated directly into GoreeCloud Location rather than operating as a separate or disconnected service. Together, these capabilities make GoreeCloud Location the platform-wide location, device-finding, proximity, location-sharing, lost-device recovery, geofencing, and location-trust subsystem.
Find My Devices
- Locate enrolled GoreeCloud phones, tablets, laptops, desktops, TVs, wearables, servers, and other supported devices.
- Provide a unified multi-device map and search/filtering by device name, type, owner/profile, status, or authorized location context.
- Preserve and clearly distinguish last-known location from live location.
- Report location confidence, source, estimated accuracy, and last-seen state without presenting stale or inferred positions as precise live positions.
Nearby Finding
- Support nearby discovery using compatible Bluetooth, UWB, or comparable proximity technologies.
- Provide distance estimation, directional guidance, and signal-strength guidance where hardware permits.
- Support Play Sound and a carefully controlled lost-device sound mode according to platform and safety constraints.
Lost Device Dashboard and Lost Mode
- Provide a centralized recovery dashboard showing device identity, connection state, battery state when available, last-seen time, current or last trusted location, location confidence, relevant network state, and authorized recovery actions.
- Lost Mode places a missing device into a protected recovery state, locks or restricts unauthorized access, supports an owner-defined recovery message and carefully selected recovery contact information, restricts sensitive functions, and may increase appropriate location reporting when technically possible and authorized.
- Notify authorized users of important recovery events and provide a protected found-device workflow for returning a recovered device to normal operation.
Remote Device Protection
- Support remote lock and protected remote secure erase for eligible devices.
- Destructive actions require explicit confirmation, strong identity verification, ownership/authority verification, and appropriate Wardveil Security policy evaluation.
- Recovery commands expose status such as pending, delivered, executed, rejected, expired, or unreachable and may be securely queued for eligible offline devices until they reconnect.
- Policies may introduce safeguards or waiting periods for especially sensitive destructive operations.
Offline Finding and Find My Network
- Compatible lost devices may be discoverable without ordinary Internet connectivity through an optional GoreeCloud Find My Network.
- Participating GoreeCloud devices may observe compatible lost devices using privacy-preserving discovery without receiving unnecessary information about the lost-device owner.
- Offline-finding reports use encrypted, end-to-end protected reporting and protected owner retrieval so unauthorized intermediaries cannot read usable location reports.
- Rotating device identifiers reduce persistent tracking risk, and finder participation should avoid revealing finder identity to the lost-device owner where unnecessary.
- Participation is understandable and controllable. Rate limits, query controls, abuse detection, and network restrictions protect against surveillance and abusive finding activity.
Device Location Timeline
- Provide an optional history of trusted device-location observations with controls to enable, disable, review, clear, and selectively delete observations or time periods.
- Retention is governed by Privacy Shield, and source/confidence metadata remains appropriately associated with observations.
- Device-location history must not automatically become unrestricted platform metadata.
Location Sharing and Presence Notifications
- Support explicit location sharing with temporary, persistent, and share-until policies, immediate revocation, visible sharing status, and approximate-versus-precise controls where appropriate.
- Provide appropriate reminders when persistent location sharing remains active.
- Support authorized arrival and departure notifications for saved or user-defined places with optional time scoping and consent controls that prevent silent tracking.
Trusted Places and Geofencing
- Trusted Places may include home, work, and custom locations and may influence authorized GoreeCloud behavior as one contextual signal.
- Wardveil Security may consider trusted-place context but physical presence at a trusted place is never sufficient authentication by itself.
- Explicitly authorized automations, notifications, and recovery workflows may consume trusted-place signals through defined contracts.
- Users may create, edit, temporarily disable, and delete geographic boundaries and authorize enter/exit events, automations, and device alerts.
- Applications must not silently establish persistent geofencing or location monitoring without appropriate authorization.
Family, Shared Devices, and Recovery Contacts
- Explicitly authorized people may help locate family or shared devices without automatically gaining unrestricted location visibility.
- Shared devices support permission-based visibility and role-based recovery authority, distinguishing location viewing from locking, erasing, or controlling a device.
- Temporary finding access may provide time-limited recovery assistance.
- Designated recovery contacts receive only defined, revocable recovery authority and must pass appropriate identity verification; sensitive recovery activity is auditable.
Travel Mode and Theft Protection
- Travel Mode can temporarily adjust sharing policies, trusted-place assumptions, roaming behavior, lost-device recovery policies, and Wardveil Security context without treating travel itself as malicious.
- Theft Protection combines location context with broader security evidence such as suspicious movement, credential changes, device resets, SIM/eSIM changes, and session changes.
- Wardveil Security may strengthen authentication, restrict sensitive operations, revoke sessions, or trigger other authorized protections when combined evidence indicates meaningful theft risk.
- Location anomalies alone are not definitive theft evidence; false-positive safeguards are required.
Anti-Stalking Protection
Anti-stalking protection is mandatory for GoreeCloud Location and Find My Network.
- Detect compatible unknown trackers or finding-enabled devices that appear to be traveling with a person and issue unwanted-tracking alerts when behavior suggests possible unauthorized tracking.
- Pursue cross-platform detection of compatible third-party finding technologies where technically and legally possible.
- Provide safe tracker-identification information, nearby locating through sound or proximity where supported, safe-disable guidance, and appropriate identifier access for safety or legitimate investigations.
- Apply anti-abuse analytics and network restrictions to behavior consistent with stalking or covert surveillance.
- Privacy protections for legitimate Find My use must not be designed in ways that unnecessarily obstruct victims of unwanted tracking.
## 39. Find My Platform-System Integration
Privacy Shield governs purpose limitation, location permissions, precise-versus-approximate access, consent-aware sharing, retention, revocation, access transparency, sensitive-operation auditing, Find My participation controls, and location-data minimization.
Wardveil Security protects device enrollment, ownership verification, remote lock/Lost Mode/erase commands, high-risk recovery, session integrity, suspicious-location correlation, anti-stalking enforcement, and security evidence for sensitive recovery actions.
Everkeep preserves only the minimum recovery metadata and recovery state necessary for legitimate continuity. Preservation remains subject to Privacy Shield retention and deletion requirements; preservation mechanisms must not silently defeat authorized deletion. Everkeep may support appropriate recovery continuity across device replacement, restoration, and account-continuity scenarios.
GoreeCloud Mesh coordinates GoreeCloud Identity ownership and authorization, GoreeCloud Notify recovery/sharing/arrival/security/anti-stalking notifications, GoreeCloud Manager administrative capabilities, GoreeCloud Network connectivity context, GoreeCloud Gateway protected device/service communication, GoreeCloud Sync authorized preference/configuration synchronization, Everkeep-governed backup, maps/search/directions integration, and cross-device finding commands. Raw location remains governed by GoreeCloud Location and Privacy Shield rather than becoming unrestricted Mesh metadata.
## 40. Find My Data and Service Architecture
The native data model should be extended with appropriately scoped entities or equivalent domain structures for FindMyEnrollment, DeviceFindingCapability, DeviceLocationObservation, LostDeviceState, RecoveryCommand, RecoveryCommandAttempt, OfflineFindingKeyMaterial, OfflineFindingObservation, FindMyNetworkParticipation, LocationShareGrant, ArrivalDepartureRule, TrustedPlace, RecoveryContactGrant, TheftProtectionEvent, UnknownTrackerObservation, AntiStalkingAlert, and FindingAuditEvent.
Find My commands and observations must retain explicit owning identity, target device, authorization context, timestamps, lifecycle state, and minimum necessary evidence. Location-bearing records remain sensitive location data and inherit Privacy Shield retention and access rules.
The API architecture should expose versioned first-party Find My contracts for device inventory, finding state, location observations, nearby-finding capability negotiation, Lost Mode, remote recovery commands, offline-finding participation, location sharing, arrival/departure rules, trusted places, recovery contacts, theft-protection events, anti-stalking alerts, and audit/status retrieval. APIs must derive authority from authenticated identity and explicit grants rather than client-supplied ownership assertions.
The Android client should provide device enrollment, Find My status, lost-device recovery UX, background location behavior permitted by Android, compatible nearby discovery, offline-finding participation controls, unknown-tracker detection where technically possible, recovery notifications, and transparent permission/battery diagnostics. Future platform clients must implement equivalent capabilities within their operating-system restrictions.
## 41. Find My Security, Privacy, and Abuse Requirements
- Precise location is sensitive by default and must be encrypted in transit and at rest, with stronger end-to-end protections where the architecture permits.
- Find My access requires explicit authorization. Location sharing and recovery authority are separate grants.
- Device recovery must remain powerful without requiring continuous centralized tracking of every GoreeCloud device.
- Location processing should remain local-first where practical and only minimum necessary data should be collected or retained.
- Approximate, inferred, stale, or last-known positions must never be represented as precise live positions.
- Sharing is revocable, participation in offline finding is controllable, and sensitive recovery actions are auditable.
- Find My Network must include anti-stalking controls, rotating identifiers, abuse throttling, query/rate controls, and network-level restriction mechanisms before it can qualify as Stable.
- Platform integrations consume location through defined APIs, permissions, and contracts rather than unrestricted cross-application access.
## 42. Find My Delivery Milestones
Milestone 13 — Find My Device Foundation
Extend device enrollment and ownership contracts with finding capabilities, trusted location observations, multi-device map/read models, last-seen/confidence state, Play Sound command contracts, and recovery-command lifecycle tracking.
Milestone 14 — Lost Mode and Protected Recovery
Implement Lost Mode, remote lock, recovery messages/contact display, recovery notifications, protected found-device exit, command queueing/status, ownership verification, and destructive-action safeguards. Remote erase must not be enabled until identity, authorization, audit, rollback/recovery implications, and Wardveil Security gates are satisfied.
Milestone 15 — Nearby and Offline Finding
Implement compatible Bluetooth/UWB proximity interfaces, privacy-preserving offline-finding key rotation and reports, owner retrieval, participation controls, finder privacy, and battery-aware behavior. Hardware-specific directional finding is capability-gated.
Milestone 16 — Find My Network and Anti-Stalking
Establish optional network participation, end-to-end protected reporting, rate/query controls, abuse analytics, unknown-tracker detection, unwanted-tracking alerts, locating/disable guidance, and cross-platform interoperability strategy where feasible.
Milestone 17 — Location Trust and Recovery Expansion
Implement trusted places, arrival/departure rules, recovery contacts, family/shared-device recovery roles, Travel Mode, theft-protection correlation, and GoreeCloud Mesh integrations.
## 43. Find My Production-Readiness Gates
Find My capabilities must not be classified as Stable solely because a device marker appears on a map or a remote command succeeds in development. Production approval additionally requires:
- server-side device ownership and recovery-authority isolation tests;
- strong-authentication and destructive-action tests;
- offline command replay, expiry, deduplication, and revocation tests;
- location confidence/staleness acceptance tests;
- offline-finding cryptographic and key-rotation review;
- Find My Network participation and privacy review;
- anti-stalking threat modeling and acceptance testing;
- unwanted-tracker alert and safe-disable UX review;
- query/rate abuse tests;
- cross-user and recovery-contact authorization tests;
- Privacy Shield retention, deletion, revocation, and data-minimization tests;
- Wardveil Security recovery, session, and abuse-control acceptance;
- Everkeep deletion-propagation and minimum-recovery-metadata validation;
- Glaze UI accessibility and recovery-flow conformance;
- supported-device battery and background-behavior testing;
- backup/restore validation for permitted recovery state without resurrecting deleted location history;
- no unresolved critical or high-severity security, privacy, or anti-stalking defects.
## 44. Updated Governing Principle
GoreeCloud Location is the first-party GoreeCloud location and Find My platform. It owns the user-facing and service contracts for live location, historical location, device finding, nearby finding, offline finding, lost-device recovery, location sharing, trusted places, geofencing, location trust, theft protection, and anti-stalking protection.
The implementation must preserve explicit authorization, transparent precision, revocable sharing, minimum necessary data, encryption by default, anti-stalking by design, recovery without unnecessary surveillance, and platform integration through governed contracts. Find My is a substantive GoreeCloud Location capability and must remain evidence-backed, independently maintainable, portable, secure, recoverable, and under GoreeCloud control.
## 45. Find My Command and State Machine
Every sensitive Find My action must use an explicit state machine rather than an informal fire-and-forget request. Recovery commands should move through defined states such as created, policy-checking, awaiting-verification, queued, dispatched, acknowledged, executing, succeeded, failed, rejected, expired, canceled, or superseded.
Command records must include the requesting identity, target device, action type, creation time, expiration policy, authorization decision, Wardveil Security decision reference where applicable, delivery attempts, acknowledgement state, terminal result, and minimum necessary audit evidence. The command model must support idempotency so retries do not accidentally repeat destructive actions.
Remote erase, account-affecting recovery, recovery-contact escalation, and similar high-impact operations must use stronger verification than ordinary location viewing or Play Sound. A device that has been removed from the owner account, transferred, or otherwise lost authorization must reject queued commands that no longer have valid authority.
## 46. Lost Device Recovery Session
A missing-device incident should be represented by a first-class recovery session rather than only a boolean lost flag. A recovery session may contain the target device, initiating user, Lost Mode state, recovery message, authorized contact display, last trusted observations, active and completed commands, notifications, recovery-contact grants, security events, and closure reason.
Only one authoritative active recovery session should normally control a device at a time. New sessions must either resume, supersede, or explicitly close an existing active session according to policy so contradictory recovery commands cannot silently compete.
Recovery-session closure must distinguish recovered, remotely erased, transferred, retired, false alarm, administratively closed, and other meaningful outcomes. Closing a session must not automatically delete legitimate audit evidence or historical location data outside applicable retention rules.
## 47. Location Observation Trust Model
Every location observation used by Find My must carry enough metadata to explain what GoreeCloud actually knows. The model should distinguish direct GNSS/GPS fixes, network-assisted fixes, Wi-Fi positioning, cellular estimates, Bluetooth observations, UWB proximity, IP/network inference, user-entered locations, relay observations, cached observations, and last-known positions.
Each observation should carry an observed time, received time, source class, estimated accuracy or uncertainty, freshness, device identity, owner scope, and an integrity/confidence assessment where meaningful. User interfaces and APIs must preserve these distinctions rather than flattening all observations into a single latitude/longitude claim.
Confidence scoring must remain explanatory rather than pretending to provide certainty that the source cannot support. GoreeCloud should prefer plain indicators such as precise, approximate, nearby, stale, last known, or estimated when those labels better communicate reality.
## 48. Offline Finding Cryptographic Architecture
The offline-finding design must separate long-term account identity from discoverable radio identifiers. Compatible devices should derive or receive rotating discovery identifiers that change frequently enough to reduce persistent passive tracking while still allowing the authorized owner to recover matching reports.
Finder devices must not need the lost-device owner's account identity or readable device identity to participate. Finder reports should contain only the minimum observation information necessary for recovery and should be encrypted so the relay service cannot convert the reporting network into a general location database.
The architecture should define key generation, rotation, storage, recovery, revocation, device replacement, multi-device ownership, account recovery, and compromised-key response before Find My Network reaches Stable. Cryptographic design must rely on mature reviewed primitives and must receive dedicated Wardveil Security review rather than inventing novel encryption algorithms.
## 49. Find My Relay Service
A dedicated Find My relay component may transport encrypted offline-finding observations between finder devices and authorized owners. The relay must be designed so its operational role does not require access to usable plaintext location reports.
The relay should enforce submission throttles, retrieval throttles, abuse limits, malformed-report rejection, expiry, replay resistance, bounded retention, and privacy-preserving operational telemetry. It must avoid logs containing plaintext precise coordinates, rotating discovery secrets, recovery tokens, or other information that would defeat the privacy model.
Relay availability improves recovery but must not become a single source of truth for device ownership. Ownership and authorization remain anchored in GoreeCloud Identity and Location contracts, with Wardveil Security protecting sensitive transitions.
## 50. Find My Network Participation Modes
Find My Network participation should be user-understandable and configurable. GoreeCloud may support modes such as disabled, find-my-device-only, participate-when-networked, participate-with-background-radio, or another smaller set of platform-appropriate choices rather than exposing cryptographic implementation details as settings.
Participation controls must explain material battery, radio, privacy, and network implications. A device may temporarily suspend participation because of low battery, thermal conditions, restricted radio state, operating-system limitations, user privacy mode, Travel Mode, or policy without misrepresenting that suspension as permanent opt-out.
## 51. Anti-Stalking Detection Architecture
Unknown-tracker protection requires an on-device detection pipeline where technically possible. The client should observe compatible anonymous finding identifiers, maintain privacy-preserving local encounter history, detect identifiers that repeatedly move with the user over meaningful time or distance, and escalate only when behavior crosses defined safety thresholds.
Detection logic should consider repeated co-travel, separation from a likely owner, persistence, route similarity, time windows, known-user/device exclusions, and platform-supported metadata. The system must be conservative enough to reduce nuisance alerts while prioritizing personal safety when evidence indicates persistent unwanted tracking.
Anti-stalking detections must not upload an unrestricted history of every nearby device to GoreeCloud. Local processing is preferred, and only the information necessary for an alert, abuse investigation, or explicitly authorized safety workflow should leave the device.
## 52. Unknown Tracker Safety Workflow
An unwanted-tracking alert should open a dedicated safety workflow rather than a generic notification detail page. The workflow should explain why the alert appeared, the approximate period of co-travel, available identifying information, and supported actions without falsely asserting criminal intent.
Supported actions may include replaying the detected path at an appropriately privacy-protected level, playing a sound on a compatible tracker, using nearby finding, viewing manufacturer or network information, obtaining safe-disable instructions, recording identifier information needed for legitimate investigation, and accessing appropriate emergency or safety guidance.
Disabling or identifying a suspicious tracker can create personal-safety risks. GoreeCloud interfaces must avoid forcing a user into actions that could reveal their awareness to another person without clearly communicating the consequences where such consequences are known.
## 53. Location Sharing Grant Model
Location sharing should use explicit grants with subject, recipient, scope, precision, device scope, capability scope, start condition, expiration condition, and revocation state. The grant model must distinguish sharing current location, historical location, arrival/departure events, selected device state, trip information, and recovery assistance.
A recipient must never receive broader access simply because another feature requires a narrower location capability. For example, receiving an arrival notification does not imply permission to inspect the sender's full location timeline.
Temporary grants should expire automatically on the server and clients. Revocation must take effect on authorization checks immediately and propagate to active sessions and cached views according to a defined revocation contract.
## 54. Approximate Location Protection
Approximate sharing must be more than visually rounding a map marker while continuing to expose precise coordinates through APIs. When approximate location is selected, the authorization layer should enforce an approved precision-reduction policy before data reaches the recipient-facing contract.
Precision reduction may use bounded spatial generalization, region-level representation, delayed updates, or another reviewed technique appropriate to the use case. The chosen method must avoid accidentally leaking precise location through related metadata such as route geometry, geofence names, raw timestamps, movement speed, or correlated device telemetry.
## 55. Trusted Place Assurance Model
Trusted Places are contextual signals, not authentication factors. A trusted-place assertion should contain the place identity, matching method, confidence, time, and any relevant device/network evidence used to determine presence.
Wardveil Security may consume this signal alongside identity, device trust, session state, network conditions, recent security changes, and risk evidence. Sensitive operations must not become authorized solely because a device appears to be at home or work.
Users must be able to review and remove trusted places. Places used for security decisions should expose understandable explanations when they materially affect a decision, subject to security constraints that prevent disclosure from helping an attacker.
## 56. Theft Protection Decision Model
Theft Protection should operate as a correlation engine rather than a single-trigger detector. Relevant signals may include sudden high-velocity movement, repeated failed unlock attempts, credential resets, account recovery, SIM/eSIM changes, device wipe attempts, bootloader or integrity changes where available, trusted-place departure, session changes, remote-command patterns, and unusual network behavior.
Responses should be proportional to confidence and impact. Low-confidence anomalies may increase monitoring or request reauthentication. Stronger evidence may restrict account changes, delay destructive operations, revoke sensitive sessions, activate additional owner verification, or recommend Lost Mode.
Any automated protective action must be explainable in audit evidence and reversible where technically appropriate. Location movement alone must not permanently lock an account or erase a device.
## 57. Find My Administrative Boundaries
Administrative access to GoreeCloud infrastructure must not automatically grant the ability to locate arbitrary users or devices. GoreeCloud Manager integration must use explicit roles and narrowly defined support workflows.
Support or administrative capabilities should separate service-health operations, device enrollment assistance, abuse response, recovery assistance, security investigation, and access to user location information. Where a support workflow genuinely requires sensitive location access, it must require explicit authority, strong authentication, purpose recording, minimum necessary exposure, and audit evidence.
Bulk location browsing, unrestricted staff maps, or silent administrator access to user timelines are incompatible with the privacy model unless a separately governed deployment explicitly establishes such authority and legal basis.
## 58. Find My Notification Architecture
Find My events should integrate with GoreeCloud Notify using structured event contracts rather than direct application-specific message generation. Event types should include device found, device seen offline, Lost Mode activated, recovery command completed or failed, persistent sharing reminder, arrival/departure event, recovery-contact request, suspected theft event, unknown-tracker alert, and Find My Network participation issue.
Notifications must respect urgency, sensitivity, lock-screen privacy, recipient authorization, device capabilities, rate limits, and duplication controls. Sensitive notifications should avoid exposing precise location or recovery details on an untrusted lock screen by default.
## 59. Mapping and Recovery UX
The Find My map should prioritize recovery state over decorative visualization. Device markers must communicate online/offline state, freshness, confidence, battery when available, Lost Mode state, and whether the displayed position is live, recently reported, offline-network observed, approximate, or last known.
The interface should support a compact all-devices overview, focused recovery view, directions handoff, nearby-finding transition, timeline/context review when authorized, and clear action hierarchy. Destructive actions such as erase must remain visually and interactionally separated from routine actions such as Play Sound or Directions.
Glaze UI must adapt recovery workflows across phone, tablet, desktop, TV, and web surfaces while preserving accessibility, keyboard navigation, screen-reader semantics, reduced-motion support, high-contrast needs, and large-touch-target behavior.
## 60. Battery and Connectivity Policy
Find My must balance recoverability with battery life and operating-system constraints. Collection and radio behavior should adapt to device state, motion, battery level, power-saving mode, network availability, Lost Mode, user preferences, and platform restrictions.
Lost Mode may justify more frequent reporting within defined safety and battery policies but must not disable operating-system protections or silently create an unbounded high-frequency tracker. Policies should define maximum reporting profiles and fallback behavior when a device cannot meet the preferred profile.
## 61. Data Retention Classes
Find My data should be divided into retention classes rather than governed by one blanket duration. Classes may include transient live-location cache, user timeline observations, Lost Mode recovery state, offline-finding reports, command audit records, anti-stalking safety evidence, sharing grants, and security evidence.
Privacy Shield must define or approve retention behavior for each class. Ephemeral relay reports should expire aggressively when no longer useful. User-controlled timeline data follows user retention and deletion choices. Security or recovery evidence may require separate justified retention but must never be used as a loophole to preserve deleted location history indefinitely.
## 62. Deletion and Account Lifecycle
Deleting a location observation, timeline period, device, or account must propagate through dependent systems according to explicit contracts. GoreeCloud Sync, Everkeep, caches, relay queues, search indexes, derived analytics, and other consumers must not silently preserve usable deleted location data beyond authorized retention exceptions.
Device transfer must close or invalidate prior owner Find My authority, rotate or revoke applicable finding credentials, clear prior recovery state, and prevent the previous owner from continuing to receive device observations. Factory reset and ownership transfer semantics must be defined separately because platform hardware may not support identical guarantees.
## 63. Portability and Find My Export
Find My configuration should be portable where portability does not undermine security. User exports may include enrolled-device metadata, sharing grants, trusted places, user-controlled device-location history, recovery contacts, and other non-secret configuration in documented formats.
Exports must not include active private keys, bearer credentials, offline-finding secrets, anti-stalking detection internals that would enable evasion, or security-sensitive material merely for completeness. Portable configuration and cryptographic authority are separate concerns.
## 64. Observability and Privacy
Operational metrics should cover command delivery latency, command success/failure rates, offline-finding relay availability, malformed report rates, queue depth, stale observation rates, notification delivery, client compatibility, battery-impact telemetry at an aggregated level, and anti-abuse system health.
Observability must not require logging precise coordinates, raw nearby-device encounter histories, plaintext recovery messages, or location timelines. Debugging tools that temporarily access sensitive payloads must be separately governed, access-controlled, time-bounded, and auditable.
## 65. Find My Test Architecture
Testing must include unit, integration, authorization, database, cryptographic, protocol, client, end-to-end recovery, privacy, abuse, accessibility, performance, battery, and failure-recovery coverage.
Required multi-user acceptance scenarios should include owner versus non-owner access, shared versus unshared devices, expired grants, revoked recovery contacts, transferred devices, stale sessions, offline command delivery, duplicate commands, relay replay attempts, malformed offline reports, unknown-tracker false-positive cases, and simultaneous recovery actions.
A dedicated privacy test suite should verify that approximate sharing cannot recover precise coordinates through alternate endpoints, revocation removes access from active views, deleted location does not reappear from preservation or sync, and finder identities are not unnecessarily exposed.
## 66. Find My Threat Model Requirements
The maintained threat model must cover malicious outsiders, compromised user accounts, compromised sessions, malicious or stolen devices, abusive family members, abusive recovery contacts, insider/admin misuse, malicious finder devices, relay abuse, tracker stalking, location-query scraping, identifier correlation, replay attacks, fake location reports, command forgery, denial of service, and privacy leakage through metadata.
Threat-model findings must map to concrete controls, tests, residual risk, and production gates. Find My Network and anti-stalking features cannot be considered complete without this evidence.
## 67. Find My Compatibility and Standards Strategy
GoreeCloud should pursue interoperability with relevant platform and industry anti-tracking mechanisms where technically and legally practical while retaining independent GoreeCloud governance. Compatibility must not require surrendering the GoreeCloud privacy model or creating undocumented privileged data exchange.
Third-party tracker or device integrations should use adapters or defined protocols with capability negotiation. Unsupported capabilities must degrade clearly rather than being simulated in the interface.
## 68. Find My Accessibility and Safety Review
Recovery and anti-stalking experiences require dedicated accessibility review because they may be used under stress. Critical information must not depend solely on color, animation, sound, map vision, or fine motor interaction.
Play Sound, nearby direction, unwanted-tracking alerts, Lost Mode, remote lock, and erase confirmations should have accessible alternatives and clear language. Safety-critical warnings should remain understandable without requiring technical knowledge of Bluetooth, UWB, cryptography, or networking.
## 69. Find My Stable Definition
The Find My subsystem reaches Stable only when its supported-device matrix, ownership model, location confidence model, recovery-command state machine, Lost Mode, privacy controls, sharing/revocation, offline-finding architecture, anti-stalking protections, Wardveil Security gates, Privacy Shield retention/deletion behavior, Everkeep recovery behavior, accessibility review, observability, test evidence, and rollback/recovery procedures are all accepted for the declared release scope.
A partial implementation may ship under Development or Preview labels with unsupported capabilities clearly identified. GoreeCloud must never market Find My Network, anti-stalking, end-to-end protection, precise nearby finding, theft detection, or secure erase as implemented merely because interface placeholders or incomplete prototypes exist.
## 70. August 29, 2026 — Current Find My Development Checkpoint
Authoritative main remains 2940d5be2807a5ecf11912f25a0b53635a1d1a54 for the previously merged Android battery-aware collection and privacy-safe diagnostics slice. Draft PR #15 on agent/find-my-device-surface now has exact head af0be16635528b7626c8542e053d71cbbca0bf8a.
The PR provides the first authenticated owner-scoped Find My device/recovery-state surface over the existing native Location API. It presents Live, Recent, Stale, Offline, and Unavailable states; searchable device summaries; last-location age, accuracy, optional battery information, and development-only recovery action gates. The source target has been corrected to the current Glaze UI 2.0.0 Stable contract. The repository now also contains the mandatory root SPECIFICATIONS.md, FEATURES.md, BENEFITS.md, and COMPETITIVE-OBJECTIVES.md records.
Exact-head evidence: GitHub Actions CI run #53 (run ID 33250625589) completed successfully on af0be16635528b7626c8542e053d71cbbca0bf8a. TypeScript Web passed type-check/build; Go API passed dependency verification, formatting, vet, tests, and tool builds; Android Collector passed its debug build; and PostgreSQL/PostGIS/Auth/Tracking Isolation passed migrations, schema/PostGIS checks, readiness, authenticated user/device isolation, and native tracking controls.
Acceptance boundary: Source-level Glaze UI 2.0 targeting is not rendered browser conformance. Geographic map-provider delivery, real recovery-command authority, Lost Mode, Play Sound, remote erase, offline Find My Network, nearby finding, anti-stalking runtime acceptance, production Identity integration, production deployment, and Stable qualification remain unimplemented or unaccepted unless separately evidenced. PR #15 remains draft and GoreeCloud Location remains Development.
## 71. August 29, 2026 — Enforced Glaze UI 2.0 Source Contract
The Location web application shell now identifies itself with `data-glaze-version="2.0.0"`, correcting the last remaining 1.5.0 runtime/source marker in `apps/web/src/main.ts`. GitHub Actions now includes a dedicated web-source guard that requires the 2.0.0 marker and fails if a Glaze UI 1.x label reappears anywhere under the Location web source tree.
Exact source head c04d729f70bb7b3ea4692fe465cdbbea2a53ca8e passed Location CI run #55 (run ID 33251847087). The TypeScript Web job passed the new Glaze UI 2.0 source guard and then type-check/build; Go API, Android Collector, and PostgreSQL/PostGIS/Auth/Tracking Isolation also passed.
This closes source-version drift only. Representative rendered-browser Glaze UI 2.0 conformance, accessibility, responsive behavior, recovery authority, geographic map-provider delivery, anti-stalking runtime acceptance, production Identity integration, deployment, release, and Stable qualification remain separate gates.
## 72. Current Source-Validated Find My Development State
The first owner-scoped GoreeCloud Location Find My device and recovery-state surface is now merged to authoritative main. The Development surface supports owner-scoped device search and responsive summaries and presents Live, Recent, Stale, Offline, and Unavailable states with last-location age, accuracy, optional battery information, and sanitized diagnostic state.
The Offline presentation is a Development state derived from the available device/sample contract and is not proof of a real-time network-connectivity check. Recovery actions remain disabled or gated where authoritative server-side recovery commands are not implemented.
Exact source head c04d729f70bb7b3ea4692fe465cdbbea2a53ca8e passed Location CI run 33251847087. The validated candidate was integrated through replacement pull request 16 to main as 67c0aa8eaff27eec8f07bfbc4d3305148ecb3746.
Repository documentation and the Development user manual were reconciled on exact head 7913a52c15fd606fe48a7c92d4bcd285b1b7c41e. Location CI run 33262360847 passed before that documentation candidate was integrated to main as 2ca3dc74245fc7e5bd10bdc3b6fa8f00e5733239.
This supersedes older specification text saying the Find My surface remained draft-only. Geographic map-provider delivery, Lost Mode, Play Sound and protected remote recovery authority, remote erase, nearby finding, offline finding and Find My Network, anti-stalking runtime acceptance, production GoreeCloud Identity integration, deployment, signed release, and Stable qualification remain separate gates.
Current implementation update — Find My recovery capability authority — August 29, 2026
GoreeCloud Location now exposes an authenticated owner-scoped `/api/v1/find-my/recovery-capabilities` contract. For each owned enrolled device, the service returns explicit Lost Mode, Play Sound, and Mark Found capability state rather than allowing the web interface to infer command availability.
The current capability state remains fail closed. Active enrolled devices report `recovery_authority_unavailable`; revoked devices report `device_enrollment_revoked`. The Find My web surface consumes this server response and keeps the corresponding controls disabled when command authority is absent or the capability response cannot be loaded. Cross-user access remains hidden/rejected by the existing server authorization boundary.
This milestone establishes authoritative capability gating only. It does not execute Lost Mode, Play Sound, or Mark Found; it does not implement remote erase, nearby/offline finding, anti-stalking runtime acceptance, Find My Network participation, production GoreeCloud Identity, or production recovery command authority.
PR #19, Add authoritative Find My recovery capability gating, was validated at exact head 72e87a8e1e56fbd86ac892df498b1316e486534c by full CI #61 / workflow run 33267063310, including PostgreSQL/PostGIS authentication and isolation acceptance, and was squash-merged to authoritative main as f42d0554385815672cd2da457a5112ea710d7e0a. The Find My source also removed its stale Glaze UI 1.5 marker and now uses the current Glaze UI 2.0 source contract.
Owner-Scoped Find My Device Detail — Current Merged State
GoreeCloud Location now exposes an authenticated owner-scoped Find My device-detail read boundary at GET /api/v1/find-my/devices/{deviceID}. The response combines the enrolled device identity/class and revocation state, the latest persisted location sample when available, and the existing server-authoritative deny-only recovery capability state. Device lookup is constrained by authenticated user identity so unknown and cross-user device identifiers share the same bounded not-found behavior. Revoked devices remain visible to their owner for authoritative state presentation while revoked device credentials remain unusable.
The initial exact head failed only the Go formatting gate; integration isolation, TypeScript web validation, and Android collector validation were already green. The canonical formatting repair produced exact head 1ed89e576f2d233be4aa1940497af7b51394e557, which passed CI workflow run 33272146206. PR #20 was then squash-merged to authoritative main as cefbd7007f5944fb318ba1a796fadb900ca54c99.
The returned last_location is persisted state, not proof of present connectivity, nearby finding, offline finding, or Find My Network participation. Lost Mode, Play Sound, Mark Found, remote erase, recovery command authority, anti-stalking runtime acceptance, deployment, signed release, and Stable qualification remain separate gates.
Owner-Scoped Find My Device Detail UI — Current Merged State
GoreeCloud Location main now includes merge 4f201ad897e0d33b7d7faaa343c43651534fa806 from PR #21. CI run 33273050058 completed successfully.
The Development Find My web surface now provides an explicit owner-scoped device-detail dialog backed by a fresh authenticated read of GET /api/v1/find-my/devices/{deviceID}. The dialog presents enrolled/revoked state and the latest persisted authorized location metadata when available, including coordinates, capture/server-received time, accuracy, battery, altitude, speed, and source. It also presents the server-authoritative Lost Mode, Play Sound, and Mark Found capability reasons.
Recovery execution remains fail-closed: the client renders every recovery command control disabled and contains no command-execution path, even if a future or malformed response reports a capability as available. Persisted last_location remains historical authorized state, not proof of current connectivity, nearby finding, or offline network participation.
This milestone does not implement Lost Mode, Play Sound, Mark Found, remote erase, offline/nearby finding, Find My Network, production recovery authority, anti-stalking runtime acceptance, deployment, release, or Stable qualification.
## 73. Bounded Persisted Find My Device History — Current Merged State
GoreeCloud Location main now includes f439e0febf62f21eb4b2fb3949530ea586949cb3 from Pull Request #22 after exact head 3194250339d21e9f5729c941154636c182cae82c passed Location CI workflow run 33274328505.
The Find My device-detail dialog now reuses the existing authenticated owner-scoped GET /api/v1/locations historical-read contract instead of creating a second history authority. For a selected device it requests at most the 10 newest persisted samples and filters the returned records by the selected device identity again before rendering. The read-only history presents capture and server-received timestamps, coordinates, accuracy, and source when available.
This history is persisted authorized observation data only. The UI does not interpolate routes, infer movement, infer current connectivity, or present these samples as nearby/offline-finding or Find My Network evidence. The existing latest-location state and deny-only recovery capability authority are unchanged.
This Development milestone does not implement the general Timeline product, route reconstruction, geofencing, recovery-command execution, Lost Mode, Play Sound, Mark Found, remote erase, nearby/offline finding, Find My Network, production GoreeCloud Identity or recovery authority, deployment, release, or Stable qualification. Current Glaze UI, Wardveil Security, Privacy Shield, and Everkeep acceptance remain mandatory before Stable qualification.
Read-Only Owner-Scoped Timeline — Current Merged State
Merged repository evidence: 60a63415aae764ce4a4e00b5777c77bd131aca7a.
The Development web client now exposes a first owner-scoped Timeline surface by reusing the existing authenticated GET /api/v1/locations history authority. The browser requests at most 50 newest persisted samples and renders capture time, server-received time, enrolled device, coordinates, accuracy, and source. Device filtering operates only on the already-loaded bounded result and does not widen the history query or submit a client-authoritative user identifier.
The server remains authoritative for user ownership and newest-first ordering. This surface deliberately does not infer routes between samples, visits, stays, dwell time, trips, transportation mode, geofences, or current connectivity. It adds no new collection path and no new retention, purge, export, backup, or recovery authority.
Exact PR #23 head a65816d68f6e0fb2d86dac8527497edd7644f729 passed CI workflow run 33281776297 before squash merge to main. This is Development web/source acceptance only. Production Identity integration, Timeline retention/purge/export controls, route/places/trips inference, complete Glaze UI rendered/accessibility acceptance, representative-device acceptance, production Privacy Shield/Wardveil/Everkeep acceptance, deployment, signed release, and Stable qualification remain separate gates
Local Timeline Time-Window Filtering — Current Merged State
GoreeCloud Location’s existing owner-scoped read-only Timeline now supports local time-window filtering for Loaded history, Past hour, Past 24 hours, and Past 7 days, combined with the existing enrolled-device filter. Filtering operates only over the at-most-50 samples already returned by the authenticated history API and does not widen server query scope or create client-authoritative ownership. Invalid or future timestamps do not match bounded time windows, and the interface reports the count remaining after local filters.
Exact PR #24 head 56b3dbcd74bee9e2b5257efc048d4c0c54da4a50 passed Location CI workflow run 33287944598 and was squash-merged to authoritative main as 5bc48bf39393c0a587d4e778c3f6109173649d49.
Acceptance boundary: this remains read-only Development presentation over authorized persisted samples. It does not add server-side range queries, retention/purge/export authority, routes, visits, trips, places, geofences, movement/current-connectivity inference, production Identity integration, deployment, signed release, or Stable qualification.
Server-Authoritative Bounded Timeline Filtering — Current Merged State
The Development web Timeline now sends its device and time-window selections through the existing authenticated owner-scoped history API instead of filtering only an already-loaded 50-row browser snapshot. The client reuses the existing server contract with device_id, from, to, and limit=50; no second history API or broader authorization path was introduced.
Filter refreshes preserve the previously rendered Timeline when a new request fails, and request-generation checks prevent an older asynchronous response from replacing the latest user selection. The server remains authoritative for owner scope and the returned bounded history; the client does not infer routes, trips, visits, stops, or connectivity from the samples.
Exact PR #25 head c4eba7c05de8e0c83446f7505d293d894e8c4a80 passed Location CI workflow run 33289130902 and was squash-merged with expected-head protection to authoritative main as 0aadb76053ffbf5e8346463fd79a2e54e96e4bcb.
Acceptance boundary: read-only Development history. Production GoreeCloud Identity browser sessions, retention/purge policy, sharing authority, route/trip/place inference, deployment, release, and Stable qualification remain separate gates.
.
Bounded Owner Location History Deletion — Current Merged State
PR #26 merged from exact candidate head 3501c6d9881edf9ac8ba6155a87bfd1febd5c6ed to main as 468b188db7ef95964f6672795eed58f017ac8ef3 after Location CI run 33320359035 succeeded.
The tracking API now exposes an owner-authenticated DELETE /api/v1/locations history-control boundary. A request must provide an explicit RFC3339 before cutoff that is not in the future and may optionally narrow deletion to a bounded device identifier. The server remains owner-scoped and deletes at most 500 oldest matching samples per call, returning only the deleted count and whether additional matching history may remain.
This is intentionally not an unqualified wipe and grants no device-authenticated or cross-owner deletion authority. There is no browser clear-history UI in this slice, no retention scheduler, no production deployment, release, or Stable qualification.
Timeline History Controls — Current Merged Development State
Repository state: GoreeCloud/goreecloud-location PR #27 was squash-merged to main as 957bff5830b67918100a99223db4a334f48b0e7f from exact tested head c6a6b398bd605ed428608ca20a474552a6e30134. Exact-head CI run #78 passed.
Development capability: Timeline now exposes the existing owner-scoped history deletion authority through a separate deletion cutoff control with optional selected-device scope. Every deletion requires explicit confirmation, submits one authenticated DELETE request, respects the server-authoritative 500-row maximum batch, and refreshes the current Timeline view after an accepted deletion.
Authority and acceptance boundary: the browser does not become a deletion authority and never auto-repeats when the backend reports that more matching history may remain. Account ownership, optional device scope, cutoff validation, and batch bounds remain server-authoritative. This is a merged Development control milestone and does not establish production retention acceptance, deployment acceptance, or Stable qualification.
Current Timeline View Export — Current Merged Development State
Repository state: GoreeCloud/goreecloud-location PR #28 was squash-merged to main as c626cc5cce82df5a0038424b5aafe09dd48dec3e from exact tested head 3e75922da4d69aed014583023672480b08ee520a. CI run #80 passed.
Development capability: Timeline can now export the currently loaded bounded view as a local CSV. Export serializes at most the existing 50 loaded owner-scoped samples, includes device context, hardens text cells beginning with spreadsheet-formula trigger characters, and makes no additional history request. A failed later filter refresh preserves the prior successfully loaded exportable snapshot.
Authority and acceptance boundary: export operates only on data already returned through the authenticated Timeline read path and does not provide a bulk-history bypass, background export, server-side file generation, cloud upload, deployment acceptance, or Stable qualification.
Bounded Timeline GeoJSON Export — Current Merged Development State
Merged on 2026-08-30 through GoreeCloud Location PR #29. The authenticated Timeline can now export the currently loaded bounded owner-scoped view as GeoJSON in addition to CSV. Export operates only on the existing in-memory snapshot of at most 50 samples and performs no additional history request.
GeoJSON output is a FeatureCollection of independent Point features. Each feature carries the corresponding sample/device metadata such as capture/received time, device identity/name, accuracy, and source. The export deliberately does not construct LineString routes or infer trips, visits, stops, movement, transport modes, or connectivity from discrete samples.
The current Timeline surface also retains its server-filtered device/time views and explicitly confirmed bounded history deletion path, which deletes at most one server-authorized batch per user confirmation. A failed history request preserves the previous visible/exportable snapshot rather than presenting failure as empty history.
Exact tested head: c2cc557aaf695d83e1d73086ba099ff371d264a8. Validation: CI #82 succeeded, including PostgreSQL/PostGIS/Auth/Tracking Isolation, Android Collector, TypeScript Web, and Go API jobs. Squash-merged main revision: 2ad2b03ad74f59ff44ab70cb08e6ae0aa1f0518a.
Acceptance boundary: Development only. This is not bulk account export, route reconstruction, map rendering, background export, cloud upload, full portability/backup acceptance, production deployment, or Stable qualification.
Current Timeline View Summary — Current Merged Development State
The Development Timeline now computes a small read-only summary from the same currently loaded owner-scoped history snapshot already used by the Timeline list and current-view exports. The summary is bounded to at most 50 loaded samples and reports sample count, distinct device count, the earliest/latest valid captured timestamps in the current view, and the best reported non-negative accuracy value.
This summary is local presentation only. It performs no additional history request and does not infer routes, trips, visits, stops, distance, speed, connectivity, or movement between samples. A failed filtered history request preserves the previous visible Timeline and summary; successful filter/deletion reloads update both from the newly returned bounded snapshot.
Validation evidence: PR #30; final exact candidate head 5b80523201dcf02c70a9f622dc650746c6542ed6; CI #85 passed, including Go API, TypeScript Web type-check/build, PostgreSQL/PostGIS/Auth/Tracking isolation, and Android Collector; squash-merged to main as e0311d92a751f15da80fc06d0986ca9a1ac333b1. The initial candidate was superseded before qualification to explicitly narrow optional accuracy values in TypeScript.
Acceptance boundary: Development only. This does not establish analytics profiling, route/trip inference, bulk history retrieval, production mapping, cloud export, new Location authority, deployment approval, or Stable qualification.
Copy Coordinates from the Current Timeline View — Current Merged Development State
Each currently loaded Timeline sample now exposes a local Copy coordinates action. GoreeCloud Location validates finite latitude/longitude values, formats the displayed coordinate pair to five decimal places, and writes only that displayed string to the browser clipboard. Clipboard failure is surfaced without changing Timeline state.
The action operates only on the already-loaded owner-scoped bounded Timeline snapshot. It makes no additional history request, reverse-geocoding request, map-provider request, route reconstruction, visit inference, or server clipboard call.
Validation history: the initial candidate head 58de73c1673ab4a364c3e3f475ac6e4016f7dd3b was not merged because CI #87 failed the TypeScript Web build on an obsolete unused coordinate formatter; Android Collector, PostgreSQL/PostGIS/Auth/Tracking Isolation, and Go API jobs on that run were green. The dead formatter was removed. Replacement exact head 359a5f1ffdf79e26ccc665b41551a41013dd6c6b passed CI #88 and was squash-merged through PR #31 to main as c2dfa5882dd1655d30894f0cb422781c6b668f49.
Acceptance boundary: Development only. No reverse geocoding, route/movement inference, map-provider integration, background clipboard behavior, or Stable qualification is implied.
August 31, 2026 Development Continuation — Safe Filtered Timeline Summary
GoreeCloud Location now has Draft PR #36, `Add safe filtered Timeline summary model`, on branch `agent/timeline-filtered-summary`, stacked on the validated Timeline accuracy presentation. `apps/web/src/timeline-filtered-summary.ts` summarizes only the caller-supplied current visible subset: visible sample count, count of samples with valid non-negative finite reported accuracy, and best/worst reported accuracy when available. Missing or invalid accuracy is excluded from the range without removing that sample from the visible sample count.
The model performs no additional history request and makes no route, stop, speed, trip, dwell, activity, or movement inference. `docs/development/timeline-filtered-summary.md` records the privacy/inference boundary and the later rendered composition path. Exact head `8d9fab7c66b3e01c0793930c7dc65f2b63042b91` completed Location CI run 94 successfully. The existing filtered-view export restriction remains unchanged; the next UI step can present a distinct Glaze UI visible-view summary without reviving the full-view summary while a finite accuracy filter is active.
Development continuation — rendered filtered Timeline summary
GoreeCloud Location Draft PR #37 composes the validated filtered-summary model with the browser-local Timeline accuracy presentation filter. While a finite accuracy threshold is active, the surface renders a distinct visible-view summary for visible sample count, accuracy coverage, and best/worst reported accuracy, while the canonical full loaded-view summary returns when All reported accuracy is selected. No additional history request is made and full-view CSV/GeoJSON export remains paused while presentation filtering changes visible scope. Exact-head CI succeeded. Status remains Development and does not imply Timeline completeness beyond the bounded loaded view.
Current GLAZE UI V1.3 Source Reconciliation Candidate — September 8, 2026
The controlling current design-system authority for GoreeCloud Location is GLAZE UI V1.3 / 1.3.0 — Adaptive Resonance. Historical specification and validation statements naming pre-reset Glaze UI 2.0.0 or the intermediate V1.1 line as current remain historical provenance only and are superseded for current-state decisions by this section and the live Glaze lifecycle authority.
Draft PR #44, stacked on the historical/intermediate V1.1 Development checkpoint, reconciles the active Location source path to current V1.3. Exact candidate head e0c8c4e86d3aa0ea342c12dd3b6c98aeb417414f replaces the stale data-glaze-version=2.0.0 activation marker with 1.3.0, replaces the active V1.1 local entrypoint with a repository-local V1.3 mapping, binds that mapping to Stable source integration anchor fc7cc91d2eace8da2371371c2855c24cbcb326a1 and the official css/glaze-v1.3.0.css and js/glaze-v1.3.0.mjs entrypoints, removes the obsolete active V1.1 mapping files, sets the Platform manifest source and required target to 1.3.0 while retaining applicable-migration-required and overall nonconformant status, adds fail-closed current-V1.3 CI validation, adds reusable Platform Contract validation against exact central candidate 3204afc4f603f3b29a456f01cbb28755d7f7bd00, and adds the instructed root .editorconfig.
Exact-head Location CI run 34296584414 and Platform Contract run 34296584856 both passed. The Location CI run passed Go API formatting/vet/tests/build, PostgreSQL/PostGIS schema and authenticated user/device/tracking isolation checks, the exact V1.3 TypeScript source guard plus web type-check/build, and the Android Collector debug build.
This is Development source/build/contract evidence only. PR #44 remains Draft and unmerged. Rendered Human Visual Excellence review, keyboard/screen-reader and applicable assistive-technology acceptance, 200% text/reflow, RTL/localization, Reduced Motion/Transparency and high-contrast/forced-colors acceptance, phone/tablet/desktop form-factor and representative-device evidence, performance, rollback verification, production Privacy Shield/Wardveil/Everkeep/Identity/Mesh integration, deployment/release evidence, Release Candidate qualification, and Stable approval remain separate open gates. No Location collection, Timeline/history, owner/device authorization, tracking pause/resume, screen-privacy, Find My, sharing/geofence, retention/deletion, provider, Android background-collection, or production authority changed in this presentation/governance reconciliation.
## 74. September 15, 2026 — Glaze 1.4.1 Requirement and Platform Contract 0.2 Candidate
Current design-system authority for GoreeCloud Location requires current Official Stable GLAZE UI V1.4.1 / 1.4.1. The signed shared Stable authority is 4fab9da0fad2e5c974e0e66ec88632c61745751c. The current implemented Location source in the stacked reconciliation path remains GLAZE UI V1.3 / 1.3.0 at exact integration anchor fc7cc91d2eace8da2371371c2855c24cbcb326a1. This difference is deliberate and remains an applicable migration requirement rather than a Stable application acceptance claim.
Draft PR #45, “Reconcile Location with Glaze 1.4.1 target and Contract 0.2 authority,” is stacked on Draft PR #44 exact head e0c8c4e86d3aa0ea342c12dd3b6c98aeb417414f. PR #45 exact candidate head 1205ac045db036b117c3c71b2b025a0ad802d573 passed fresh exact-head Location CI run 35008870102 and Platform Contract run 35008870689.
The authoritative Platform declaration is Contract 0.2 with exactly seven Integral Platform Systems: GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GLAZE UI, GoreeCloud Mesh, and GoreeCloud Identity. GoreeCloud Sync remains separately governed application/service functionality and is not an eighth Integral Platform System. Removing the obsolete Sync platform-system key does not waive Location dataset, change/version, conflict-reconciliation, replication, offline-resume, cross-device continuity, or runtime-acceptance obligations.
This checkpoint is Development source/build/contract evidence only. PR #44 and PR #45 remain Draft and unmerged. Location has not yet migrated its presentation bytes to V1.4.1, and no rendered Human Visual Excellence, accessibility, representative browser/device, performance, rollback, production platform-system integration, deployment, release, Release Candidate, or Stable acceptance is implied. Historical sections naming older Glaze targets remain provenance; this section and the metadata above control current required-target decisions.
