"""Build the LP duality topic from lesson.md.

    python build.py chapters | page | sandbox | all

Everything structural lives in the shared `illuminate.site` module; this file
is just what makes this topic itself -- what its chapters are called, and what
its four interactive pages do.
"""

from __future__ import annotations

import sys
from pathlib import Path

from illuminate.site import (Chapter, Sandbox, Topic, chapter_markdown,
                             main, slider, split_lesson)

ROOT = Path(__file__).resolve().parent

CHAPTERS = [
    Chapter(0, "00-what-this-is", "What this is"),
    Chapter(1, "01-the-workshop", "The workshop"),
    Chapter(2, "02-no-way-to-check", "A good plan cannot prove itself best"),
    Chapter(3, "03-mixing-the-rules", "Charging for the ingredients"),
    Chapter(4, "04-every-mix-is-a-ceiling", "Every honest price list is a ceiling"),
    Chapter(5, "05-the-gap-closes", "The gap closes, every time"),
    Chapter(6, "06-who-is-binding", "Which rules are actually holding you back"),
    Chapter(7, "07-what-one-more-is-worth", "What one more plank is worth"),
    Chapter(8, "08-the-price-breaks", "The price is only local"),
    Chapter(9, "09-when-it-goes-wrong", "When it goes wrong"),
    Chapter(10, "10-where-this-leads", "Where this leads"),
]

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

SANDBOXES = [
    Sandbox(1, "Move the money",
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

    Sandbox(3, "Find a ceiling by hand",
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

    Sandbox(6, "Change the shelves",
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

    Sandbox(8, "Watch a price die",
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


TOPIC = Topic(
    slug="lp-duality",
    root=ROOT,
    title="Two problems, one number — LP duality",
    blurb=("Linear programming duality built from a workshop with three "
           "shelves and two products, with every number checked by code."),
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="# Two problems, one number",
)

if __name__ == "__main__":
    main(TOPIC, sys.argv[1:])
