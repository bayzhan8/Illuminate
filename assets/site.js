/* Colour scheme, remembered, and applied before the canvases draw.

   The sandbox pages read their colours from CSS custom properties at draw
   time rather than from a stylesheet rule, so flipping the scheme has to tell
   them to redraw. That is what the themechange event is for. */

(function () {
  var KEY = "illuminate-theme";

  function system() {
    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    var button = document.getElementById("theme");
    if (button) button.textContent = theme === "dark" ? "LIGHT" : "DARK";
    document.dispatchEvent(new Event("themechange"));
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
  apply(saved || system());

  document.addEventListener("DOMContentLoaded", function () {
    var button = document.getElementById("theme");
    if (!button) return;
    button.textContent =
      document.documentElement.dataset.theme === "dark" ? "LIGHT" : "DARK";
    button.addEventListener("click", function () {
      var next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      try { localStorage.setItem(KEY, next); } catch (e) { /* private mode */ }
      apply(next);
    });
  });
})();
