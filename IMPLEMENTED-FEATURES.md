# GoreeCloud Location — Implemented Features

**Authority:** Repository-native implemented-feature record.  
**Lifecycle:** Forge  
**Deployment state:** Development

This file distinguishes accepted repository behavior from unmerged candidate work. Candidate source is not accepted-main, deployment, release, production, or Anchor evidence.

## Accepted Development foundation

- Go HTTP service with authenticated user and device boundaries.
- PostgreSQL/PostGIS persistence with tested multi-user ownership isolation.
- Device enrollment, revocation, device-scoped credentials, and server-enforced tracking pause.
- Device-authenticated location ingestion with idempotency and bounded validation.
- Owner-scoped live and historical location reads.
- Responsive Live web experience with last-known state, age, accuracy, optional battery, stale/no-location states, and refresh.
- Owner-scoped Timeline queries with bounded device/time filters.
- Explicitly confirmed owner-scoped Timeline deletion using a server-bounded batch.
- Local CSV and GeoJSON export of the currently loaded bounded Timeline view.
- Development Find My device-state surface with Live/Recent/Stale/Offline/Unavailable presentation and server-authoritative recovery-action gating.
- Native Android collection/retry foundations.

## Current stabilization candidate — PR #49

Draft PR #49 adds or consolidates:

- deterministic Timeline newest/oldest ordering;
- reported-accuracy presentation filtering;
- filtered visible-view summaries and explicit loaded/visible/hidden scope truth;
- filter reset with focus restoration;
- presentation-only Timeline screen privacy that hides precise coordinate text, disables coordinate copy, and pauses coordinate-bearing export while active;
- repository-local GLAZE UI V1.6 / 1.6.0 source mapping with protected semantic surfaces, accessibility-profile fallbacks, input-mode adaptation, Reduced Motion/Transparency, forced-colors behavior, and bounded performance fallback;
- Platform Contract 2.0 exact-head validation with nine Integral Platform Systems.

These remain candidate-only until protected promotion.

## Evidence boundary

Accepted or candidate source does not establish production Identity, production geographic providers, reliable physical-device background collection, Find My recovery authority, sharing, anti-stalking acceptance, complete backup/restore, deployment, release, or Anchor qualification.
