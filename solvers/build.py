"""Build the solvers topic from lesson.md.

    python build.py chapters | page | sandbox | all
"""

from __future__ import annotations

import sys
from pathlib import Path

from illuminate.site import (Chapter, Sandbox, Topic, chapter_markdown, main,
                             slider, split_lesson)

ROOT = Path(__file__).resolve().parent

CHAPTERS = [
    Chapter(0, "00-what-this-is", "What this is"),
    Chapter(1, "01-not-an-algorithm", "A solver is not an algorithm"),
    Chapter(2, "02-what-it-removes", "What presolve takes out"),
    Chapter(3, "03-the-cascade", "The cascade, and where the gap opens"),
    Chapter(4, "04-a-decision-by-arithmetic", "A decision made by arithmetic"),
    Chapter(5, "05-what-it-costs", "What it costs you"),
    Chapter(6, "06-the-rest-of-the-machine", "The rest of the machine"),
    Chapter(7, "07-who-is-who", "Who is who"),
    Chapter(8, "08-a-layer-not-a-solver", "A layer is not a solver"),
    Chapter(9, "09-not-linear", "When the problem is not linear"),
    Chapter(10, "10-a-toolkit-is-not-a-solver", "What OR-Tools actually is"),
    Chapter(11, "11-the-benchmarks", "Why the benchmarks cannot be read straight"),
    Chapter(12, "12-measure-your-own", "Measure on your own models"),
    Chapter(13, "13-the-licence", "The licence is the deployment problem"),
    Chapter(14, "14-how-to-choose", "How to choose"),
]

# The bound-tightening chain from chapter 3, in JavaScript so the page needs no
# server. tests/test_sandbox.py runs this and the Python over the same inputs.
MATHS = r"""
// One link row: make <= M * open, with open a yes/no switch.
// Demand forces make up; the row then forces open up; integrality rounds it.
function impliedOpen(demand, bigM) {
  return demand / bigM;                      // before rounding
}
function forcedOpen(demand, bigM) {
  return Math.ceil(impliedOpen(demand, bigM) - 1e-12);
}
function verdict(demand, bigM) {
  if (demand <= 0) return "nothing forces a setup";
  if (demand > bigM) return "no setting of the switch is legal";
  return "the switch is forced on before any search runs";
}
"""

SANDBOXES = [
    Sandbox(
        4, "Watch a decision get made without a search",
        "The link row says production cannot exceed the big-M constant times "
        "the setup switch. Demand pushes production up from below. Somewhere "
        "in between, the switch stops being a decision.",
        "Put demand at zero and the switch is free. Raise it by one unit and "
        "the fraction lifts off the floor, rounding takes it to 1, and the "
        "search never gets asked. Then push demand past the big-M constant and "
        "watch the model become impossible.",
        slider("demand", "units demanded", 0, 120, 1, 25)
        + slider("bigm", "the big-M constant", 10, 200, 5, 100),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const dEl = document.getElementById("demand"), mEl = document.getElementById("bigm");

function draw() {
  const d = +dEl.value, M = +mEl.value;
  document.getElementById("demandv").textContent = d;
  document.getElementById("bigmv").textContent = M;

  const p = Plot(cv, 0, 120, 0, 1.35, { l: 62, r: 22, t: 20, b: 42 });
  p.clear();
  p.grid(20, 0.25);
  // ticks every half, not every quarter: the shared formatter derives its
  // decimal places from the step, and a step of 0.25 prints 0.25 as "0.3",
  // which is the one number on this page that has to be exact
  p.axes("units demanded", "lower bound on the switch", 20, 0.5);

  // the fractional bound demand/M, and the whole-number bound above it
  p.ctx.beginPath();
  p.ctx.strokeStyle = p.P.muted; p.ctx.lineWidth = 1.6;
  for (let k = 0; k <= 240; k++) {
    const x = 120 * k / 240, y = Math.min(impliedOpen(x, M), 1.3);
    if (k === 0) p.ctx.moveTo(p.X(x), p.Y(y)); else p.ctx.lineTo(p.X(x), p.Y(y));
  }
  p.ctx.stroke();

  p.ctx.beginPath();
  p.ctx.strokeStyle = p.P.plan; p.ctx.lineWidth = 2.6;
  for (let k = 0; k <= 240; k++) {
    const x = 120 * k / 240, y = Math.min(forcedOpen(x, M), 1.3);
    if (k === 0) p.ctx.moveTo(p.X(x), p.Y(y)); else p.ctx.lineTo(p.X(x), p.Y(y));
  }
  p.ctx.stroke();

  // where the reader is standing
  const frac = Math.min(impliedOpen(d, M), 1.3);
  const whole = Math.min(forcedOpen(d, M), 1.3);
  p.dot(d, frac, p.P.muted);
  p.dot(d, whole, p.P.plan);
  // both labels sit clear of their dots, and flip side near the right edge
  const side = d > 88 ? "right" : "left";
  const nudge = d > 88 ? -3 : 3;
  p.label(d + nudge, whole + 0.10, "forced to " + forcedOpen(d, M), p.P.plan, side);
  p.label(d + nudge, Math.max(frac - 0.09, 0.04),
          impliedOpen(d, M).toFixed(2) + " before rounding", p.P.muted, side, 11);

  out.textContent =
    "production must reach " + d + ", so the switch must reach " +
    d + "/" + M + " = " + impliedOpen(d, M).toFixed(3) +
    ", and a whole number at or above that is " + forcedOpen(d, M) +
    ". " + verdict(d, M) + ".";
}
[dEl, mEl].forEach(el => el.addEventListener("input", draw));
draw();
""",
        "The fainter line is the bound before rounding, the solid one after. "
        "Rounding a bound on a whole-number variable is the cheapest reasoning "
        "in the whole solver, and on this row it settles the variable outright."),
]

TOPIC = Topic(
    slug="solvers",
    root=ROOT,
    title="What solvers actually do",
    blurb="What is inside an optimisation solver, why presolve is where most "
          "of the work happens, and how the commercial and open-source ones "
          "actually differ once you have to deploy one.",
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="What solvers actually do",
)

if __name__ == "__main__":
    main(TOPIC, sys.argv[1:])
