# GoreeCloud Location — Browser QA and visual acceptance

**Development preview · November 3, 2026.** GC UI is the sole authoritative design system. Browser tests are a necessary but not sufficient visual acceptance gate.

## Automated checks

The CI browser job starts the real GoreeCloud Location API on **127.0.0.1 only**, with a new SQLite database containing one synthetic test account. It drives headless Chromium via Playwright 1.64.1 and checks desktop (1440×900), tablet (820×1180) and phone (390×844) layouts.

Coverage includes private login, responsive navigation, light/dark theme toggle, preview-only retention, device enrollment and one-time token handling, browser geolocation using fake coordinates, map/history updates, logout, third-party request absence, JavaScript console errors and page-level horizontal overflow.

The job saves synthetic screenshots covering login, empty overview, light-theme settings, masked one-time device token dialog, recorded GPS overview, and history on each viewport. GitHub retains the screenshot artifact for seven days. **Actual visual acceptance requires inspecting the captured screenshots** against the current [GC UI design language](https://github.com/GoreeCloud/gc-ui/blob/main/docs/DESIGN_LANGUAGE.md) and [component contract](https://github.com/GoreeCloud/gc-ui/blob/main/docs/COMPONENTS.md). A green test does not certify polished visual design.

## Safety

Tests use a fresh random loopback port, a synthetic account, and a temporary SQLite database. The screenshots deliberately mask device ingestion secrets; test accounts and coordinates are fabricated. No public listener, map tile provider, real mobile device, production database or third-party network is involved. Browser engine downloading occurs only on the disposable GitHub CI runner.

## Keyboard and modal semantics checkpoint

The browser acceptance runner checks that Settings navigation can be activated with Enter, one-time token and erasure confirmation dialogs have names/descriptions, their actions can be operated from the keyboard, Escape cancels the erasure dialog, and Sign out can be activated with Enter. Screen-reader behavior, focus visibility and full keyboard tab-order review remain manual acceptance gates, not proven by these checks.

## Remaining acceptance gates

- Inspect screenshots for typography, spacing, hierarchy, card density, responsive overflow, accessible focus styles, errors, and thematic consistency.
- Verify actual browser accessibility with keyboard-only operation and screen-reader audits.
- Add Safari/WebKit and Firefox testing, browser permissions rejection, performance budgets, reduced-motion, high-contrast, and touch target assessment.
- Test on physical Android/iOS hardware and Linux desktop separately. A browser UI does not satisfy mandatory native application delivery requirements.

## Three-format History import regression

The unified History file chooser is exercised with **synthetic CSV, GPX and GeoJSON** uploads at desktop (1440×900), tablet (820×1180) and phone (390×844). Each successful import must increase that account’s point count by exactly one; selecting an unsupported `.txt` extension must display an error and result in **zero** HTTP import calls. This is a browser/UI regression gate, not a proof of real-world archive compatibility, production accessibility, or import throughput.
