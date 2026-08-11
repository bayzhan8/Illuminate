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

  /* A hairline along the bottom of the bar showing how far through the
     reading the page is scrolled. Only on pages long enough to warrant one. */
  document.addEventListener("DOMContentLoaded", function () {
    var prose = document.querySelector(".prose");
    var bar = document.querySelector(".bar");
    if (!prose || !bar || prose.offsetHeight < 2000) return;
    var line = document.createElement("div");
    line.className = "progress";
    bar.appendChild(line);
    var draw = function () {
      var total = document.body.scrollHeight - window.innerHeight;
      var done = total > 0 ? window.scrollY / total : 0;
      line.style.width = Math.max(0, Math.min(1, done)) * 100 + "%";
    };
    var pending = false;
    window.addEventListener("scroll", function () {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { draw(); pending = false; });
    }, { passive: true });
    draw();
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
