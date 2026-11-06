# GoreeCloud Location — Product Feature Specification

**Founder product direction · 3 November 2026 · target capabilities, not implemented-state evidence**

GoreeCloud Location is the privacy-first, self-hosted location intelligence, GPS tracking, family safety, travel history, vehicle management, and emergency coordination component of the GoreeCloud ecosystem. It is intended for personal, family, household, organizational and fleet use on independently controlled infrastructure. The product should offer Android, iOS, Linux and modern web experiences in GoreeCloud UI, while centralizing data on self-hosted services.

## Status notation

- **[Foundation]** Exists in the initial development source; requires CI, runtime, security, and UI acceptance verification before calling it stable.
- **[Planned]** Product requirement; no implementation has been verified.
- **[External]** Depends on compatible hardware, a separate mapping/data source, a licensed provider, or a professional response service. No service-provider availability is implied.

The full scope below is categorized from the founder's 22-section product brief. No feature is considered shipped solely by appearing in this specification.

## 1. Real-time location tracking

**[Foundation]** Account-isolated GPS positions, owned devices, authenticated per-device ingestion, user-initiated browser location capture, accuracy/altitude/speed/heading/battery/timestamp storage, last-known locations, live UI refresh on reload, and location history.

**[Planned]** Continuous and background updates; movement/time/distance-based triggers; on-demand and last-known requests; high accuracy, balanced, battery-saving and quiet modes; interval and distance controls; satellite/connectivity indicators; multi-device live streaming; offline collection and later synchronization; stationary/movement classification; tracking activity/diagnostic logs; GPS/cellular/Wi-Fi fusion; real-time map following.

## 2. Maps and geographic visualization

**[Foundation]** Responsive coordinate map, interactive device markers, path overlays, zoom-to-fit, GC UI light/dark themes, location timeline, and optional owner-managed same-origin map tile templates.

**[Planned]** Accurate street/terrain/topographic/hybrid/satellite maps with appropriate provider rights; offline/self-hosted tile downloads; richer zoom/pan/rotation; full-screen map; map layers, clustering and accuracy circles; speed-coded tracks; heatmaps; fog-of-war and visited-country/region exploration; 3D globe; place/geofence/photo and journey overlays; historic animations and timeline playback; search/address lookup/reverse geocoding; distance measurements, printable maps, map/video exports.

## 3. Location history and timelines

**[Foundation]** Persistent chronological GPS points, last-known device position, owner-scoped timeline, individual deletion, per-device confirmed history erasure, timestamp-based history querying, and export.

**[Planned]** Daily/weekly/monthly/yearly views, calendar navigation, full-history search and advanced filtering, visit/stop/overnight detection, trip grouping and transport modes, cross-device and consented family comparisons, GPS anomaly correction, bulk edits/deletion, automatic retention schedules and age-based policies, import/migration, history backup/restore with recovery tests, automated historical route animations.

## 4. Places, geofencing, and location awareness

**[Foundation]** Named places, circular geofences (10 to 50,000 meters), accuracy-gated entry/exit transitions, owner-scoped event history and place deletion.

**[Planned]** Custom place icons/categories/notes; home/work/school categories; inferred visits and visitation statistics; polygon and route-corridor geofences; scheduled/expected arrivals, missed-arrival and safe-arrival notifications; device/family/vehicle/pet/asset-specific rules; geofence automation and webhooks; privacy zones; proximity/separation alerts; accuracy and hysteresis refinements.

## 5. Family circles and shared location

**[Implemented — membership foundation, no sharing]** Private named circles, recipient-generated one-time invitation codes, pending invitations with expiry, accept/decline, owner/member roles, owner revocation and member exit. Membership does not grant any position, history, device or export permissions. See [CIRCLES.md](CIRCLES.md).

**[Planned]** Permission-isolated family maps, verified live/history sharing grants, separate permission expiries and immediate revocation, group administrators and invitations beyond the first owner/member roles, member avatars/battery/location cards, check-ins, trusted contacts, alerts, trips, driving reports, and shared records. No location disclosure is active.

**Safety gate:** No cross-account location access without explicit consent, auditable grants, and tested revocation.

## 6. Location sharing and privacy

**[Foundation]** Personal account ownership and no public location-share endpoints.

**[Planned]** Temporary, one-time and continuous location sharing; links with expiry/password/revocation; individual, circle and trip/history-specific grants; approximate location and privacy bubbles; quiet, paused and manual modes; request/accept/decline flows; selective historical redaction; disclosure logs; consent history; distinct collection, retention and sharing controls; controlled emergency disclosures.

## 7. Driving detection and safety

**[Planned]** Automatic drive/trip classification; driver versus passenger analysis with consent and suitable signal quality; route/time/distance/speed reporting; speed limit violations where map data allows; acceleration, braking, harsh driving and device interaction signals; driver safety summaries; historical driving events; GPS speed charts; configurable thresholds; vehicle idle detection, device/driver associations and fleet driving reports.

**[External]** Hardware-specific driver identification and authoritative speed-limit datasets.

## 8. Emergency assistance and personal safety

**[Planned]** User-triggered SOS, silent SOS/countdown, emergency contacts, location-sharing links, check-ins, event history/acknowledgments, escalation workflows, safety incident recording and trusted-contact responses.

**[External]** Crash detection with validated sensors, hardware SOS buttons, medical/roadside/vehicle assistance, professional dispatch, emergency service coordination, disaster response and travel assistance. Must use authorized providers and make no emergency guarantees without contractual, operational, and end-to-end testing.

## 9. Vehicle tracking and fleet management

**[Foundation]** Device kind `vehicle`, location history and owner-scoped position ingestion.

**[Planned]** Fleets, vehicle profiles/identifiers, dispatch/administrator controls, driver assignments, ignition/idle/trip/stop detection, mileage/odometer/engine hours, fuel/battery metrics, unauthorized movement/tow/tamper alarms, maintenance schedules, custom sensors, telemetry charts, route replay and fleet reports, remote commands and driver/vehicle access restrictions.

**[External]** GPS hardware protocols, compatible sensors and command safety constraints.

## 10. GPS devices, sensors and assets

**[Foundation]** Devices with types `person`, `vehicle`, `pet`, `item`, `asset`, `other`, one-time device ingestion credentials, last position, basic battery/accuracy/speed/altitude/heading fields.

**[Planned]** Device enrollment lifecycle, hardware protocols, cellular/wearable trackers, power/sensor telemetry, inactivity/tamper/SOS alerts, asset grouping, remote configuration, command responses, device diagnostic history and specialized access rights.

## 11. Pet location and safety

**[Foundation]** A `pet` device category with tracked positions.

**[Planned]** Pet photos/profiles/IDs, safe places and escape notifications, lost-pet mode, activity/walking summaries, care routines, feeding/medication reminders, caregiving attribution, activity roundups, QR identification and finder workflows.

**[External]** Pet GPS hardware, nearby Bluetooth finders and community search partnerships.

## 12. Personal belongings and item tracking

**[Foundation]** An `item` or `asset` device with location history.

**[Planned]** Profile and ownership assignment for keys/wallets/bags/luggage; item icons, last-seen location, separation/movement/geofence alarms, missing-item status, QR recovery labels, asset histories, return contact flows, audible/LED find commands.

**[External]** Bluetooth hardware and proprietary finder networks cannot be duplicated automatically.

## 13. Trips, travel and transportation

**[Planned]** Automatic/manual trips; journaling, trip dates/notes/photos; day/multi-day routes, stops, distances and time; walking/cycling/driving/stationary/flight classifications; travel itineraries; airport and flight notifications through authorized feeds; country/city exploration stats; visited-region collections; trip posters/animations/exports; family trip sharing and vehicle/flight history integrations.

## 14. Location statistics, analytics and reports

**[Foundation]** Counts for positions, devices, places and geofence events.

**[Planned]** Daily through yearly movement summaries, distance by mode, travel days, countries/cities, time moving/stationary/driving, stop/visit frequency, recurring places, heatmaps, exploration coverage, trend comparisons, trip and fleet reports, driver behavior charts, telemetry dashboards, geofence reports, filtered and shareable exportable analytics.

## 15. Notifications, alerts and communication

**[Foundation]** In-app geofence event records. No external alert delivery yet.

**[Planned]** Arrival/departure, missed arrival, check-in, driving, SOS, crash, offline-device/battery/tamper, fuel/maintenance, pet/lost item, flight and custom event notifications; app/email/push/SMS gateways; per-user/device notification schedules; delivery status, acknowledgment, quick notes, trusted-contact messages and phone shortcuts.

**[External]** Email/SMS/push providers and reliable delivery infrastructure.

## 16. Home automation and location workflows

**[Planned]** MQTT/HTTP/JSON position/event publishing; geofence and occupancy triggers; family presence, nearby Bluetooth beacons, battery/driver/vehicle workflow events; Home Assistant, Node-RED, n8n connectors; signed webhooks, retry/delivery logs; conditional workflows, REST subscription endpoints and action histories.

## 17. Data collection, import, export and migration

**[Foundation]** Authenticated JSON/HTTP ingestion, bounded owner-scoped CSV imports with duplicate skipping, full streaming GPX/GeoJSON exports, keyset-paginated GPS history and manual consistent SQLite snapshot, verification and restore-to-new-file commands; preview-first owner-controlled history cleanup.

**[Planned]** Resumable bulk exports; Google Takeout/Timeline migration; GPX/FIT/TCX/KML/KMZ/GeoJSON/ZIP and specialized travel-history imports; OwnTracks/Traccar connectors; duplicate point detection; import progress/diagnostics/undo; geotagged photo imports; data mapping/correction, full-account export, incremental backups, portable format conversions, automated encrypted backups and operational recovery drills.

## 18. Privacy, security and data ownership

**[Foundation]** Self-hosted SQLite, no default accounts, no public signup, scrypt passwords, temporary sessions, per-device hashed ingestion tokens, owner-scoped reads/writes, validation, no analytics/CDN, strict security headers, loopback default, basic throttle, controlled deletion/export.

**[Planned]** Verified external TLS identity integration, MFA and recovery, user-session token rotation, role/group permissions, consent ledger, finer-grained sharing, privacy geofences, data redaction, configurable retention, encrypted backups, audited access, private mapping/geocoding, server diagnostics and independent security acceptance.

## 19. Accounts, administration and management

**[Foundation]** Local administrator account creation, login/logout, device and place management, basic per-user private data views.

**[Planned]** Invitation and account lifecycle, external identity, advanced RBAC, organizations and hierarchy, notification settings, remote device administration, geofence permissions, audit dashboards, backup/restore administration, policy-driven retention, reliable upgrades and migration controls, isolated tenants and fleet dispatch roles.

## 20. Mobile, desktop and web experiences

**[Foundation]** Responsive desktop/mobile web UI, light/dark mode, keyboard-labeled inputs, browser GPS capture on explicit action; no third-party runtime dependencies in the web client.

**[Planned]** Native Android/iOS/Linux clients; background GPS, battery/power policies, offline encrypted queues, push notifications, native navigation, BLE/iBeacon monitoring, hardware/smartwatch support, per-device tracking diagnostics, onboarding, QR provisioning, screen-reader/high-contrast/reduced-motion acceptance and fully reviewed GoreeCloud UI tokens.

## 21. Self-hosting, infrastructure and APIs

**[Foundation]** Python FastAPI/SQLite service, Dockerfile and loopback-bound Compose, JSON REST endpoints, device ingestion API, static web frontend, Docker non-root/read-only/rootless-friendly configuration, optional same-origin external tile-service integration.

**[Planned]** OwnTracks MQTT adapter, Traccar GPS-protocol integration, local map tile renderer, geocoding/routing/map matching, event streaming, webhook publication, highly available storage only when justified, identity and MIPS integration, upgrade/migration/rollback tooling, observability and disaster recovery verification.

## 22. Digital safety and recovery assistance

**[Planned]** Lost-device recovery workflow, theft reports, family safety incident records, emergency contact logs, trusted-contact escalation and configurable safety provider adapters.

**[External]** Breach/dark-web/identity/credit/fraud information, protection/insurance claims, professional responders, medical and roadside assistance, proprietary crowd-finding network coverage. These require opt-in, legally authorized providers and separate validation.

---

## Core product principles

1. **Self-hosted ownership:** I maintain control of sensitive location data on infrastructure I authorize.
2. **Privacy by default:** Collection and every form of sharing require understandable controls and consent.
3. **Unified experience:** People, pets, vehicles and devices are represented coherently, not mixed across permissions.
4. **Cross-platform:** Android, iOS, Linux and the web follow GoreeCloud UI while respecting native OS security and background-operation rules.
5. **Interoperability:** Open formats, HTTP, MQTT, APIs and trusted hardware adapters avoid unnecessary lock-in.
6. **Reliable tracking:** History integrity, offline synchronization, backups and device diagnostics require actual tests before acceptance.
7. **Safety and consent:** A map marker is not proof of physical safety; professional emergency response requires authorized providers.
8. **Modular design:** History, mapping, sharing, telemetry and automation can be maintained independently.
9. **Security/accessibility:** Validation, least privilege, explicit data handling and accessible controls are architecture requirements.
10. **Long-term maintainability:** Clear documentation, tests, independent deployment and reversible upgrades take priority over feature volume.

## Prioritization

- **Phase 0 (current):** Secure self-hosted single-account foundation and regression tests.
- **Phase 1:** History/import/export completeness, backups, local tiles/geocoding, credential rotation, UI acceptance.
- **Phase 2:** Consent-based family circles and genuine mobile clients; deny cross-account access by default.
- **Phase 3:** GPS device/fleet protocol adapters, automation, operational reporting and alerts.
- **Phase 4:** Safety modules and provider integrations only after independent safety, legal, and runtime gates.

Implementation truth is tracked in [STATUS.md](STATUS.md); operational and privacy details are in [ARCHITECTURE.md](ARCHITECTURE.md) and [SECURITY.md](SECURITY.md).
