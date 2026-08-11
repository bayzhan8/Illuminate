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

  /* Mark the chapter currently under the reader in the contents list.
     Uses the heading nearest the top of the viewport rather than whichever
     one an observer fired for last, so scrolling up highlights correctly. */
  document.addEventListener("DOMContentLoaded", function () {
    var links = [].slice.call(document.querySelectorAll(".toc a"));
    if (links.length) {
      var heads = links.map(function (a) {
        return document.getElementById(a.getAttribute("href").slice(1));
      });
      var mark = function () {
        var best = 0;
        for (var i = 0; i < heads.length; i++) {
          if (heads[i] && heads[i].getBoundingClientRect().top <= 120) best = i;
        }
        links.forEach(function (a, i) { a.classList.toggle("current", i === best); });
      };
      var waiting = false;
      window.addEventListener("scroll", function () {
        if (waiting) return;
        waiting = true;
        requestAnimationFrame(function () { mark(); waiting = false; });
      }, { passive: true });
      mark();
    }
  });

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
