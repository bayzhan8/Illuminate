"""Turn lesson.md into everything else.

    python build.py chapters   split the lesson into chapters/NN-slug/README.md
    python build.py page       render lesson.md to lp-duality/index.html
    python build.py sandbox    write the interactive pages under sandbox/
    python build.py all        all three

``lesson.md`` is the only place the prose exists.  The chapter files used to be
maintained by hand next to it and the two drifted within a week, so they are
generated now and the tests fail if a generated file on disk does not match
what this script would write.

The site is served from the repository root rather than from a ``docs`` folder,
which means the image paths in lesson.md are the same paths the published page
uses.  Nothing has to be rewritten, and no image is stored twice.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
LESSON = ROOT / "lesson.md"
SITE = "https://bayzhan8.github.io/Illuminate"

# (number, folder, title) -- the folder names are fixed here rather than
# derived from the headings, so retitling a chapter never silently orphans the
# images sitting in its folder.
CHAPTERS = [
    (0, "00-what-this-is", "What this is"),
    (1, "01-the-workshop", "The workshop"),
    (2, "02-no-way-to-check", "Why you cannot just check"),
    (3, "03-mixing-the-rules", "Charging for the ingredients"),
    (4, "04-every-mix-is-a-ceiling", "Every honest price list is a ceiling"),
    (5, "05-they-always-meet", "They always meet"),
    (6, "06-who-is-binding", "Which rules are actually holding you back"),
    (7, "07-what-one-more-is-worth", "What one more plank is worth"),
    (8, "08-the-price-breaks", "The price is only local"),
    (9, "09-when-it-goes-wrong", "When it goes wrong"),
    (10, "10-where-this-leads", "Where this leads"),
]

renderer = MarkdownIt("commonmark").enable("table")


# --- reading the lesson ----------------------------------------------------

def split_lesson() -> tuple[str, list[str], str]:
    """(front matter, one block of markdown per chapter, everything after)."""
    text = LESSON.read_text()
    parts = re.split(r"\n---\n", text)
    front = parts[0]
    chapters, tail = [], []
    for part in parts[1:]:
        if re.match(r"\s*## \d+ · ", part):
            chapters.append(part.strip())
        else:
            tail.append(part.strip())
    if len(chapters) != len(CHAPTERS):
        raise SystemExit(f"lesson.md has {len(chapters)} chapters, "
                         f"build.py expects {len(CHAPTERS)}")
    return front.strip(), chapters, "\n\n---\n\n".join(t for t in tail if t)


# --- chapter files ---------------------------------------------------------

def chapter_markdown(index: int, body: str) -> str:
    number, folder, title = CHAPTERS[index]
    # images are addressed from the chapter's own folder, so drop the prefix
    body = body.replace(f"chapters/{folder}/", "")
    lines = [
        f"<!-- generated from ../../lesson.md by ../../build.py; do not edit -->",
        "",
        body,
        "",
        "---",
        "",
    ]
    nav = []
    if index > 0:
        prev = CHAPTERS[index - 1]
        nav.append(f"← [{prev[2]}](../{prev[1]}/README.md)")
    nav.append("[all chapters](../..#chapters)")
    if index < len(CHAPTERS) - 1:
        nxt = CHAPTERS[index + 1]
        nav.append(f"[{nxt[2]}](../{nxt[1]}/README.md) →")
    lines.append(" · ".join(nav))
    return "\n".join(lines) + "\n"


def build_chapters() -> None:
    _, chapters, _ = split_lesson()
    for index, body in enumerate(chapters):
        folder = ROOT / "chapters" / CHAPTERS[index][1]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "README.md").write_text(chapter_markdown(index, body))
    print(f"  wrote {len(chapters)} chapter files")


# Applied before first paint so a dark-mode reader never sees a cream flash.
# Kept as a constant rather than inlined in the templates because its braces
# would otherwise have to be doubled to survive str.format.
THEME_BOOT = """<script>
  try {
    var t = localStorage.getItem("illuminate-theme");
    document.documentElement.dataset.theme = t ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  } catch (e) {}
</script>"""


# --- the web page ----------------------------------------------------------

PAGE = """<!doctype html>
<html lang="en" data-page="lesson">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{blurb}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/site.css">
{boot}
</head>
<body>
<header class="bar">
  <a class="brand" href="../">ILLUMINATE</a>
  <button class="toggle" id="theme" type="button" aria-label="Switch colour scheme">DARK</button>
</header>
<main class="prose">
{body}
</main>
<footer class="foot">
  <a href="{site}">Illuminate</a> ·
  <a href="https://github.com/bayzhan8/Illuminate/tree/main/lp-duality">source and tests</a>
</footer>
<script src="../assets/site.js"></script>
</body>
</html>
"""


def render_page() -> None:
    front, chapters, tail = split_lesson()
    body = renderer.render("\n\n".join([front] + chapters + [tail]))
    body = decorate(body)
    title = "Every plan has a price tag — LP duality"
    blurb = ("Linear programming duality built from a workshop with three "
             "shelves and two products, with every number checked by code.")
    (ROOT / "index.html").write_text(
        PAGE.format(title=html.escape(title), blurb=html.escape(blurb),
                    body=body, site=SITE, boot=THEME_BOOT))
    print("  wrote lp-duality/index.html")


def decorate(body: str) -> str:
    """Small structural passes the Markdown itself should not have to carry."""
    # every image becomes a bordered plate; the alt text stays alt text, since
    # it describes the picture for someone who cannot see it and would be
    # redundant as a visible caption next to the prose that already says it
    body = re.sub(
        r'<p><img src="([^"]+)" alt="([^"]*)"\s*/?></p>',
        lambda m: (f'<figure class="plate">'
                   f'<img src="{m.group(1)}" alt="{m.group(2)}" loading="lazy">'
                   f'</figure>'),
        body)
    # anchor every chapter heading so the contents list can reach it
    def anchor(match):
        number = match.group(1)
        return (f'<h2 id="ch{number}"><span class="num">{number}</span>'
                f'{match.group(2)}</h2>')
    body = re.sub(r'<h2>(\d+) · ([^<]+)</h2>', anchor, body)
    body = body.replace("<table>", '<div class="scroll"><table>')
    body = body.replace("</table>", "</table></div>")
    body = body.replace('<blockquote>', '<blockquote class="aside">')
    return body


# --- the interactive pages -------------------------------------------------

# The mathematics below is the same mathematics as src/lpduality, written a
# second time in JavaScript so the pages need no server and no libraries.
# tests/test_sandbox.py runs both against the same inputs, because two copies
# of a formula drift apart the moment one of them is edited alone.
MATHS = r"""
// --- the workshop, as data ------------------------------------------------
const RECIPE = [[4, 2], [2, 3], [3, 1]];      // planks, hours, saw, per product
const STOCK  = [44, 30, 32];
const PROFIT = [30, 20];
const ROWS   = ["planks", "hours", "saw time"];

// --- feasibility and corners ----------------------------------------------
function feasible(x, A, b) {
  if (x[0] < -1e-9 || x[1] < -1e-9) return false;
  for (let i = 0; i < A.length; i++)
    if (A[i][0] * x[0] + A[i][1] * x[1] > b[i] + 1e-9) return false;
  return true;
}

function corners(A, b) {
  const lines = A.map((r, i) => [r[0], r[1], b[i]])
    .concat([[-1, 0, 0], [0, -1, 0]]);
  const out = [];
  for (let i = 0; i < lines.length; i++)
    for (let j = i + 1; j < lines.length; j++) {
      const [a1, b1, r1] = lines[i], [a2, b2, r2] = lines[j];
      const det = a1 * b2 - a2 * b1;
      if (Math.abs(det) < 1e-12) continue;
      const x = [(r1 * b2 - r2 * b1) / det, (a1 * r2 - a2 * r1) / det];
      if (feasible(x, A, b) && !out.some(p => Math.abs(p[0] - x[0]) < 1e-9 &&
                                              Math.abs(p[1] - x[1]) < 1e-9))
        out.push(x);
    }
  return out;
}

// The best plan, by looking at every corner. Hopeless at any real size and
// exactly right at this one, where it has the advantage of being obviously
// correct rather than merely tested.
function bestPlan(c, A, b) {
  const pts = corners(A, b);
  if (!pts.length) return null;
  let best = pts[0], bestValue = c[0] * pts[0][0] + c[1] * pts[0][1];
  for (const p of pts) {
    const v = c[0] * p[0] + c[1] * p[1];
    if (v > bestValue) { best = p; bestValue = v; }
  }
  return { x: best, value: bestValue };
}

function tightRows(A, b, x) {
  const out = [];
  for (let i = 0; i < A.length; i++)
    if (Math.abs(A[i][0] * x[0] + A[i][1] * x[1] - b[i]) < 1e-7) out.push(i);
  return out;
}

// Prices, read off the rules the plan is pressed against: the rows with
// nothing to spare carry the whole bill, and the rest are worth zero.
function prices(c, A, b, x) {
  const y = A.map(() => 0);
  const tight = tightRows(A, b, x);
  if (x[0] > 1e-9 && x[1] > 1e-9 && tight.length >= 2) {
    const [i, j] = tight.slice(0, 2);
    const det = A[i][0] * A[j][1] - A[j][0] * A[i][1];
    if (Math.abs(det) > 1e-12) {
      y[i] = (c[0] * A[j][1] - c[1] * A[j][0]) / det;
      y[j] = (c[1] * A[i][0] - c[0] * A[i][1]) / det;
    }
  } else if (tight.length) {
    // only one product gets built: one row carries it
    const i = tight[0];
    const k = x[0] > 1e-9 ? 0 : 1;
    if (Math.abs(A[i][k]) > 1e-12) y[i] = c[k] / A[i][k];
  }
  return y;
}

function covers(c, A, y) {
  for (let k = 0; k < c.length; k++) {
    let charged = 0;
    for (let i = 0; i < A.length; i++) charged += y[i] * A[i][k];
    if (charged < c[k] - 1e-9) return false;
  }
  return y.every(v => v >= -1e-9);
}

function ceilingFrom(A, b, c, y) {
  if (!covers(c, A, y)) return null;
  return y.reduce((s, v, i) => s + v * b[i], 0);
}

function money(v) { return "$" + v.toLocaleString(undefined,
  { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
"""

PLOT = r"""
// --- a very small drawing helper, in the site's colours -------------------
function palette() {
  const dark = document.documentElement.dataset.theme === "dark";
  return dark
    ? { paper: "#1a1816", ink: "#e8e6e0", ink2: "#a8a599", muted: "#787366",
        rule: "#4a4540", plan: "#4A87CC", price: "#C25A42", ok: "#4E8F55" }
    : { paper: "#fffff8", ink: "#000000", ink2: "#404040", muted: "#707070",
        rule: "#C0BDAD", plan: "#1B4F9C", price: "#B4341F", ok: "#2E6B33" };
}

function Plot(canvas, xlo, xhi, ylo, yhi, pad) {
  const dpr = window.devicePixelRatio || 1;
  const cssW = canvas.clientWidth || 660, cssH = canvas.clientHeight || 380;
  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  pad = pad || { l: 54, r: 22, t: 18, b: 42 };
  const P = palette();
  const X = x => pad.l + (x - xlo) / (xhi - xlo) * (cssW - pad.l - pad.r);
  const Y = y => cssH - pad.b - (y - ylo) / (yhi - ylo) * (cssH - pad.t - pad.b);
  const font = n => `${n}px "IBM Plex Mono", ui-monospace, monospace`;
  return {
    ctx, X, Y, P, W: cssW, H: cssH, pad,
    clear() { ctx.clearRect(0, 0, cssW, cssH); },
    grid(stepX, stepY) {
      ctx.strokeStyle = P.rule; ctx.lineWidth = 1; ctx.setLineDash([1, 4]);
      for (let x = xlo; x <= xhi + 1e-9; x += stepX) {
        ctx.beginPath(); ctx.moveTo(X(x), pad.t); ctx.lineTo(X(x), cssH - pad.b); ctx.stroke();
      }
      for (let y = ylo; y <= yhi + 1e-9; y += stepY) {
        ctx.beginPath(); ctx.moveTo(pad.l, Y(y)); ctx.lineTo(cssW - pad.r, Y(y)); ctx.stroke();
      }
      ctx.setLineDash([]);
    },
    axes(xlabel, ylabel, stepX, stepY) {
      ctx.strokeStyle = P.ink; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, cssH - pad.b);
      ctx.lineTo(cssW - pad.r, cssH - pad.b); ctx.stroke();
      ctx.fillStyle = P.muted; ctx.font = font(11); ctx.textAlign = "center";
      for (let x = xlo; x <= xhi + 1e-9; x += stepX)
        ctx.fillText(String(Math.round(x)), X(x), cssH - pad.b + 17);
      ctx.textAlign = "right";
      for (let y = ylo; y <= yhi + 1e-9; y += stepY)
        ctx.fillText(String(Math.round(y)), pad.l - 9, Y(y) + 4);
      ctx.fillStyle = P.ink2; ctx.font = font(12); ctx.textAlign = "center";
      if (xlabel) ctx.fillText(xlabel, (pad.l + cssW - pad.r) / 2, cssH - 8);
      if (ylabel) { ctx.save(); ctx.translate(14, (pad.t + cssH - pad.b) / 2);
        ctx.rotate(-Math.PI / 2); ctx.fillText(ylabel, 0, 0); ctx.restore(); }
    },
    polygon(pts, fill, stroke) {
      if (!pts.length) return;
      ctx.beginPath(); ctx.moveTo(X(pts[0][0]), Y(pts[0][1]));
      for (const p of pts.slice(1)) ctx.lineTo(X(p[0]), Y(p[1]));
      ctx.closePath();
      if (fill) { ctx.globalAlpha = 0.14; ctx.fillStyle = fill; ctx.fill(); ctx.globalAlpha = 1; }
      if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.8; ctx.stroke(); }
    },
    line(x0, y0, x1, y1, color, width, dash) {
      ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = width || 1.4;
      if (dash) ctx.setLineDash(dash);
      ctx.beginPath(); ctx.moveTo(X(x0), Y(y0)); ctx.lineTo(X(x1), Y(y1));
      ctx.stroke(); ctx.restore();
    },
    dot(x, y, color, r) {
      ctx.beginPath(); ctx.arc(X(x), Y(y), r || 6, 0, 7);
      ctx.fillStyle = color; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = P.paper; ctx.stroke();
    },
    label(x, y, text, color, align) {
      ctx.fillStyle = color; ctx.font = font(12);
      ctx.textAlign = align || "left"; ctx.fillText(text, X(x), Y(y));
    }
  };
}

function sortRound(pts) {
  if (!pts.length) return pts;
  const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
  const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
  return pts.slice().sort((a, b) =>
    Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx));
}
"""

SANDBOX_PAGE = """<!doctype html>
<html lang="en" data-page="sandbox">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Illuminate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/site.css">
{boot}
</head>
<body>
<header class="bar">
  <a class="brand" href="../../">ILLUMINATE</a>
  <button class="toggle" id="theme" type="button" aria-label="Switch colour scheme">DARK</button>
</header>
<main class="sandbox">
  <a class="back" href="../index.html#ch{number}">← back to chapter {number}</a>
  <h1>{title}</h1>
  <p class="lede">{lede}</p>
  <p class="try"><strong>Try this.</strong> {try_this}</p>
  <canvas id="c" width="660" height="380"></canvas>
  <div class="controls">{controls}</div>
  <pre class="out" id="out"></pre>
  <p class="note">{note}</p>
  <nav class="pager">{pager}</nav>
</main>
<script src="../../assets/site.js"></script>
<script>
{maths}
{plot}
{widget}
</script>
</body>
</html>
"""


def slider(ident, label, lo, hi, step, value):
    return (f'<div class="row"><label for="{ident}">{label}</label>'
            f'<input type="range" id="{ident}" min="{lo}" max="{hi}" '
            f'step="{step}" value="{value}">'
            f'<output class="val" id="{ident}v"></output></div>')


SANDBOXES = [
    (1, "Move the money",
     "The workshop's plans, and the best one. The sliders change what a table "
     "and a chair sell for.",
     "Drag the chair price up past $15. The best plan does not drift — it "
     "jumps from one corner to the next, and then sits there for a long while.",
     slider("pt", "a table sells for", 5, 60, 1, 30)
     + slider("pc", "a chair sells for", 5, 60, 1, 20),
     r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const pt = document.getElementById("pt"), pc = document.getElementById("pc");
function draw() {
  const c = [+pt.value, +pc.value];
  const p = Plot(cv, 0, 13, 0, 12);
  p.clear(); p.grid(1, 1); p.axes("tables", "chairs", 2, 2);
  const pts = sortRound(corners(RECIPE, STOCK));
  p.polygon(pts, p.P.plan, p.P.plan);
  for (let i = 0; i < RECIPE.length; i++) {
    const [a, b] = RECIPE[i], r = STOCK[i];
    p.line(0, r / b, 13, (r - 13 * a) / b, p.P.muted, 1.1);
  }
  const best = bestPlan(c, RECIPE, STOCK);
  const lvl = best.value;
  p.line(0, lvl / c[1], 13, (lvl - 13 * c[0]) / c[1], p.P.price, 1.8);
  for (const q of pts) p.dot(q[0], q[1], p.P.plan, 3.5);
  p.dot(best.x[0], best.x[1], p.P.plan, 7);
  const y = prices(c, RECIPE, STOCK, best.x);
  out.textContent =
    "best plan    " + best.x[0].toFixed(2) + " tables, " +
      best.x[1].toFixed(2) + " chairs\n" +
    "worth        " + money(best.value) + "\n" +
    "prices       " + y.map((v, i) => ROWS[i] + " " + money(v)).join("   ") + "\n" +
    "the bill     " + money(y.reduce((s, v, i) => s + v * STOCK[i], 0)) +
      "   (the same number, every time)";
  document.getElementById("ptv").textContent = "$" + pt.value;
  document.getElementById("pcv").textContent = "$" + pc.value;
}
pt.addEventListener("input", draw); pc.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
     "The prices are read off the rules the best plan is pressed against, and "
     "the bill is computed from them independently of the plan. That the two "
     "agree at every setting of the sliders is the whole point of chapter 5."),

    (3, "Find a ceiling by hand",
     "Set a price on each of the three resources. The page checks whether "
     "your prices cover both products, and if they do, works out the ceiling "
     "they prove.",
     "Get the ceiling under $360 without either product going red. Then try "
     "to reach $349 — the reason you cannot is chapter 5.",
     slider("y0", "price of a plank", 0, 12, 0.25, 3)
     + slider("y1", "price of an hour", 0, 12, 0.25, 1)
     + slider("y2", "price of an hour of saw time", 0, 12, 0.25, 0),
     r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const ys = ["y0", "y1", "y2"].map(id => document.getElementById(id));
function draw() {
  const y = ys.map(s => +s.value);
  ys.forEach(s => document.getElementById(s.id + "v").textContent = "$" + (+s.value).toFixed(2));
  const p = Plot(cv, -0.7, 1.7, 0, 46, { l: 54, r: 22, t: 18, b: 46 });
  p.clear(); p.grid(10, 10);
  const ctx = p.ctx;
  const charged = [0, 1].map(k => y.reduce((s, v, i) => s + v * RECIPE[i][k], 0));
  for (let k = 0; k < 2; k++) {
    const okk = charged[k] >= PROFIT[k] - 1e-9;
    ctx.fillStyle = okk ? p.P.ok : p.P.price;
    const x0 = p.X(k - 0.23), x1 = p.X(k + 0.23);
    ctx.fillRect(x0, p.Y(charged[k]), x1 - x0, p.Y(0) - p.Y(charged[k]));
    p.line(k - 0.32, PROFIT[k], k + 0.32, PROFIT[k], p.P.plan, 2.4);
    p.label(k, PROFIT[k] + 1.6, "earns $" + PROFIT[k], p.P.plan, "center");
    p.label(k + 0.30, charged[k], okk ? "covered" : "too cheap",
            okk ? p.P.ok : p.P.price, "left");
    p.label(k, -3.2, k === 0 ? "one table" : "one chair", p.P.ink2, "center");
  }
  p.axes("", "dollars charged", 99, 10);
  const total = ceilingFrom(RECIPE, STOCK, PROFIT, y);
  out.textContent = total === null
    ? "these prices prove nothing\n" +
      "a price list only says something when it covers every product at once"
    : "these prices are honest\n" +
      "nothing this workshop can build is worth more than " + money(total) + "\n" +
      "the best plan really is worth $350.00, so this ceiling is " +
      money(total - 350) + " too high";
  document.dispatchEvent(new Event("drawn"));
}
ys.forEach(s => s.addEventListener("input", draw));
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
     "A ceiling is only as good as its worst product. Under-price either one "
     "and the number this page would have printed is not a weak claim, it is "
     "no claim at all."),

    (6, "Change the shelves",
     "The same workshop, with the stock levels under your control. Watch which "
     "rules become binding and which prices switch on.",
     "Drop the saw time to 25 and watch it acquire a price while another rule "
     "loses its own. Exactly two rules are ever paid for at once.",
     slider("s0", "planks in stock", 10, 70, 1, 44)
     + slider("s1", "hours of work", 5, 60, 1, 30)
     + slider("s2", "hours of saw time", 5, 60, 1, 32),
     r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const ss = ["s0", "s1", "s2"].map(id => document.getElementById(id));
function draw() {
  const b = ss.map(s => +s.value);
  ss.forEach(s => document.getElementById(s.id + "v").textContent = s.value);
  const p = Plot(cv, 0, 20, 0, 20);
  p.clear(); p.grid(2, 2); p.axes("tables", "chairs", 4, 4);
  const best = bestPlan(PROFIT, RECIPE, b);
  const y = best ? prices(PROFIT, RECIPE, b, best.x) : [0, 0, 0];
  const tight = best ? tightRows(RECIPE, b, best.x) : [];
  p.polygon(sortRound(corners(RECIPE, b)), p.P.plan, p.P.plan);
  for (let i = 0; i < RECIPE.length; i++) {
    const [a, bb] = RECIPE[i], hot = tight.includes(i);
    p.line(0, b[i] / bb, 20, (b[i] - 20 * a) / bb,
           hot ? p.P.price : p.P.muted, hot ? 2.2 : 1.1, hot ? null : [5, 4]);
  }
  if (best) p.dot(best.x[0], best.x[1], p.P.plan, 7);
  const lines = RECIPE.map((_, i) => {
    const used = best ? RECIPE[i][0] * best.x[0] + RECIPE[i][1] * best.x[1] : 0;
    const spare = b[i] - used;
    return ROWS[i].padEnd(9) + " spare " + spare.toFixed(2).padStart(6) +
           "   worth " + money(y[i]).padStart(7) +
           (spare > 1e-7 && y[i] > 1e-7 ? "   <- impossible" : "");
  });
  out.textContent =
    "best plan " + best.x[0].toFixed(2) + " tables, " + best.x[1].toFixed(2) +
    " chairs, worth " + money(best.value) + "\n\n" + lines.join("\n") +
    "\n\nnever both: spare capacity and a price above zero";
}
ss.forEach(s => s.addEventListener("input", draw));
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
     "The last column is the one to watch. A row with capacity to spare and a "
     "price above zero would break complementary slackness, and no setting of "
     "these three sliders can produce one."),

    (8, "Watch a price die",
     "The value of the workshop as one resource's stock changes, traced out "
     "in full. The marker is where the workshop currently is.",
     "Take the planks past 45. The curve goes flat and the plank price drops "
     "to nothing — the saw has become the thing standing in the way.",
     '<div class="row"><label for="which">which resource</label>'
     '<select id="which"><option value="0">planks</option>'
     '<option value="1">hours of work</option>'
     '<option value="2">saw time</option></select></div>'
     + slider("amt", "how much of it", 0, 80, 0.5, 44),
     r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const which = document.getElementById("which"), amt = document.getElementById("amt");
function valueAt(row, level) {
  const b = STOCK.slice(); b[row] = level;
  const best = bestPlan(PROFIT, RECIPE, b);
  return best ? best.value : 0;
}
function draw() {
  const row = +which.value, here = +amt.value;
  document.getElementById("amtv").textContent = here.toFixed(1);
  const p = Plot(cv, 0, 80, 0, 460);
  p.clear(); p.grid(10, 50); p.axes(ROWS[row] + " in stock", "best profit", 20, 100);
  const ctx = p.ctx;
  ctx.beginPath(); ctx.strokeStyle = p.P.plan; ctx.lineWidth = 2.4;
  for (let k = 0; k <= 400; k++) {
    const t = k * 80 / 400, v = valueAt(row, t);
    if (k === 0) ctx.moveTo(p.X(t), p.Y(v)); else ctx.lineTo(p.X(t), p.Y(v));
  }
  ctx.stroke();
  const v = valueAt(row, here);
  const step = 0.02;
  const up = (valueAt(row, here + step) - v) / step;
  const down = (v - valueAt(row, here - step)) / step;
  p.dot(here, v, p.P.plan, 7);
  p.line(here, 0, here, v, p.P.price, 1, [3, 3]);
  const same = Math.abs(up - down) < 1e-6;
  out.textContent =
    ROWS[row] + " in stock  " + here.toFixed(1) + "\n" +
    "best profit         " + money(v) + "\n" +
    (same
      ? "one more is worth   " + money(up)
      : "one MORE is worth   " + money(up) + "\n" +
        "one FEWER costs     " + money(down) + "\n" +
        "you are standing on a bend: the price here is not a single number");
}
which.addEventListener("change", draw); amt.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
     "The two rates are measured by re-solving a hundredth either side rather "
     "than by reading a formula, which is why standing exactly on a bend "
     "reports two different numbers instead of quietly picking one."),
]


def build_sandbox() -> None:
    out_dir = ROOT / "sandbox"
    out_dir.mkdir(exist_ok=True)
    for position, (number, title, lede, try_this, controls, widget, note) in \
            enumerate(SANDBOXES):
        pager = []
        if position > 0:
            pager.append(f'<a href="{SANDBOXES[position - 1][0]:02d}.html">'
                         f'← {SANDBOXES[position - 1][1]}</a>')
        pager.append('<a href="index.html">all four</a>')
        if position < len(SANDBOXES) - 1:
            pager.append(f'<a href="{SANDBOXES[position + 1][0]:02d}.html">'
                         f'{SANDBOXES[position + 1][1]} →</a>')
        (out_dir / f"{number:02d}.html").write_text(SANDBOX_PAGE.format(
            number=number, title=html.escape(title), lede=html.escape(lede),
            try_this=html.escape(try_this), controls=controls, note=html.escape(note),
            pager=" · ".join(pager), maths=MATHS, plot=PLOT, widget=widget,
            boot=THEME_BOOT))

    items = "\n".join(
        f'<li><a href="{n:02d}.html"><span class="num">{n}</span>{html.escape(t)}</a>'
        f'<span class="sub">{html.escape(l)}</span></li>'
        for n, t, l, *_ in SANDBOXES)
    (out_dir / "index.html").write_text(f"""<!doctype html>
<html lang="en" data-page="sandbox-index">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Things to play with — Illuminate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/site.css">
{THEME_BOOT}
</head>
<body>
<header class="bar">
  <a class="brand" href="../../">ILLUMINATE</a>
  <button class="toggle" id="theme" type="button" aria-label="Switch colour scheme">DARK</button>
</header>
<main class="prose">
<h1>Things to play with</h1>
<p>Four pages from the duality guide, each one a chapter you can push around.
They run entirely in the page.</p>
<ul class="chapters">{items}</ul>
<p><a href="../index.html">← back to the guide</a></p>
</main>
<script src="../../assets/site.js"></script>
</body>
</html>
""")
    print(f"  wrote {len(SANDBOXES)} sandbox pages + index")


# --- entry point -----------------------------------------------------------

JOBS = {"chapters": build_chapters, "page": render_page, "sandbox": build_sandbox}

if __name__ == "__main__":
    wanted = sys.argv[1:] or ["all"]
    if wanted == ["all"]:
        wanted = list(JOBS)
    for job in wanted:
        if job not in JOBS:
            raise SystemExit(f"unknown job {job!r}; try: {', '.join(JOBS)} or all")
        JOBS[job]()
