# GoreeCloud Location — Features

Status vocabulary: **Accepted main**, **Stabilization candidate**, **Planned**, or **Blocked by prerequisite**. Candidate status is not production or Anchor acceptance.

## Accepted main / existing Development foundation

- Authenticated user identity boundary and device enrollment/revocation.
- Device-scoped tracking credentials.
- PostgreSQL/PostGIS geospatial persistence with multi-user/device isolation tests.
- Device-authenticated location ingestion with idempotency and bounded validation.
- Owner-scoped live and history reads.
- Server-enforced tracking pause/resume.
- Responsive Live experience with sample age, accuracy, optional battery, stale/no-location states, and refresh.
- Owner-scoped Timeline API with bounded device/time filtering.
- Explicit bounded history deletion.
- Local CSV and GeoJSON export of the currently loaded bounded Timeline snapshot.
- Development Find My device-state surface and server-authoritative recovery-capability gate.
- Native Android collection/retry foundations.

## Current stabilization candidate

- deterministic newest/oldest ordering for the loaded Timeline snapshot;
- rendered Timeline order control;
- reported-accuracy presentation filter with bounded choices;
- filtered-summary model and visible-view summary;
- explicit loaded/visible/hidden scope truth;
- explicit accuracy-filter reset with focus restoration;
- presentation-only Timeline screen privacy mode that hides precise coordinate text, disables coordinate copy, and pauses coordinate-bearing export while active;
- repository-local GLAZE UI V1.3 / 1.3.0 mapping with 48 px targets, focus treatment, Light/Dark/Deep Dark structure, Reduced Transparency, Reduced Motion, and forced-colors fallbacks;
- current GLAZE UI V1.6 / 1.6.0 migration declaration without relabeling V1.3 source bytes;
- exact-head CI and Platform Contract 2.0 validation;
- explicit GoreeCloud Policy and GoreeCloud Observability blocked-state evaluation.

## Development boundaries

The Timeline ordering/accuracy/privacy features operate on already-authorized bounded data and do not create new location-history authority, route/trip/visit inference, retention authority, or provider requests.

Screen privacy is a shoulder-surfing presentation control. It does not delete or redact server data, clear browser memory, replace OS screen protection, or satisfy Privacy Shield retention/deletion requirements.

GLAZE UI is presentation only. It does not change collection, history, tracking pause/resume, Find My, sharing, geofence, Identity, Policy, Observability, Security, continuity, or Sync authority.

## Planned / incomplete

- substantive GLAZE UI V1.6 migration and Location-specific rendered/accessibility/device/performance acceptance;
- production GoreeCloud Identity browser/device sessions and credential lifecycle;
- replaceable geographic map provider and rendered map acceptance;
- Android encrypted queue, retry/backoff, retention, permission-safe recovery, battery behavior, and physical-device acceptance;
- multi-user/family sharing and revocation workflows;
- places, trips, timeline playback, geofences, and insights;
- Find My recovery commands, nearby/offline finding, trusted places, and recovery contacts;
- anti-stalking and abuse-prevention runtime acceptance;
- complete-account export/import, retention management, Everkeep backup/restore, and migration validation;
- GoreeCloud Sync dataset/version/conflict/offline-resume/cross-device contracts;
- Policy and Observability runtime integration;
- deployment, rollback, release provenance, and Anchor qualification.

## Evidence rule

A capability may be described only at its verified evidence level. A green build, metadata declaration, UI label, stale branch, or provider seam must never be upgraded into production or Anchor truth without the applicable exact-revision evidence.
