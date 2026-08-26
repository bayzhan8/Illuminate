"""Build the branch-and-price topic from lesson.md.

    python build.py chapters | page | sandbox | all

Everything structural lives in the shared `illuminate.site` module; this file
is what makes this topic itself.
"""

from __future__ import annotations

import sys
from pathlib import Path

from illuminate.site import (Chapter, Sandbox, Topic, chapter_markdown, main,
                             slider, split_lesson)

ROOT = Path(__file__).resolve().parent

CHAPTERS = [
    Chapter(0, "00-what-this-is", "What this is"),
    Chapter(1, "01-the-order", "The order"),
    Chapter(2, "02-the-obvious-model", "The obvious model, and why it is too weak"),
    Chapter(3, "03-one-variable-per-pattern", "One variable per pattern"),
    Chapter(4, "04-too-many-to-write-down", "Too many to write down"),
    Chapter(5, "05-start-with-a-few", "Start with a few"),
    Chapter(6, "06-what-the-prices-say", "What the prices are telling you"),
    Chapter(7, "07-the-same-from-the-dual", "The same test, from the other side"),
    Chapter(8, "08-a-knapsack", "Asking for a pattern is a knapsack"),
    Chapter(9, "09-the-loop", "The loop, and why it is allowed to stop"),
    Chapter(10, "10-branch-and-price", "Branching, when the answer is 6.5 boards"),
    Chapter(11, "11-where-this-leads", "Where this leads"),
]

# The same mathematics as src/bandp, written a second time in JavaScript so the
# pages need no server. tests/test_lesson.py runs both over the same inputs.
MATHS = r"""
const BOARD = 25;
const WIDTHS = [4, 9, 10];
const DEMANDS = [3, 6, 7];

// every maximal way to cut one board: nothing more would fit in the leftover
function allPatterns(board, widths) {
  const out = [];
  (function extend(i, left, sofar) {
    if (i === widths.length) {
      if (sofar.some(v => v > 0) && left < Math.min(...widths)) out.push(sofar.slice());
      return;
    }
    for (let k = 0; k <= Math.floor(left / widths[i]); k++)
      extend(i + 1, left - k * widths[i], sofar.concat([k]));
  })(0, board, []);
  return out;
}

function waste(pattern, board, widths) {
  return board - pattern.reduce((s, n, i) => s + n * widths[i], 0);
}

function describe(pattern, widths) {
  const parts = [];
  for (let i = 0; i < widths.length; i++)
    if (pattern[i]) parts.push(pattern[i] + "×" + widths[i]);
  return parts.length ? parts.join(" + ") : "nothing";
}

// Fill one board to maximise the value of the pieces taken off it: an
// unbounded knapsack, solved exactly by working up from an empty board.
function knapsack(prices, board, widths) {
  const best = new Array(board + 1).fill(0);
  const took = new Array(board + 1).fill(-1);
  for (let cap = 1; cap <= board; cap++)
    for (let i = 0; i < widths.length; i++)
      if (widths[i] <= cap && best[cap - widths[i]] + prices[i] > best[cap] + 1e-12) {
        best[cap] = best[cap - widths[i]] + prices[i];
        took[cap] = i;
      }
  const pattern = new Array(widths.length).fill(0);
  let cap = board;
  while (took[cap] >= 0) { pattern[took[cap]]++; cap -= widths[took[cap]]; }
  return { value: best[board], pattern: pattern };
}
"""

SANDBOXES = [
    Sandbox(
        8, "Ask for a pattern",
        "Set a price on each ordered length. The knapsack builds the single "
        "most valuable board there is at those prices — including patterns "
        "nobody has written down.",
        "Push the 4-foot price up on its own. The pattern the knapsack builds "
        "flips to all-short-pieces long before that price looks large.",
        slider("p0", "price of a 4 ft piece", 0, 1, 0.02, 0.17)
        + slider("p1", "price of a 9 ft piece", 0, 1, 0.02, 0.5)
        + slider("p2", "price of a 10 ft piece", 0, 1, 0.02, 0.5),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const ps = ["p0", "p1", "p2"].map(id => document.getElementById(id));
const SHADES = ["#dfe6f0", "#b9c9e0", "#8fa8cd"];
function draw() {
  const prices = ps.map(s => +s.value);
  ps.forEach(s => document.getElementById(s.id + "v").textContent = (+s.value).toFixed(2));
  const best = knapsack(prices, BOARD, WIDTHS);
  const p = Plot(cv, 0, BOARD, 0, 10, { l: 20, r: 20, t: 26, b: 30 });
  p.clear();
  let x = 0;
  for (let i = 0; i < WIDTHS.length; i++)
    for (let k = 0; k < best.pattern[i]; k++) {
      p.rect(x, 4, x + WIDTHS[i], 7, SHADES[i], 1);
      p.ctx.strokeStyle = p.P.ink; p.ctx.lineWidth = 1;
      p.ctx.strokeRect(p.X(x), p.Y(7), p.X(x + WIDTHS[i]) - p.X(x), p.Y(4) - p.Y(7));
      p.label(x + WIDTHS[i] / 2, 5.3, String(WIDTHS[i]), p.P.ink, "center", 11);
      x += WIDTHS[i];
    }
  if (x < BOARD) {
    p.rect(x, 4, BOARD, 7, p.P.muted, 0.18);
    p.label((x + BOARD) / 2, 5.3, "waste", p.P.muted, "center", 10);
  }
  p.ctx.strokeStyle = p.P.ink; p.ctx.lineWidth = 1.6;
  p.ctx.strokeRect(p.X(0), p.Y(7), p.X(BOARD) - p.X(0), p.Y(4) - p.Y(7));
  p.label(0, 8, "the best board at these prices", p.P.ink2, "left", 12);
  p.label(0, 2.4, describe(best.pattern, WIDTHS), p.P.plan, "left", 13);
  const helps = best.value > 1 + 1e-9;
  out.textContent =
    "pieces are worth   " + best.value.toFixed(3) + "\n" +
    "a board costs      1.000\n\n" +
    (helps
      ? "worth more than one board — this pattern is missing,\nadd it and solve again"
      : "worth no more than one board — no pattern anywhere\nwould help, so the model is already optimal");
}
ps.forEach(s => s.addEventListener("input", draw));
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "The knapsack does not pick from a list. It builds the winner from "
        "scratch, which is why its answer covers patterns that have never been "
        "written down."),

    Sandbox(
        9, "Run the loop",
        "Column generation on the 25-foot order, one round at a time: solve, "
        "read the prices, ask the knapsack, add.",
        "Step to the end. Three patterns get added, the number falls from 7 to "
        "6.5, and the last round is the one that proves there is nothing left.",
        '<div class="row"><label for="step">round</label>'
        '<input type="range" id="step" min="0" max="3" step="1" value="0">'
        '<output class="val" id="stepv"></output></div>',
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const step = document.getElementById("step");
// the rounds as the Python produced them; tests/test_lesson.py checks these
// against a live run rather than trusting the numbers pasted here
const ROUNDS = ROUNDS_JSON;
function draw() {
  const k = +step.value, r = ROUNDS[k];
  document.getElementById("stepv").textContent = (k + 1) + " of " + ROUNDS.length;
  const p = Plot(cv, 0, 4, 6.2, 7.2, { l: 54, r: 22, t: 22, b: 40 });
  p.clear(); p.grid(1, 0.2); p.axes("round", "boards needed", 1, 0.2);
  const xs = ROUNDS.map((_, i) => i);
  p.ctx.beginPath(); p.ctx.strokeStyle = p.P.plan; p.ctx.lineWidth = 2.4;
  ROUNDS.forEach((rr, i) => {
    if (i <= k) { const X = p.X(i), Y = p.Y(rr.value);
      if (i === 0) p.ctx.moveTo(X, Y); else p.ctx.lineTo(X, Y); }
  });
  p.ctx.stroke();
  ROUNDS.forEach((rr, i) => { if (i <= k) p.dot(i, rr.value, p.P.plan, 6); });
  p.line(0, 6.5, 4, 6.5, p.P.muted, 1, [4, 4]);
  p.label(3.9, 6.54, "6.5", p.P.muted, "right", 11);
  const prices = r.duals.map((d, i) => WIDTHS[i] + "ft " + d).join("   ");
  out.textContent =
    "holding " + r.held + " patterns   master needs " + r.value.toFixed(4) + " boards\n" +
    "prices   " + prices + "\n\n" +
    "knapsack builds  " + r.best + "\n" +
    "worth            " + r.bestValue.toFixed(4) + "\n" +
    (r.added ? "more than one board — add it, go again"
             : "exactly one board — nothing is missing, stop");
}
step.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "The last round is not wasted work. It is the round that proves the "
        "previous answer was already optimal, and without it you would only "
        "have a good number rather than the right one."),
]

TOPIC = Topic(
    slug="branch-and-price",
    root=ROOT,
    title="Solving a problem you never wrote down — column generation",
    blurb=("Column generation and branch-and-price built from a cutting-stock "
           "order, with every number checked by code."),
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="# Solving a problem you never wrote down",
)


def rounds_json() -> str:
    """The loop's rounds, as the page's JavaScript needs them.

    Baked in rather than recomputed in the browser: the sandbox shows the run
    the chapter shows, and the test compares this against a live solve so the
    two cannot drift.
    """
    import json

    from bandp import mill as m
    return json.dumps([
        {"held": len(r.patterns), "value": float(r.value),
         "duals": [str(d) for d in r.duals],
         "best": m.BOARDS.describe(r.best_pattern),
         "bestValue": float(r.best_value), "added": r.added}
        for r in m.ROUNDS])


if __name__ == "__main__":
    SANDBOXES[1].widget = SANDBOXES[1].widget.replace("ROUNDS_JSON", rounds_json())
    main(TOPIC, sys.argv[1:])
