# GoreeCloud Location — Feature Roadmap

**Status:** Active roadmap control  
**As of:** 2026-09-27  
**Authoritative project record:** Project Specification — Location  
**Canonical repository:** GoreeCloud/location  
**Drive control:** `GoreeCloud/Feature Roadmap/GoreeCloud Location/FEATURE-ROADMAP.docx`

## Purpose

This file is the repository-side feature roadmap control for GoreeCloud Location. It records current planned and recommended feature work without replacing the authoritative project record, exact implementation evidence, release gates, or GoreeCloud Tasks Management.

## Roadmap

| ID | Feature / obligation | Priority | Current state |
| --- | --- | --- | --- |
| FR-001 | Reconcile current and recommended Location scope against the authoritative project record and verified repository evidence. | High | Ongoing control |
| FR-002 | Move unfinished actionable obligations into GoreeCloud Tasks Management with priority, dependency, and lifecycle disposition. | High | Ongoing control |
| FR-003 | Do not mark features implemented, complete, cancelled, superseded, Anchor, or production-ready without authoritative evidence. | High | Ongoing control |
| FR-004 | Consolidate the current Timeline ordering/accuracy/scope/privacy work and Glaze governance stack into one current reviewable candidate instead of maintaining a long stale stacked-PR chain. | Critical | In progress — stabilization candidate |
| FR-005 | Complete fresh Location rendered/accessibility/device/performance/battery acceptance for the implemented GLAZE UI V1.6 / 1.6.0 source mapping. | High | Source implemented; acceptance blocked |
| FR-006 | Complete Platform Contract 2.0 nine-system integration work for Manager, Privacy Shield, Wardveil, Everkeep, Glaze UI, Mesh, Identity, Policy, and Observability. | Critical | Blocked / in progress |
| FR-007 | Complete Android collector reliability: encrypted bounded queue, retry/backoff, retention, credential revocation, permission-safe recovery, battery-aware profiles, and physical-device acceptance. | Critical | In progress / blocked |
| FR-008 | Advance Find My device surfaces with stale/offline/approximate truth, recovery gating, privacy controls, anti-abuse/anti-stalking protections, and explicit authorization. | Critical | In progress / blocked |
| FR-009 | Implement sharing, geofencing, places/visits, trips, migration/import, complete export, backup/restore, and controlled native cutover without retiring transitional systems before acceptance. | High | Planned / staged |
| FR-010 | Complete production geographic-map delivery, Sync contracts, representative-device validation, deployment, rollback, release provenance, and Anchor qualification. | High | Planned / blocked |

## Privacy and authority boundary

Location owns approved current position, tracking, personal history, device location, Find My, geofences, and location-sharing policy. Precise location remains sensitive and private by default. Maps may consume approved current-position behavior through an explicit Location contract but must not become a second location-history or tracking authority.

## Maintenance and synchronization

This roadmap and the corresponding Drive `FEATURE-ROADMAP.docx` must remain materially synchronized with the authoritative project record, live GitHub state, Platform Contract, and GoreeCloud Tasks Management. Missing obligations, stale repository names, stale platform-system counts, obsolete Glaze targets, duplicated work, or undocumented status changes are defects.

Completion and lifecycle claims require the applicable implementation, exact-head validation, review, runtime evidence, release evidence, and production acceptance. A green CI run alone does not establish Anchor.
