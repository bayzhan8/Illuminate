"""Build the queueing topic from lesson.md.

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
    Chapter(1, "01-the-desk", "The desk"),
    Chapter(2, "02-draw-a-box", "Draw a box"),
    Chapter(3, "03-what-it-does-not-need", "What the law does not need"),
    Chapter(4, "04-the-multiplier", "Where the multiplier comes from"),
    Chapter(5, "05-the-wait-explodes", "The wait explodes before the clerk is full"),
    Chapter(6, "06-variance-not-utilisation", "The other dial"),
    Chapter(7, "07-the-long-job", "Why you keep arriving during the long job"),
    Chapter(8, "08-three-dials", "Three dials"),
    Chapter(9, "09-two-clerks", "Two clerks, one line"),
    Chapter(10, "10-when-pooling-loses", "When pooling is the wrong answer"),
    Chapter(11, "11-measuring-is-harder", "Measuring it is harder than computing it"),
    Chapter(12, "12-coverage", "The confidence interval is twenty times too narrow"),
    Chapter(13, "13-the-same-law-elsewhere", "The same law somewhere else"),
]

# The same formulas as src/queues, in JavaScript so the pages need no server.
# tests/test_lesson.py runs both over the same inputs.
MATHS = r"""
// One clerk, six minutes a job. Rates are per hour throughout.
const SERVICE_RATE = 10;

// Random arrivals, random service: the wait is the service time multiplied
// by one over the idle fraction.
function waitRandom(rate) {
  const load = rate / SERVICE_RATE;
  return load / (SERVICE_RATE - rate);          // hours
}

// Any service distribution, via Pollaczek-Khinchine written in the form that
// separates the three dials: utilisation, variability, and job length.
function waitWithSpread(rate, cv2) {
  const meanService = 1 / SERVICE_RATE;
  const load = rate * meanService;
  return (load / (1 - load)) * ((1 + cv2) / 2) * meanService;
}

// The chance every clerk is busy, by the Erlang B recursion, which never
// forms a^c or c! and so does not overflow.
function allBusy(servers, offered) {
  const load = offered / servers;
  let b = 1.0;
  for (let k = 1; k <= servers; k++) b = offered * b / (k + offered * b);
  return b / (1 - load * (1 - b));
}

function waitPooled(rate, servers) {
  const offered = rate / SERVICE_RATE;
  return allBusy(servers, offered) / (servers * SERVICE_RATE - rate);
}

function minutes(hours) { return hours * 60; }
"""

SANDBOXES = [
    Sandbox(
        8, "Turn the three dials",
        "The wait, as utilisation and service variability move independently. "
        "The clerk's average speed never changes.",
        "Set the variability to zero and push utilisation up to 95%. Then put "
        "utilisation back to 85% and raise the variability instead. The second "
        "one hurts more.",
        slider("busy", "fraction of time busy", 5, 97, 1, 90)
        + slider("cv2", "how variable the service is", 0, 25, 1, 1),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const busy = document.getElementById("busy"), cv2El = document.getElementById("cv2");
function draw() {
  const rho = +busy.value / 100, cv2 = +cv2El.value;
  document.getElementById("busyv").textContent = (100 * rho).toFixed(0) + "%";
  document.getElementById("cv2v").textContent = cv2.toFixed(0);
  const p = Plot(cv, 0, 1, 0, 240, { l: 60, r: 22, t: 20, b: 42 });
  p.clear(); p.grid(0.1, 40); p.axes("fraction of the time busy", "wait, minutes", 0.2, 40);

  // the curve at the chosen variability, and the textbook one for reference
  for (const [c2, colour, width] of [[1, p.P.muted, 1.4], [cv2, p.P.plan, 2.4]]) {
    p.ctx.beginPath(); p.ctx.strokeStyle = colour; p.ctx.lineWidth = width;
    for (let k = 0; k <= 400; k++) {
      const r = 0.005 + 0.985 * k / 400;
      const w = Math.min(minutes(waitWithSpread(r * SERVICE_RATE, c2)), 250);
      if (k === 0) p.ctx.moveTo(p.X(r), p.Y(w)); else p.ctx.lineTo(p.X(r), p.Y(w));
    }
    p.ctx.stroke();
  }
  const wait = minutes(waitWithSpread(rho * SERVICE_RATE, cv2));
  if (wait < 238) p.dot(rho, wait, p.P.plan, 7);
  p.label(0.02, 224, "grey: the textbook case, variability 1", p.P.muted, "left", 11);
  out.textContent =
    "busy            " + (100 * rho).toFixed(0) + "%\n" +
    "variability     " + cv2.toFixed(0) + "\n" +
    "average wait    " + (wait > 1e4 ? "off the scale" : wait.toFixed(1) + " min") + "\n\n" +
    "the clerk still averages six minutes a customer";
}
busy.addEventListener("input", draw); cv2El.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "The grey curve never moves: it is the same desk with textbook "
        "variability. Everything the blue curve does differently was bought or "
        "sold with variance, not with capacity."),

    Sandbox(
        9, "One line or several",
        "The same clerks and the same work, arranged as one shared queue or as "
        "one queue each.",
        "Drag the number of clerks up while keeping them equally busy. The "
        "single line pulls further ahead the more clerks there are, and the "
        "gap narrows as they get busier.",
        slider("clerks", "how many clerks", 1, 12, 1, 2)
        + slider("load", "how busy each one is", 20, 95, 1, 90),
        r"""
const cv = document.getElementById("c"), out = document.getElementById("out");
const clerks = document.getElementById("clerks"), load = document.getElementById("load");
function draw() {
  const c = +clerks.value, rho = +load.value / 100;
  document.getElementById("clerksv").textContent = c;
  document.getElementById("loadv").textContent = (100 * rho).toFixed(0) + "%";
  const total = c * rho * SERVICE_RATE;
  const apart = minutes(waitRandom(rho * SERVICE_RATE));   // one clerk's own queue
  const together = minutes(waitPooled(total, c));
  const p = Plot(cv, 0, 1, 0, 130, { l: 60, r: 22, t: 20, b: 42 });
  p.clear(); p.grid(0.1, 20); p.axes("how busy each clerk is", "wait, minutes", 0.2, 20);
  for (const [fn, colour] of [[r => minutes(waitRandom(r * SERVICE_RATE)), p.P.price],
                              [r => minutes(waitPooled(c * r * SERVICE_RATE, c)), p.P.plan]]) {
    p.ctx.beginPath(); p.ctx.strokeStyle = colour; p.ctx.lineWidth = 2.3;
    for (let k = 0; k <= 300; k++) {
      const r = 0.02 + 0.95 * k / 300;
      const w = Math.min(fn(r), 140);
      if (k === 0) p.ctx.moveTo(p.X(r), p.Y(w)); else p.ctx.lineTo(p.X(r), p.Y(w));
    }
    p.ctx.stroke();
  }
  p.dot(rho, Math.min(apart, 128), p.P.price, 6);
  p.dot(rho, Math.min(together, 128), p.P.plan, 6);
  p.label(0.03, 122, "a queue each", p.P.price, "left", 11);
  p.label(0.03, 110, "one shared queue", p.P.plan, "left", 11);
  out.textContent =
    c + " clerks, each busy " + (100 * rho).toFixed(0) + "% of the time\n" +
    "total arrivals   " + total.toFixed(1) + " per hour\n\n" +
    "a queue each     " + apart.toFixed(1) + " min\n" +
    "one shared queue " + together.toFixed(1) + " min\n" +
    (c === 1 ? "\nwith one clerk there is nothing to pool"
             : "\nthe shared queue is " + (apart / together).toFixed(2) + "x shorter");
}
clerks.addEventListener("input", draw); load.addEventListener("input", draw);
window.addEventListener("resize", draw);
document.addEventListener("themechange", draw);
draw();
""",
        "With one clerk the two arrangements are the same queue, and the page "
        "says so rather than reporting a meaningless ratio of one."),
]

TOPIC = Topic(
    slug="queues",
    root=ROOT,
    title="The wait is not about the speed — queues and Little's law",
    blurb=("Queueing theory and Little's law built from one clerk and a "
           "six-minute job, with every number checked by code."),
    chapters=CHAPTERS,
    sandboxes=SANDBOXES,
    maths=MATHS,
    heading="# The wait is not about the speed",
)

if __name__ == "__main__":
    main(TOPIC, sys.argv[1:])
