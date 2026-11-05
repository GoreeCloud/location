"use strict";

// GoreeCloud Location — zero-dependency browser interface.
// The session token lives in sessionStorage for this tab, not in a cookie.
const $ = (id) => document.getElementById(id);
const state = {
  token: sessionStorage.getItem("gc-location-session") || "",
  user: null, devices: [], points: [], places: [], events: [],
  retentionPreview: null,
  selectedHistoryDevice: "", zoomAdjust: 0, tileTemplate: "",
  historyItems: [], historyCursor: null, historyHasMore: false,
  historyLoading: false, historySequence: 0
};
const headings = {
  overview: ["Good to see you.", "OVERVIEW"],
  history: ["Your location history.", "HISTORY"],
  places: ["Places & geofences.", "PLACES"],
  devices: ["Your tracking devices.", "DEVICES"],
  settings: ["Privacy comes first.", "SETTINGS"]
};

function elt(tag, css, text) {
  const element = document.createElement(tag);
  if (css) element.className = css;
  if (text !== undefined && text !== null) element.textContent = String(text);
  return element;
}
function text(id, value) { $(id).textContent = value; }
function empty(node, message) {
  node.replaceChildren(elt("div", "empty-small", message));
}
function showToast(message) {
  const node = $("toast");
  node.textContent = message;
  node.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => { node.hidden = true; }, 4200);
}
async function api(path, options = {}) {
  const requestToken = state.token;
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (state.token) headers.set("Authorization", "Bearer " + state.token);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(path, { ...options, headers, cache: "no-store" });
  if (!response.ok) {
    // A delayed 401 for a previous session must not sign out a new user.
    if (response.status === 401 && !path.startsWith("/api/auth/login")
        && state.token === requestToken) signOutLocal();
    let message = "Request failed (" + response.status + ").";
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch (_ignore) {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}
function signedIn(user) {
  state.user = user;
  $("login-screen").hidden = true;
  $("app-shell").hidden = false;
  text("user-label", user.username);
  text("user-avatar", user.username.slice(0, 1).toUpperCase());
  selectView("overview");
}
function signOutLocal() {
  state.token = "";
  state.user = null;
  state.devices = [];
  state.points = [];
  state.places = [];
  state.events = [];
  state.selectedHistoryDevice = "";
  state.zoomAdjust = 0;
  state.retentionPreview = null;
  sessionStorage.removeItem("gc-location-session");
  $("app-shell").hidden = true;
  $("login-screen").hidden = false;
  $("username").value = "";
  $("password").value = "";
  $("login-feedback").hidden = true;
  $("retention-confirm").value = "";
  text("retention-summary", "No preview yet.");
  $("device-form").reset();
  $("place-form").reset();
  $("history-import-file").value = "";
  if ($("secret-dialog").open) $("secret-dialog").close();
  if ($("erase-dialog").open) $("erase-dialog").close();
  text("device-secret", "");
  text("user-label", "");
  text("user-avatar", "");
  clearTimeout(showToast.timer);
  $("toast").textContent = "";
  $("toast").hidden = true;
  // Clear location coordinates, map pins and lists from the DOM as well as
  // application state, including when another account signs into this tab.
  renderRecent();
  renderDevices();
  renderPlaces();
  renderHistory();
  renderEvents();
  renderCaptureSelect();
  // Hidden maps cannot be rerendered (zero dimensions); explicitly scrub
  // coordinates, SVG paths/pins, tile images and last-user metric values.
  $("map-paths").replaceChildren();
  $("map-markers").replaceChildren();
  $("tile-layer").replaceChildren();
  $("map-empty").hidden = false;
  text("map-count", "No positions yet");
  text("map-coordinates", "Waiting for location");
  for (const name of ["points","devices","places","events"]) text("metric-" + name, "0");
}
function selectView(view) {
  if (!headings[view]) return;
  for (const key of Object.keys(headings)) $("view-" + key).hidden = key !== view;
  document.querySelectorAll("[data-nav]").forEach((node) => {
    const active = node.dataset.nav === view;
    node.classList.toggle("active", active);
    if (active) node.setAttribute("aria-current", "page");
    else node.removeAttribute("aria-current");
  });
  text("page-title", headings[view][0]);
  text("breadcrumb", headings[view][1]);
  if (view === "overview") requestAnimationFrame(renderMap);
}
function fmtTime(iso) {
  if (!iso) return "Never";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "Unknown" : d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}
function fmtCoord(lat, lon) { return Number(lat).toFixed(5) + ", " + Number(lon).toFixed(5); }
function deviceIcon(kind) {
  return ({vehicle:"↗", pet:"♥", item:"◇", asset:"⬡", person:"◎", other:"◈"})[kind] || "◎";
}
function makeRow(title, subtitle, when, icon = "◎") {
  const row = elt("div", "list-row");
  const avatar = elt("div", "list-avatar", icon);
  const body = elt("div", "list-body");
  body.append(elt("strong", "", title), elt("p", "", subtitle));
  row.append(avatar, body);
  if (when) row.append(elt("span", "list-time", when));
  return row;
}

async function refresh() {
  const requestToken = state.token;
  const [summary, devices, points, places, events] = await Promise.all([
    api("/api/summary"), api("/api/devices"), api("/api/locations?limit=1000"),
    api("/api/places"), api("/api/events?limit=50")
  ]);
  // Ignore any response started before sign-out or an account switch.
  if (!state.user || !requestToken || state.token !== requestToken) return;
  state.devices = devices;
  state.points = points;
  state.places = places;
  state.events = events;
  text("metric-points", Number(summary.points).toLocaleString());
  text("metric-devices", Number(summary.devices).toLocaleString());
  text("metric-places", Number(summary.places).toLocaleString());
  text("metric-events", Number(summary.events).toLocaleString());
  renderRecent();
  renderDevices();
  renderPlaces();
  renderHistory();
  renderEvents();
  renderCaptureSelect();
  renderMap();
}
function renderRecent() {
  const list = $("recent-list");
  list.replaceChildren();
  if (!state.points.length) return empty(list, "No recorded positions yet.");
  for (const p of state.points.slice(0, 6)) {
    list.append(makeRow(p.device_name, fmtCoord(p.latitude, p.longitude),
                        new Date(p.recorded_at).toLocaleDateString(),
                        deviceIcon(p.device_kind)));
  }
}
function renderEvents() {
  const list = $("event-list");
  list.replaceChildren();
  if (!state.events.length) return empty(list, "No geofence events yet.");
  for (const e of state.events.slice(0, 6)) {
    list.append(makeRow(e.device_name + " · " + e.kind, e.place_name,
                        new Date(e.recorded_at).toLocaleDateString(), e.kind === "arrival" ? "↘" : "↗"));
  }
}
function confirmEraseHistory(name) {
  return new Promise((resolve) => {
    const dialog = $("erase-dialog");
    const phrase = $("erase-confirm");
    dialog.returnValue = "cancel";
    phrase.value = "";
    text("erase-device-name", name);
    dialog.addEventListener("close", () => {
      resolve(dialog.returnValue === "erase" && phrase.value === "ERASE");
    }, {once:true});
    dialog.showModal();
    requestAnimationFrame(() => phrase.focus());
  });
}
function renderDevices() {
  const node = $("devices-list");
  node.replaceChildren();
  if (!state.devices.length) return empty(node, "No registered devices. Create one to start collecting positions.");
  for (const d of state.devices) {
    const row = elt("div", "item-card");
    const avatar = elt("div", "list-avatar", deviceIcon(d.kind));
    const info = elt("div", "list-body");
    info.append(elt("strong", "", d.name),
                elt("p", "", d.recorded_at ? "Last position · " + fmtTime(d.recorded_at) : "Awaiting first position"));
    info.append(elt("p", "", d.tracking_paused
      ? "Collection paused · uploads blocked"
      : "Collection active"));
    const small = elt("span", "list-time", d.kind);
    const toggle = elt("button", "tiny-action",
      d.tracking_paused ? "Resume collection" : "Pause collection");
    toggle.type = "button";
    toggle.setAttribute("aria-label", (d.tracking_paused ? "Resume" : "Pause")
      + " location collection for " + d.name);
    toggle.addEventListener("click", async () => {
      const paused = !Boolean(d.tracking_paused);
      const warning = paused
        ? "Pause incoming GPS uploads for " + d.name
          + "? Existing history remains. The tracker may continue to record locally."
        : "Resume GPS collection for " + d.name
          + "? A new live geofence baseline will be created.";
      if (!window.confirm(warning)) return;
      try {
        await api("/api/devices/" + d.id + "/collection", {
          method: "PUT", body: JSON.stringify({paused})
        });
        await refresh();
        showToast(paused ? "Collection paused for " + d.name + "."
          : "Collection resumed for " + d.name + ".");
      } catch (error) { showToast(error.message); }
    });
    const rotate = elt("button", "tiny-action", "Rotate key");
    rotate.type = "button";
    rotate.setAttribute("aria-label", "Rotate ingestion key for " + d.name);
    rotate.addEventListener("click", async () => {
      if (!window.confirm("Rotate the private ingestion key for " + d.name
          + "? The old key will stop working immediately; update your tracker with the new key.")) return;
      try {
        const updated = await api("/api/devices/" + d.id + "/rotate-token", {method:"POST"});
        text("secret-title", "Device key rotated");
        text("secret-description",
          "The previous key has been revoked. Save this new key now and reconfigure your tracking client.");
        text("device-secret", updated.ingest_token);
        $("secret-dialog").showModal();
      } catch (error) { showToast(error.message); }
    });
    const erase = elt("button", "tiny-action danger", "Erase history");
    erase.type = "button";
    erase.setAttribute("aria-label", "Permanently erase tracking history for " + d.name);
    erase.addEventListener("click", async () => {
      if (!await confirmEraseHistory(d.name)) return;
      try {
        await api("/api/devices/" + d.id + "/history", {method:"DELETE"});
        await refresh();
        showToast("History and place events erased for " + d.name + ". Device remains registered.");
      } catch (error) { showToast(error.message); }
    });
    const actions = elt("div", "item-actions");
    actions.append(toggle, rotate, erase);
    row.append(avatar, info, small, actions);
    node.append(row);
  }
}
function renderPlaces() {
  const node = $("places-list");
  node.replaceChildren();
  if (!state.places.length) return empty(node, "No places yet. Create a geofence to track arrivals and departures.");
  for (const p of state.places) {
    const row = elt("div", "item-card");
    const avatar = elt("div", "list-avatar", "⌾");
    const info = elt("div", "list-body");
    info.append(elt("strong", "", p.name),
                elt("p", "", fmtCoord(p.latitude, p.longitude) + " · " + Math.round(p.radius_m) + " m radius"));
    const remove = elt("button", "tiny-action", "Remove");
    remove.type = "button";
    remove.setAttribute("aria-label", "Remove " + p.name);
    remove.addEventListener("click", async () => {
      if (!window.confirm("Delete " + p.name + " and its associated geofence events?")) return;
      try { await api("/api/places/" + p.id, {method:"DELETE"}); await refresh(); showToast("Place removed."); }
      catch (error) { showToast(error.message); }
    });
    row.append(avatar, info, remove);
    node.append(row);
  }
}
function makeChoice(select, value, name) {
  const option = document.createElement("option");
  option.value = String(value);
  option.textContent = name;
  select.append(option);
}
function renderCaptureSelect() {
  const select = $("capture-device");
  const old = select.value;
  select.replaceChildren();
  const active = state.devices.filter((d) => !d.tracking_paused);
  if (!active.length) {
    makeChoice(select, "", state.devices.length
      ? "All devices paused · resume in Devices" : "Add a device first");
    select.disabled = true;
    $("capture-location").disabled = true;
    return;
  }
  for (const d of active) makeChoice(select, d.id, d.name);
  if (active.some((d) => String(d.id) === old)) select.value = old;
  select.disabled = false;
  $("capture-location").disabled = false;
}
function renderHistory() {
  const select = $("history-device");
  const old = state.selectedHistoryDevice;
  select.replaceChildren();
  makeChoice(select, "", "All devices");
  for (const d of state.devices) makeChoice(select, d.id, d.name);
  if (state.devices.some((d) => String(d.id) === old)) select.value = old;
  else state.selectedHistoryDevice = "";
  const rows = state.points.filter((p) =>
    !state.selectedHistoryDevice || String(p.device_id) === state.selectedHistoryDevice);
  const tbody = $("history-table");
  tbody.replaceChildren();
  if (!rows.length) {
    const tr = elt("tr");
    const td = elt("td", "empty-small", "No matching location records.");
    td.colSpan = 4; tr.append(td); tbody.append(tr); return;
  }
  for (const p of rows) {
    const tr = elt("tr");
    for (const value of [p.device_name, fmtTime(p.recorded_at),
                         fmtCoord(p.latitude, p.longitude),
                         p.accuracy_m === null ? "—" : Math.round(p.accuracy_m) + " m"]) {
      tr.append(elt("td", "", value));
    }
    tbody.append(tr);
  }
}
function mercator(lat, lon) {
  const y = Math.log(Math.tan(Math.PI / 4 + Math.max(-85, Math.min(85, lat)) * Math.PI / 360));
  return [(lon + 180) / 360 * 256, (1 - y / Math.PI) / 2 * 256];
}
function mapGeometry(width, height) {
  const points = state.points;
  if (!points.length) return null;
  const coords = points.map((p) => mercator(Number(p.latitude), Number(p.longitude)));
  const xs = coords.map((c) => c[0]), ys = coords.map((c) => c[1]);
  const left = Math.min(...xs), right = Math.max(...xs);
  const top = Math.min(...ys), bottom = Math.max(...ys);
  const spanX = Math.max(.001, right - left), spanY = Math.max(.001, bottom - top);
  const fit = Math.min((width * .72) / spanX, (height * .72) / spanY);
  const autoZoom = Math.max(2, Math.min(16, Math.floor(Math.log2(fit))));
  const zoom = Math.max(2, Math.min(17, autoZoom + state.zoomAdjust));
  const scale = 2 ** zoom;
  const centerX = (left + right) / 2, centerY = (top + bottom) / 2;
  return {coords, scale, centerX, centerY, zoom,
    toScreen: ([x,y]) => [width / 2 + (x - centerX) * scale,
                          height / 2 + (y - centerY) * scale]};
}
function renderTiles(geometry, width, height) {
  const node = $("tile-layer");
  node.replaceChildren();
  if (!geometry || !state.tileTemplate) return;
  const z = geometry.zoom, world = 2 ** z;
  const cx = geometry.centerX / 256 * world;
  const cy = geometry.centerY / 256 * world;
  const fromX = Math.floor(cx - width / 512) - 1;
  const toX = Math.ceil(cx + width / 512) + 1;
  const fromY = Math.max(0, Math.floor(cy - height / 512) - 1);
  const toY = Math.min(world - 1, Math.ceil(cy + height / 512) + 1);
  for (let y = fromY; y <= toY; y++) {
    for (let x = fromX; x <= toX; x++) {
      const wrappedX = ((x % world) + world) % world;
      const tilePath = state.tileTemplate.replaceAll("{z}", z)
        .replaceAll("{x}", wrappedX).replaceAll("{y}", y);
      // Defense in depth: URL parsers interpret /\\host as //host.
      // The map renderer must never request an external tile provider.
      if (!tilePath.startsWith("/") || tilePath.startsWith("//") ||
          tilePath.includes("\\")) continue;
      let tileUrl;
      try { tileUrl = new URL(tilePath, window.location.origin); }
      catch (_error) { continue; }
      if (tileUrl.origin !== window.location.origin) continue;
      const image = document.createElement("img");
      image.alt = "";
      image.loading = "lazy";
      image.src = tileUrl.href;
      image.style.left = (width / 2 + (x - cx) * 256) + "px";
      image.style.top = (height / 2 + (y - cy) * 256) + "px";
      node.append(image);
    }
  }
}
function renderMap() {
  if ($("view-overview").hidden) return;
  const node = $("map");
  const width = node.clientWidth, height = node.clientHeight;
  if (!width || !height) return;
  const svg = $("map-paths"), pins = $("map-markers");
  svg.replaceChildren(); pins.replaceChildren();
  const geometry = mapGeometry(width, height);
  $("map-empty").hidden = Boolean(geometry);
  text("map-count", state.points.length ? state.points.length + " latest positions" : "No positions yet");
  if (!geometry) {
    text("map-coordinates", "Waiting for location");
    $("tile-layer").replaceChildren();
    return;
  }
  const first = state.points[0];
  text("map-coordinates", fmtCoord(first.latitude, first.longitude) + " · z" + geometry.zoom);
  renderTiles(geometry, width, height);
  svg.setAttribute("viewBox", "0 0 " + width + " " + height);
  const groups = new Map();
  state.points.forEach((p,i) => {
    const key = p.device_id;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push({point:p, coord:geometry.coords[i]});
  });
  for (const group of groups.values()) {
    const ordered = group.slice().reverse();
    if (ordered.length > 1) {
      const poly = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
      poly.setAttribute("points", ordered.map((x) =>
        geometry.toScreen(x.coord).map((n) => n.toFixed(1)).join(",")).join(" "));
      svg.append(poly);
    }
    const newest = group[0];
    const [x,y] = geometry.toScreen(newest.coord);
    if (x >= -10 && x <= width + 10 && y >= -10 && y <= height + 10) {
      const marker = elt("button", "map-pin");
      marker.type = "button";
      marker.style.left = x + "px";
      marker.style.top = y + "px";
      marker.title = newest.point.device_name + " · " + fmtCoord(newest.point.latitude, newest.point.longitude);
      marker.setAttribute("aria-label", marker.title);
      marker.addEventListener("click", () => showToast(marker.title + " · " + fmtTime(newest.point.recorded_at)));
      pins.append(marker);
    }
  }
}
async function exportData(format) {
  const id = state.selectedHistoryDevice || String(state.devices[0]?.id || "");
  if (!id) return showToast("Create a device before exporting.");
  try {
    const response = await fetch("/api/export/" + format + "?device_id=" + encodeURIComponent(id),
      {headers: {"Authorization": "Bearer " + state.token}, cache:"no-store"});
    if (!response.ok) {
      if (response.status === 401) signOutLocal();
      throw new Error("Export failed (" + response.status + ").");
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url; link.download = "goreecloud-locations." + format;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 3000);
    if (format === "gpx" && response.headers.get("X-GoreeCloud-Export-Truncated") === "true")
      showToast("Export limited to the first 10,000 points.");
  } catch (error) { showToast(error.message); }
}
function setupEvents() {
  document.querySelectorAll("[data-nav]").forEach((node) =>
    node.addEventListener("click", (event) => {
      event.preventDefault();
      selectView(node.dataset.nav);
    }));
  $("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    $("login-feedback").hidden = true;
    try {
      const session = await api("/api/auth/login", {method:"POST", body:JSON.stringify({
        username:$("username").value, password:$("password").value})});
      state.token = session.access_token;
      sessionStorage.setItem("gc-location-session", state.token);
      signedIn(session.user); await refresh();
    } catch (error) {
      $("login-feedback").textContent = error.message;
      $("login-feedback").hidden = false;
    }
  });
  const logoutAction = async () => {
    try { await api("/api/auth/logout", {method:"POST"}); } catch (_ignore) {}
    signOutLocal();
  };
  $("logout").addEventListener("click", logoutAction);
  $("mobile-logout").addEventListener("click", logoutAction);
  $("logout-all").addEventListener("click", async () => {
    if (!window.confirm("Revoke all of your signed-in account sessions, including this browser? Separate GPS device upload keys will remain active.")) return;
    try {
      await api("/api/auth/logout-all", {method:"POST"});
      signOutLocal();
    } catch (error) { showToast(error.message); }
  });
  $("theme-toggle").addEventListener("click", () => {
    const mode = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = mode;
    sessionStorage.setItem("gc-location-theme", mode);
  });
  $("device-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const added = await api("/api/devices", {method:"POST", body:JSON.stringify({
        name:$("device-name").value, kind:$("device-kind").value})});
      $("device-name").value = "";
      await refresh();
      text("secret-title", "Device added successfully");
      text("secret-description", "Save this private ingestion token now. It cannot be viewed again after closing this window.");
      text("device-secret", added.ingest_token);
      $("secret-dialog").showModal();
    } catch (error) { showToast(error.message); }
  });
  $("close-secret").addEventListener("click", () => {
    $("secret-dialog").close();
    $("device-secret").textContent = "";
  });
  $("secret-dialog").addEventListener("close", () => {
    $("device-secret").textContent = "";
  });
  $("copy-secret").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("device-secret").textContent); showToast("Token copied."); }
    catch (_error) { showToast("Copy unavailable. Select the token and copy it manually."); }
  });
  $("place-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/places", {method:"POST", body:JSON.stringify({
        name:$("place-name").value, latitude:Number($("place-lat").value),
        longitude:Number($("place-lon").value), radius_m:Number($("place-radius").value)})});
      $("place-form").reset(); await refresh(); showToast("Geofence saved.");
    } catch (error) { showToast(error.message); }
  });
  $("use-last-position").addEventListener("click", () => {
    if (!state.points.length) return showToast("No recorded positions to use.");
    $("place-lat").value = state.points[0].latitude;
    $("place-lon").value = state.points[0].longitude;
  });
  $("capture-location").addEventListener("click", () => {
    if (!navigator.geolocation) return showToast("Geolocation is unavailable in this browser.");
    const device_id = Number($("capture-device").value);
    if (!device_id) return showToast("Create a device first.");
    showToast("Requesting your browser's location permission…");
    navigator.geolocation.getCurrentPosition(async (position) => {
      const c = position.coords;
      try {
        await api("/api/locations", {method:"POST", body:JSON.stringify({
          device_id, latitude:c.latitude, longitude:c.longitude,
          accuracy_m:c.accuracy, altitude_m:c.altitude,
          speed_mps:c.speed, heading_deg:c.heading
        })});
        state.zoomAdjust = 0; await refresh(); showToast("Location captured privately.");
      } catch (error) { showToast(error.message); }
    }, (error) => showToast("Unable to read your location: " + error.message),
    {enableHighAccuracy:true, timeout:15000, maximumAge:0});
  });
  $("retention-days").addEventListener("input", () => {
    state.retentionPreview = null;
    text("retention-summary", "Days changed. Preview again before deleting.");
  });
  $("retention-preview").addEventListener("click", async () => {
    const days = Number($("retention-days").value);
    if (!Number.isInteger(days) || days < 1 || days > 36500) {
      return showToast("Choose a whole number of days between 1 and 36,500.");
    }
    try {
      const data = await api("/api/retention/preview?older_than_days=" + days);
      state.retentionPreview = data;
      text("retention-summary", data.eligible_points + " GPS points and "
        + data.eligible_events + " geofence events eligible across "
        + data.affected_devices + " devices.");
    } catch (error) { showToast(error.message); }
  });
  $("retention-purge").addEventListener("click", async () => {
    const days = Number($("retention-days").value);
    const preview = state.retentionPreview;
    if (!preview || preview.older_than_days !== days) {
      return showToast("Preview this period before attempting deletion.");
    }
    if ($("retention-confirm").value !== "DELETE_OLD_HISTORY") {
      return showToast("Type the exact confirmation phrase before deleting.");
    }
    if (!preview.eligible_points && !preview.eligible_events) {
      return showToast("No old records are eligible for deletion.");
    }
    if (!window.confirm("Permanently delete up to " + preview.eligible_points
      + " location points and " + preview.eligible_events
      + " geofence events older than " + days + " days? Backups remain untouched.")) return;
    try {
      const result = await api("/api/retention/purge", {
        method: "POST", body: JSON.stringify({
          older_than_days: days,
          expected_points: preview.eligible_points,
          expected_events: preview.eligible_events,
          confirmation: "DELETE_OLD_HISTORY"
        })
      });
      $("retention-confirm").value = "";
      state.retentionPreview = null;
      text("retention-summary", "Deleted " + result.deleted_points + " points and "
        + result.deleted_events + " events from the live database.");
      await refresh();
      showToast("Manual history cleanup finished. Backups and exports were not changed.");
    } catch (error) { showToast(error.message); }
  });
  $("history-device").addEventListener("change", (event) => {
    state.selectedHistoryDevice = event.target.value; renderHistory();
  });
  $("history-import").addEventListener("click", async () => {
    const selected = state.selectedHistoryDevice;
    const chooser = $("history-import-file");
    const file = chooser.files[0];
    if (!selected) return showToast("Choose one device in the timeline filter before importing.");
    if (!file) return showToast("Choose a CSV, GPX or GeoJSON file first.");
    const formats = {
      csv: {path:"csv", media:"text/csv"},
      gpx: {path:"gpx", media:"application/gpx+xml"},
      geojson: {path:"geojson", media:"application/geo+json"}
    };
    const extension = file.name.split(".").pop().toLowerCase();
    const format = formats[extension];
    if (!format) return showToast("Choose a .csv, .gpx or .geojson file.");
    if (file.size > 2097152) return showToast("History imports are limited to 2 MiB.");
    try {
      const response = await api("/api/devices/" + encodeURIComponent(selected)
        + "/import/" + format.path, {
        method: "POST", headers: {"Content-Type": format.media}, body: file
      });
      chooser.value = "";
      await refresh();
      showToast("Imported " + response.imported + " positions; skipped "
        + response.skipped_duplicates + " duplicates.");
    } catch (error) { showToast(error.message); }
  });
  $("export-geojson").addEventListener("click", () => exportData("geojson"));
  $("export-gpx").addEventListener("click", () => exportData("gpx"));
  $("zoom-in").addEventListener("click", () => { state.zoomAdjust++; renderMap(); });
  $("zoom-out").addEventListener("click", () => { state.zoomAdjust--; renderMap(); });
  $("fit-map").addEventListener("click", () => { state.zoomAdjust = 0; renderMap(); });
  window.addEventListener("resize", () => requestAnimationFrame(renderMap));
}
async function start() {
  $("capture-device")?.remove(); // no duplicate dynamic selection on hot reload
  const selector = document.createElement("select");
  selector.id = "capture-device";
  selector.setAttribute("aria-label", "Device for current location");
  selector.className = "capture-device";
  $("capture-location").before(selector);
  const theme = sessionStorage.getItem("gc-location-theme");
  if (theme === "dark" || theme === "light") document.documentElement.dataset.theme = theme;
  setupEvents();
  try {
    const config = await api("/api/config");
    state.tileTemplate = config.tile_template || "";
  } catch (_ignore) {}
  if (!state.token) return;
  try {
    const user = await api("/api/me");
    signedIn(user); await refresh();
  } catch (_error) { signOutLocal(); }
}
window.addEventListener("DOMContentLoaded", start);
