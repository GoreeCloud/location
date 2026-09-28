import "./glaze-v1-6.css";

type NavigatorWithConnection = Navigator & {
  connection?: { saveData?: boolean };
};

const root = document.documentElement;
const media = {
  reducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)"),
  reducedTransparency: window.matchMedia("(prefers-reduced-transparency: reduce)"),
  increasedContrast: window.matchMedia("(prefers-contrast: more)"),
  forcedColors: window.matchMedia("(forced-colors: active)"),
  coarsePointer: window.matchMedia("(pointer: coarse)"),
};

const applyEnvironment = (): void => {
  const profiles: string[] = [];
  if (media.reducedMotion.matches) profiles.push("reduced-motion");
  if (media.reducedTransparency.matches) profiles.push("reduced-transparency");
  if (media.increasedContrast.matches) profiles.push("increased-contrast");
  if (media.forcedColors.matches) profiles.push("forced-colors");

  root.dataset.glazeVersion = "1.6.0";
  root.dataset.glazeRuntime = "repository-local";
  root.dataset.glazeAuthority = "presentation-only";
  root.dataset.glazeAccessibility = profiles.join(" ") || "default";
  root.dataset.glazeMotion = media.reducedMotion.matches ? "minimal" : "standard";
  root.dataset.glazePerformance =
    (navigator as NavigatorWithConnection).connection?.saveData === true ? "efficient" : "balanced";
  if (!root.dataset.glazeInput) {
    root.dataset.glazeInput = media.coarsePointer.matches ? "touch" : "pointer";
  }
};

Object.values(media).forEach((query) => query.addEventListener("change", applyEnvironment));

window.addEventListener("keydown", (event) => {
  if (event.key === "Tab" || event.key.startsWith("Arrow")) {
    root.dataset.glazeInput = "keyboard";
  }
});

window.addEventListener("pointerdown", (event) => {
  root.dataset.glazeInput = event.pointerType === "touch" ? "touch" : "pointer";
});

applyEnvironment();
