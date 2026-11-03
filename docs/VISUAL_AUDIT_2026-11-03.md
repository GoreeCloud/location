# GoreeCloud Location — Screenshot-led Browser UI Review

**3 November 2026 · GoreeCloud UI development acceptance evidence**

## Baseline and scope

The canonical design authority is [GoreeCloud UI](https://github.com/GoreeCloud/gc-ui), especially its [design language](https://github.com/GoreeCloud/gc-ui/blob/main/docs/DESIGN_LANGUAGE.md) and [component contract](https://github.com/GoreeCloud/gc-ui/blob/main/docs/COMPONENTS.md). This review assesses only the existing self-hosted browser development preview. It does not qualify the application as Stable, native mobile, or production ready.

Evidence: [GitHub Actions run 41638054089](https://github.com/GoreeCloud/location/actions/runs/41638054089), which passed the main Python suite (31 tests) and real Playwright Chromium interaction journeys at 1440×900, 820×1180, and 390×844. The workflow generated **18 screenshots** across login, overview empty, populated overview, history, light settings, and the token dialog, with ingestion tokens masked. The screenshots are retained for seven days as `goreecloud-location-browser-evidence`.

## Visual observations from inspected screenshots

| Surface | Verified observation | Outcome |
| --- | --- | --- |
| Desktop login (1440×900) | Distinctive split hero, brand mark, large typography, well-spaced form, visible account-creation limitation | No obvious blocking composition defect |
| Desktop empty dashboard | Strong hierarchy across navigation, statistics, coordinate map, recent activities and events; useful empty-state explanation | Rendered, intentionally designed; functional data coverage separately tested |
| Desktop secret dialog | Clear hierarchy, centered native modal and strong action contrast; secret was masked before screenshot upload | Rendered; keyboard focus and screen-reader announcement still require dedicated review |
| Desktop light settings | Readable cards, clear deletion warning and data ownership content | Uneven final card position identified for follow-up |
| Tablet light settings (820×1180) | Icon rail and readable controls; final development-preview card occupies only the left column, leaving the other side empty | **Actionable visual imbalance**, addressed in settings grid candidate PR |
| Phone login (390×844) | Responsive brand/hero/form stacking, readable form inputs, no observed page-level overflow | Rendered and functional in Chromium |
| Phone light settings | Retention controls reachable through new mobile Privacy tab; warnings and form inputs fit phone width | Main mobile navigation blocker resolved |
| Phone populated overview | New topbar Sign out, fixed five-tab bottom navigation, synthesized GPS pin and responsive cards | Successful synthetic GPS capture shown; not a real-device tracking validation |

## Corrective change under review

At desktop widths 1191px and above, present all three Privacy & settings cards as one balanced three-column row. Between 681px and 1190px, allow the last informational card to span the two-column grid. Phone layouts remain a single column. Add browser assertions for this geometry at every tested viewport.

## Remaining gates

- Review **all** screenshots from the final corrective CI run, including all responsive and theme states, before asserting full visual acceptance.
- Test WCAG contrast, focus visibility, keyboard-only traversal, semantic labels, screen reader announcement, reduced-motion and enlarged text.
- Extend to WebKit/Firefox, physical Android/iOS browser and native clients, and real-world touch testing.
- Add explicit permission-denial, offline, error/loading and session-expiration screenshots. Current tests cover successful browser geolocation with fabricated coordinates only.
- The app's map is still a private coordinate visualization unless a separately deployed self-hosted tile server is configured. A passing test does not mean satellite/topographic maps are available.

**Decision:** The current interface passes an initial rendered Chromium regression milestone. **Full premium GC UI acceptance remains OPEN** until the remaining usability, accessibility and design checks are completed and evidenced.
