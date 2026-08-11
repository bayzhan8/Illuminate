"""Build the first-order / GPU topic from lesson.md."""

from __future__ import annotations

import sys
from pathlib import Path

from illuminate.site import (Chapter, Sandbox, Topic, chapter_markdown, main,
                             slider, split_lesson)

ROOT = Path(__file__).resolve().parent

CHAPTERS = [
    Chapter(0, "00-what-this-is", "What this is"),
    Chapter(1, "01-wider-not-faster", "Wider, not faster"),
    Chapter(2, "02-the-wrong-shape", "Why simplex is the wrong shape"),
    Chapter(3, "03-one-operation", "A method made of one operation"),
    Chapter(4, "04-the-obvious-version", "The obvious version does not work"),
    Chapter(5, "05-one-term-different", "One term different"),
    Chapter(6, "06-fast-turn-slow-shrink", "It turns fast and shrinks slowly"),
    Chapter(7, "07-cancel-the-rotation", "Cancel the rotation"),
    Chapter(8, "08-the-same-answer", "Does it get the right answer?"),
    Chapter(9, "09-what-it-costs", "What it costs"),
    Chapter(10, "10-where-this-leaves-things", "Where this leaves things"),
]

# The same iteration as src/firstorder, in JavaScript so the pages run with
# nothing behind them. tests/test_lesson.py runs both over the same inputs.
MATHS = r"""
// the workshop: three shelves, two products
const A = [[4, 2], [2, 3], [3, 1]];
const B = [44, 30, 32];
const PROFIT = [30, 20];

function matvec(M, v) { return M.map(r => r.reduce((s, a, j) => s + a * v[j], 0)); }
function matTvec(M, v) {
  const out = new Array(M[0].length).fill(0);
  for (let i = 0; i < M.length; i++)
    for (let j = 0; j < M[i].length; j++) out[j] += M[i][j] * v[i];
  return out;
}
function clamp(v) { return v.map(t => Math.max(t, 0)); }

// largest stretch of A, by power iteration: sets the safe step size
function norm2(M) {
  let v = new Array(M[0].length).fill(1);
  for (let k = 0; k < 200; k++) {
    const w = matTvec(M, matvec(M, v));
    const n = Math.hypot(...w);
    v = w.map(t => t / n);
  }
  return Math.sqrt(Math.hypot(...matvec(M, v)) ** 2 / (Math.hypot(...v) ** 2));
}

// One sweep of either method. `extrapolate` is the single differing term:
// with it the prices see where the plan is heading, without it where it was.
function step(x, y, tau, sigma, extrapolate) {
  const grad = matTvec(A, y).map((t, j) => -PROFIT[j] + t);
  const xn = clamp(x.map((t, j) => t - tau * grad[j]));
  const lead = extrapolate ? xn.map((t, j) => 2 * t - x[j]) : x;
  const resid = matvec(A, lead).map((t, i) => t - B[i]);
  const yn = clamp(y.map((t, i) => t + sigma * resid[i]));
  return [xn, yn];
}

function run(iterations, stepSize, extrapolate, restartEvery) {
  let x = [0, 0], y = [0, 0, 0];
  const path = [[x.slice(), y.slice()]];
  let sx = [0, 0], sy = [0, 0, 0], seen = 0;
  for (let k = 1; k <= iterations; k++) {
    [x, y] = step(x, y, stepSize, stepSize, extrapolate);
    sx = sx.map((t, j) => t + x[j]); sy = sy.map((t, i) => t + y[i]); seen++;
    if (restartEvery && seen === restartEvery) {
      x = sx.map(t => t / seen); y = sy.map(t => t / seen);
      sx = [0, 0]; sy = [0, 0, 0]; seen = 0;
    }
    path.push([x.slice(), y.slice()]);
  }
  return path;
}

function value(x) { return PROFIT[0] * x[0] + PROFIT[1] * x[1]; }
function violation(x) {
  const over = matvec(A, x).map((t, i) => t - B[i]);
  return Math.max(0, ...over, ...x.map(t => -t));
}
"""

SANDBOXES = [
    Sandbox(
        5, "One term, on or off",
        "The two methods of chapters 4 and 5, on the workshop, with the "
        "extrapolation you can switch off.",
        "Turn anticipation off and watch it start cycling instead of settling. "
        "Then turn it back on and raise the step size until even that fails.",
        '<div class="row"><label for="mode">the prices see</label>'
        '<select id="mode">'
        '<option value="1">where the plan is heading</option>'
        '<option value="0">where the plan was</option>'
        '</select></div>'
        + slider("step", "step size", 2, 30, 1, 14),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const mode = document.getElementById("mode"), stepEl = document.getElementById("step");
const SHOWN = 300;
function draw() {
  const extrapolate = mode.value === "1";
  const tau = +stepEl.value / 100;
  document.getElementById("stepv").textContent = tau.toFixed(2);
  const path = run(SHOWN, tau, extrapolate, 0);
  const vals = path.map(p => value(p[0]));
  const p = Plot(cv, 0, SHOWN, -50, 850, { l: 58, r: 22, t: 20, b: 42 });
  p.clear(); p.grid(50, 100); p.axes("iterations", "claimed value", 100, 200);
  p.line(0, 350, SHOWN, 350, p.P.muted, 1.2, [4, 4]);
  p.label(SHOWN - 4, 372, "the answer, 350", p.P.muted, "right", 11);
  p.ctx.beginPath();
  p.ctx.strokeStyle = extrapolate ? p.P.plan : p.P.price;
  p.ctx.lineWidth = 1.8;
  vals.forEach((v, k) => {
    const V = Math.max(-50, Math.min(850, v));
    if (k === 0) p.ctx.moveTo(p.X(k), p.Y(V)); else p.ctx.lineTo(p.X(k), p.Y(V));
  });
  p.ctx.stroke();
  const last = path[path.length - 1][0];
  const tail = vals.slice(-60);
  const spread = Math.max(...tail) - Math.min(...tail);
  out.textContent =
    "after " + SHOWN + " iterations\n" +
    "  plan       " + last[0].toFixed(4) + " tables, " + last[1].toFixed(4) + " chairs\n" +
    "  claims     " + value(last).toFixed(4) + "\n" +
    "  breaks a rule by " + violation(last).toExponential(2) + "\n\n" +
    (spread < 1e-3
      ? "settled. the true answer is 9 tables, 4 chairs, 350."
      : "still swinging by " + spread.toFixed(1) + " over the last 60 steps: not converging.");
}
mode.addEventListener("change", draw); stepEl.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "The step size has a ceiling above which even the working method stops "
        "converging. That ceiling is the same rule that makes it contract so "
        "slowly below it, which is chapter 6."),

    Sandbox(
        7, "Restart it",
        "The same iteration, with the averaging of chapter 7. The cost per "
        "step is identical either way.",
        "Sweep the restart period. There is a best value near the length of one "
        "revolution of the spiral, and it beats never restarting by orders of "
        "magnitude.",
        slider("period", "restart every", 0, 120, 5, 40),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const period = document.getElementById("period");
const TRUE_X = [9, 4], TRUE_Y = [6.25, 2.5, 0], SHOWN = 600;
function far(state) {
  const [x, y] = state;
  return Math.hypot(x[0] - TRUE_X[0], x[1] - TRUE_X[1],
                    y[0] - TRUE_Y[0], y[1] - TRUE_Y[1], y[2] - TRUE_Y[2]);
}
function draw() {
  const every = +period.value;
  document.getElementById("periodv").textContent = every === 0 ? "never" : every;
  const tau = 0.9 / norm2(A);
  const plain = run(SHOWN, tau, true, 0).map(far);
  const fixed = run(SHOWN, tau, true, every).map(far);
  const p = Plot(cv, 0, SHOWN, -16, 2, { l: 58, r: 22, t: 20, b: 42 });
  p.clear(); p.grid(100, 2); p.axes("iterations", "log10 distance", 200, 4);
  for (const [series, colour, width] of [[plain, p.P.muted, 1.6],
                                         [fixed, p.P.plan, 2.2]]) {
    p.ctx.beginPath(); p.ctx.strokeStyle = colour; p.ctx.lineWidth = width;
    series.forEach((d, k) => {
      const L = Math.max(-16, Math.log10(Math.max(d, 1e-16)));
      if (k === 0) p.ctx.moveTo(p.X(k), p.Y(L)); else p.ctx.lineTo(p.X(k), p.Y(L));
    });
    p.ctx.stroke();
  }
  p.label(SHOWN - 6, -1.4, "never restarted", p.P.muted, "right", 11);
  const gain = plain[SHOWN] / Math.max(fixed[SHOWN], 1e-16);
  out.textContent =
    "after " + SHOWN + " iterations\n" +
    "  never restarted   " + plain[SHOWN].toExponential(2) + " away\n" +
    "  restarted         " + fixed[SHOWN].toExponential(2) + " away\n\n" +
    (every === 0 ? "restarting is off"
                 : "restarting is " + gain.toExponential(1) + " times closer, " +
                   "for the same number of matrix products");
}
period.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "Restarting far too often is worse than not restarting: averaging over "
        "a fraction of a turn does not cancel the rotation, it just discards "
        "progress."),
]

TOPIC = Topic(
    slug="lp-on-gpu",
    root=ROOT,
    title="The machine got wider, not faster — first-order LP",
    blurb=("Why linear programming had to change algorithms to use a GPU, "
           "built from one workshop and checked against an exact solver."),
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="# The machine got wider, not faster",
)

if __name__ == "__main__":
    main(TOPIC, sys.argv[1:])
