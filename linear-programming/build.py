"""Build the linear-programming topic from lesson.md.

    python build.py chapters | page | sandbox | all

The structure lives in `illuminate.site`; this file names the chapters and
holds the sandboxes' JavaScript.
"""

from __future__ import annotations

import sys
from pathlib import Path

from illuminate.site import (Chapter, Sandbox, Topic, chapter_markdown,  # noqa: F401
                             main, slider, split_lesson)

ROOT = Path(__file__).resolve().parent

CHAPTERS = [
    Chapter(0, "00-what-this-is", "What this is"),
    Chapter(1, "01-inside-the-walls", "A plan inside the walls"),
    Chapter(2, "02-best-is-a-corner", "The best plan sits on a corner"),
]

# A second copy of src/linprog's corner search, so the pages need no server.
# tests/test_sandbox.py runs it through node against the Python.
MATHS = r"""
const USE   = [[1, 2], [1, 1]];   // water, land used by an acre of wheat, of corn
const STOCK = [32, 20];
const PROFIT = [3, 5];            // thousand dollars an acre

function feasible(x, A, b) {
  if (x[0] < -1e-9 || x[1] < -1e-9) return false;
  for (let i = 0; i < A.length; i++)
    if (A[i][0] * x[0] + A[i][1] * x[1] > b[i] + 1e-9) return false;
  return true;
}

function corners(A, b) {
  const lines = A.map((r, i) => [r[0], r[1], b[i]]).concat([[1, 0, 0], [0, 1, 0]]);
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

// Every corner that ties for best, not just the first one found, because the
// page has to say so when a whole edge ties.
function bestCorners(c, A, b) {
  const pts = corners(A, b);
  const value = p => c[0] * p[0] + c[1] * p[1];
  const top = Math.max(...pts.map(value));
  return { value: top, at: pts.filter(p => Math.abs(value(p) - top) < 1e-9) };
}

function money(thousands) {
  return "$" + Math.round(thousands * 1000).toLocaleString("en-US");
}
"""

SANDBOXES = [
    Sandbox(2, "Change what the crops earn",
     "The farm, with the profit per acre of each crop under your control. The "
     "dashed line is every plan worth as much as the best one.",
     "Start corn at $5,000 and lower it slowly. Nothing happens, and then the "
     "best plan jumps to a different corner all at once. Find the price where "
     "two corners tie.",
     slider("pw", "an acre of wheat earns ($ thousand)", 0.5, 8, 0.25, 3)
     + slider("pc", "an acre of corn earns ($ thousand)", 0.5, 8, 0.25, 5),
     r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const pw = document.getElementById("pw"), pc = document.getElementById("pc");
function draw() {
  const c = [+pw.value, +pc.value];
  document.getElementById("pwv").textContent = money(c[0]);
  document.getElementById("pcv").textContent = money(c[1]);
  const p = Plot(cv, 0, 23, 0, 18.5);
  p.clear(); p.grid(2, 2); p.axes("acres of wheat", "acres of corn", 4, 4);
  const pts = sortRound(corners(USE, STOCK));
  p.polygon(pts, p.P.plan, p.P.plan);
  for (let i = 0; i < USE.length; i++)
    p.line(0, STOCK[i] / USE[i][1], 23, (STOCK[i] - 23 * USE[i][0]) / USE[i][1], p.P.muted, 1.1);
  const best = bestCorners(c, USE, STOCK);
  p.line(0, best.value / c[1], 23, (best.value - 23 * c[0]) / c[1], p.P.ink, 1.6, [6, 3]);
  for (const q of pts) p.dot(q[0], q[1], p.P.muted, 3.5);
  for (const q of best.at) p.dot(q[0], q[1], p.P.plan, 7);
  const plan = q => q[0] + " acres wheat, " + q[1] + " acres corn";
  out.textContent = (best.at.length > 1
    ? "a tie: every plan on the edge between\n  " + best.at.map(plan).join("\n  ") +
      "\nearns the same"
    : "best plan   " + plan(best.at[0])) +
    "\nworth       " + money(best.value);
}
pw.addEventListener("input", draw); pc.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
     "The page checks all four corners and keeps the best. That only works "
     "because the best plan is always at a corner, which is what chapter 2 "
     "argues."),
]

TOPIC = Topic(
    slug="linear-programming",
    root=ROOT,
    title="Corners, walls and prices: linear programming",
    blurb=("Linear programming from one small farm, following Tovey's Linear "
           "Optimization and Duality, with every number checked by code."),
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="# Corners, walls and prices",
)

if __name__ == "__main__":
    main(TOPIC, sys.argv[1:])
