"""Build the simplex-against-interior-point topic from lesson.md."""

from __future__ import annotations

import sys
from pathlib import Path

from illuminate.site import (Chapter, Sandbox, Topic, chapter_markdown, main,
                             slider, split_lesson)

ROOT = Path(__file__).resolve().parent

CHAPTERS = [
    Chapter(0, "00-what-this-is", "What this is"),
    Chapter(1, "01-a-new-kind-of-problem", "A new kind of problem"),
    Chapter(2, "02-along-the-edge", "Along the edge"),
    Chapter(3, "03-it-should-have-been-slow", "It should have been slow"),
    Chapter(4, "04-the-cube", "Klee and Minty build a cube"),
    Chapter(5, "05-not-the-rule", "Where the exponent lives"),
    Chapter(6, "06-not-cycling-is-not-fast", "Bland's rule finishes, slowly"),
    Chapter(7, "07-every-rule-has-a-cube", "Every rule has a cube"),
    Chapter(8, "08-why-nobody-meets-one", "Why nobody ever meets one"),
    Chapter(9, "09-polynomial-and-slower", "Polynomial, and slower"),
    Chapter(10, "10-the-wall-that-pushes-back", "The wall that pushes back"),
    Chapter(11, "11-the-central-path", "The central path"),
    Chapter(12, "12-what-the-barrier-does", "What the barrier actually does"),
    Chapter(13, "13-a-gap-you-can-forecast", "A gap you can forecast"),
    Chapter(14, "14-neither-one-won", "Neither one won"),
]

# The same two methods as src/twopaths, in JavaScript so the pages need nothing
# behind them. tests/test_lesson.py runs both over the same inputs and checks
# that they agree, which is the only reason to trust a reimplementation.
MATHS = r"""
// --- the squashed cube, and a simplex whose pivot rule is an argument -------

function kleeMinty(n) {
  const c = [], A = [], b = [];
  for (let j = 0; j < n; j++) c.push(Math.pow(2, n - j - 1));
  for (let i = 0; i < n; i++) {
    const row = [];
    for (let j = 0; j < i; j++) row.push(2 * Math.pow(10, i - j));
    row.push(1);
    for (let j = i + 1; j < n; j++) row.push(0);
    A.push(row);
    b.push(Math.pow(100, i));
  }
  return { c, A, b };
}

function dantzig(obj, width) {
  let best = 0, at = null;
  for (let j = 0; j < width; j++) if (obj[j] < best) { best = obj[j]; at = j; }
  return at;
}

function bland(obj, width) {
  for (let j = 0; j < width; j++) if (obj[j] < -1e-9) return j;
  return null;
}

function steepest(obj, width, T) {
  let bestScore = null, at = null;
  for (let j = 0; j < width; j++) {
    if (obj[j] >= -1e-9) continue;
    let len = 1;
    for (let i = 1; i < T.length; i++) len += T[i][j] * T[i][j];
    const score = (obj[j] * obj[j]) / len;
    if (bestScore === null || score > bestScore) { bestScore = score; at = j; }
  }
  return at;
}

const RULES = { dantzig: dantzig, bland: bland, steepest: steepest };

// Maximise c.x subject to Ax <= b, x >= 0, from the slack basis at the origin.
// Returns the pivot count and the value; the cube's numbers span many orders
// of magnitude, so this is floating point and the Python side is exact.
function simplex(c, A, b, ruleName, limit) {
  const rows = A.length, cols = c.length, width = cols + rows;
  const T = [];
  const top = [];
  for (let j = 0; j < cols; j++) top.push(-c[j]);
  for (let j = 0; j < rows; j++) top.push(0);
  top.push(0);
  T.push(top);
  for (let i = 0; i < rows; i++) {
    const row = A[i].slice();
    for (let j = 0; j < rows; j++) row.push(i === j ? 1 : 0);
    row.push(b[i]);
    T.push(row);
  }
  const basis = [];
  for (let i = 0; i < rows; i++) basis.push(cols + i);
  const rule = RULES[ruleName];

  for (let step = 0; step <= (limit || 100000); step++) {
    const entering = ruleName === "steepest"
      ? steepest(T[0], width, T) : rule(T[0], width);
    if (entering === null) return { steps: step, value: T[0][width] };
    let bestKey = null, bestRow = -1;
    for (let i = 1; i <= rows; i++) {
      if (T[i][entering] > 1e-12) {
        const ratio = T[i][width] / T[i][entering];
        if (bestKey === null || ratio < bestKey - 1e-12 ||
            (Math.abs(ratio - bestKey) <= 1e-12 && basis[i - 1] < basis[bestRow - 1])) {
          bestKey = ratio; bestRow = i;
        }
      }
    }
    if (bestRow < 0) return { steps: step, value: Infinity };
    const piece = T[bestRow][entering];
    for (let j = 0; j <= width; j++) T[bestRow][j] /= piece;
    for (let i = 0; i <= rows; i++) {
      if (i === bestRow || T[i][entering] === 0) continue;
      const factor = T[i][entering];
      for (let j = 0; j <= width; j++) T[i][j] -= factor * T[bestRow][j];
    }
    basis[bestRow - 1] = entering;
  }
  return { steps: -1, value: NaN };
}

// --- the workshop, and the barrier that walks through the middle of it -----

const WA = [[4, 2], [2, 3], [3, 1]];
const WB = [44, 30, 32];
const WPROFIT = [30, 20];

// Every wall as w.x <= limit: the three rules, then the two floors.
const WALLS = [[4, 2], [2, 3], [3, 1], [-1, 0], [0, -1]];
const LIMITS = [44, 30, 32, 0, 0];

function slack(x) { return LIMITS.map((c, i) => c - WALLS[i][0] * x[0] - WALLS[i][1] * x[1]); }
function inside(x) { return slack(x).every(s => s > 0); }

function barrier(x, mu) {
  const room = slack(x);
  if (room.some(s => s <= 0)) return Infinity;
  let logs = 0;
  for (const s of room) logs += Math.log(s);
  return -(WPROFIT[0] * x[0] + WPROFIT[1] * x[1]) - mu * logs;
}

// Damped Newton on the barrier. Halving until the step lands somewhere legal
// is the whole safeguard: a full step walks through a wall, where the thing
// being minimised is not merely worse but undefined.
function centreFor(mu, start) {
  let x = start.slice();
  for (let it = 0; it < 200; it++) {
    const room = slack(x);
    let g = [-WPROFIT[0], -WPROFIT[1]];
    let H = [[0, 0], [0, 0]];
    for (let i = 0; i < WALLS.length; i++) {
      const inv = 1 / room[i];
      g[0] += mu * WALLS[i][0] * inv;
      g[1] += mu * WALLS[i][1] * inv;
      const w = mu * inv * inv;
      H[0][0] += w * WALLS[i][0] * WALLS[i][0];
      H[0][1] += w * WALLS[i][0] * WALLS[i][1];
      H[1][0] += w * WALLS[i][1] * WALLS[i][0];
      H[1][1] += w * WALLS[i][1] * WALLS[i][1];
    }
    const det = H[0][0] * H[1][1] - H[0][1] * H[1][0];
    if (Math.abs(det) < 1e-300) break;
    const d = [(-g[0] * H[1][1] + g[1] * H[0][1]) / det,
               (-g[1] * H[0][0] + g[0] * H[1][0]) / det];
    let len = 1, ok = false;
    for (let k = 0; k < 80; k++) {
      const trial = [x[0] + len * d[0], x[1] + len * d[1]];
      if (inside(trial) && barrier(trial, mu) <= barrier(x, mu)) { ok = true; break; }
      len /= 2;
    }
    if (!ok) break;
    x = [x[0] + len * d[0], x[1] + len * d[1]];
    if (Math.hypot(len * d[0], len * d[1]) < 1e-13) break;
  }
  return x;
}

function centralPath(muFrom, muTo, points) {
  const out = [];
  let x = [1, 1];
  for (let k = 0; k < points; k++) {
    const t = points === 1 ? 0 : k / (points - 1);
    const mu = Math.exp(Math.log(muFrom) + t * (Math.log(muTo) - Math.log(muFrom)));
    x = centreFor(mu, x);
    out.push({ mu: mu, x: x.slice() });
  }
  return out;
}

function worth(x) { return WPROFIT[0] * x[0] + WPROFIT[1] * x[1]; }
"""

SANDBOXES = [
    Sandbox(
        5, "Change the rule, not the method",
        "The same cube and the same simplex code. The only thing the control "
        "changes is which improving column gets entered.",
        "Set the rule to Dantzig and raise the dimension one notch at a time. "
        "The count doubles. Switch to Bland at the same dimension and watch it "
        "drop without becoming anything you would call small.",
        '<div class="row"><label for="rule">pivot rule</label>'
        '<select id="rule">'
        '<option value="dantzig">Dantzig: fastest improvement per unit</option>'
        '<option value="bland">Bland: lowest-numbered improving column</option>'
        '<option value="steepest">steepest edge: per unit of movement</option>'
        '</select></div>'
        + slider("dim", "dimension of the cube", 2, 12, 1, 6),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const ruleEl = document.getElementById("rule"), dimEl = document.getElementById("dim");
const MAXN = 12;

function series(name, upto) {
  const pts = [];
  for (let n = 2; n <= upto; n++) {
    const km = kleeMinty(n);
    pts.push(simplex(km.c, km.A, km.b, name, 20000).steps);
  }
  return pts;
}

function draw() {
  const name = ruleEl.value, n = +dimEl.value;
  document.getElementById("dimv").textContent = n;
  const counts = series(name, MAXN);

  const p = Plot(cv, 2, MAXN, -0.35, Math.log10(8192), { l: 62, r: 22, t: 20, b: 44 });
  p.clear(); p.grid(1, 1); p.axes("dimension", "pivots (log scale)", 1, 1);

  // Every rule drawn faintly, the chosen one on top: the point of the page is
  // that these are three readings of one method.
  for (const other of ["dantzig", "bland", "steepest"]) {
    if (other === name) continue;
    const s = series(other, MAXN);
    p.ctx.beginPath(); p.ctx.strokeStyle = p.P.muted; p.ctx.lineWidth = 1;
    s.forEach((v, k) => {
      const Y = Math.log10(Math.max(v, 1));
      if (k === 0) p.ctx.moveTo(p.X(k + 2), p.Y(Y)); else p.ctx.lineTo(p.X(k + 2), p.Y(Y));
    });
    p.ctx.stroke();
  }
  p.ctx.beginPath();
  p.ctx.strokeStyle = name === "dantzig" ? p.P.price : p.P.plan;
  p.ctx.lineWidth = 2;
  counts.forEach((v, k) => {
    const Y = Math.log10(Math.max(v, 1));
    if (k === 0) p.ctx.moveTo(p.X(k + 2), p.Y(Y)); else p.ctx.lineTo(p.X(k + 2), p.Y(Y));
  });
  p.ctx.stroke();
  p.dot(n, Math.log10(Math.max(counts[n - 2], 1)),
        name === "dantzig" ? p.P.price : p.P.plan, 5);

  // n pivots means n + 1 corners stood on, which is the number worth
  // reporting: Dantzig takes 2^n - 1 pivots and sees all 2^n corners.
  const here = counts[n - 2], corners = Math.pow(2, n);
  out.textContent =
    "cube in " + n + " dimensions\n" +
    "  corners        " + corners + "\n" +
    "  pivots taken   " + here + "\n" +
    "  corners stood on " + (here + 1) + " of " + corners +
      "  (" + (100 * (here + 1) / corners).toFixed(1) + "%)\n\n" +
    (name === "dantzig"
      ? "every corner, at every size: 2^n - 1."
      : name === "bland"
        ? "2 Fib(n+1) - 1. still exponential, base 1.618 instead of 2."
        : "one pivot. this cube was not built against this rule.");
}
ruleEl.addEventListener("change", draw); dimEl.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "Nothing about the cube changes between these three readings. The "
        "exponent belongs to the rule."),

    Sandbox(
        11, "Turn the repulsion down",
        "The barrier problem for the workshop, solved exactly at whatever mu "
        "you choose. The curve is where the answer goes as you sweep it.",
        "Start at the far left, where profit is irrelevant and the point sits "
        "at the analytic centre. Drag towards zero and watch the receipt at "
        "the bottom: the promise shrinks in step with mu, and the real gap "
        "stays under it the whole way.",
        slider("mu", "log10 of mu", -6, 4, 0.1, 2),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const muEl = document.getElementById("mu");
const CORNERS = [[0, 0], [32 / 3, 0], [10, 2], [9, 4], [0, 10]];
const BEST = 350;

function draw() {
  const mu = Math.pow(10, +muEl.value);
  document.getElementById("muv").textContent = mu.toPrecision(3);

  const p = Plot(cv, 0, 12.4, 0, 11.4, { l: 52, r: 22, t: 20, b: 44 });
  p.clear(); p.grid(2, 2); p.axes("tables", "chairs", 2, 2);

  p.ctx.beginPath(); p.ctx.strokeStyle = p.P.text; p.ctx.lineWidth = 1.4;
  CORNERS.concat([CORNERS[0]]).forEach((c, k) => {
    if (k === 0) p.ctx.moveTo(p.X(c[0]), p.Y(c[1])); else p.ctx.lineTo(p.X(c[0]), p.Y(c[1]));
  });
  p.ctx.stroke();

  const path = centralPath(1e4, 1e-7, 90);
  p.ctx.beginPath(); p.ctx.strokeStyle = p.P.price; p.ctx.lineWidth = 1.2;
  p.ctx.globalAlpha = 0.45;
  path.forEach((s, k) => {
    if (k === 0) p.ctx.moveTo(p.X(s.x[0]), p.Y(s.x[1])); else p.ctx.lineTo(p.X(s.x[0]), p.Y(s.x[1]));
  });
  p.ctx.stroke(); p.ctx.globalAlpha = 1;

  const x = centreFor(mu, [1, 1]);
  p.dot(9, 4, p.P.ok, 6);
  p.dot(x[0], x[1], p.P.price, 6);

  const value = worth(x);
  const promised = mu * WALLS.length;
  const room = Math.min.apply(null, slack(x));
  out.textContent =
    "mu = " + mu.toPrecision(3) + "\n" +
    "  plan            " + x[0].toFixed(4) + " tables, " + x[1].toFixed(4) + " chairs\n" +
    "  worth           $" + value.toFixed(4) + "\n" +
    "  nearest wall    " + room.toExponential(2) + " away\n\n" +
    "  promised within $" + promised.toFixed(4) + "  (5 walls x mu)\n" +
    "  actually within $" + (BEST - value).toFixed(4) + "\n" +
    (room > 0 ? "  still strictly inside, as it will be at every mu > 0."
              : "  on a wall, which should not happen.");
}
muEl.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "The promise is 5 mu at every setting, and the real gap sits under it "
        "at every setting. That is what a forecastable method looks like."),
]

TOPIC = Topic(
    slug="corners-vs-centre",
    root=ROOT,
    title="Along the edge, or through the middle — simplex against interior point",
    blurb=("Why linear programming has two serious methods, where each came "
           "from, and what each one actually does."),
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="# Along the edge, or through the middle",
)

if __name__ == "__main__":
    main(TOPIC, sys.argv[1:])
