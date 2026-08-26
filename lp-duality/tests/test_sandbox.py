"""Cross-checks the canvas pages' JavaScript against `lpduality`.

The sandbox pages carry their own copy of the corner search, the prices and the
ceiling, since they run client-side with nothing behind them. Requires `node`;
without it only the HTML structure assertions execute.

The comparison is deliberately over many inputs rather than one, because the
failure being guarded against is a divergence that only shows up away from the
default slider positions.
"""

import json
import random
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from lpduality import workshop as w
from lpduality.duality import ceiling_from
from lpduality.lp import LP, solve
from lpduality.sensitivity import with_rhs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

SANDBOX = ROOT / "sandbox"
NODE = shutil.which("node") or shutil.which("nodejs")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_js(snippet: str):
    result = subprocess.run([NODE, "-e", build.MATHS + snippet],
                            capture_output=True, text=True, timeout=600)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# --- structure -------------------------------------------------------------

def test_a_page_exists_for_every_sandbox():
    for box in build.SANDBOXES:
        assert (SANDBOX / f"{box.chapter:02d}.html").exists()
    assert (SANDBOX / "index.html").exists()


def test_the_pages_carry_their_own_logic():
    """No script tag pointing anywhere but this repository, and no fetching.
    A webfont may fail to load; nothing else is allowed to."""
    for page in SANDBOX.glob("*.html"):
        text = page.read_text()
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "cdn."):
            assert forbidden not in text, f"{page.name} reaches out via {forbidden}"
        for script in re.findall(r'<script src="([^"]+)"', text):
            assert script.startswith("../../assets/"), script


def test_every_sandbox_is_linked_from_the_chapter_it_belongs_to():
    lesson = (ROOT / "lesson.md").read_text()
    for box in build.SANDBOXES:
        assert f"sandbox/{box.chapter:02d}.html" in lesson, \
            f"sandbox {box.chapter:02d} is not reachable from the lesson"


def test_every_sandbox_number_is_a_real_chapter():
    chapters = {c.number for c in build.CHAPTERS}
    assert {b.chapter for b in build.SANDBOXES} <= chapters


# --- the two implementations -----------------------------------------------

@needs_node
def test_the_pages_find_the_same_best_plan():
    got = run_js("""
      const best = bestPlan(PROFIT, RECIPE, STOCK);
      console.log(JSON.stringify({x: best.x, value: best.value}));
    """)
    assert got["value"] == float(w.BEST_PROFIT)
    assert got["x"] == [float(v) for v in w.PLAN]


@needs_node
def test_the_pages_find_the_same_prices():
    got = run_js("""
      const best = bestPlan(PROFIT, RECIPE, STOCK);
      console.log(JSON.stringify(prices(PROFIT, RECIPE, STOCK, best.x)));
    """)
    assert got == [float(p) for p in w.PRICES]


@needs_node
def test_the_pages_agree_about_prices_at_many_stock_levels():
    """Sandbox 06 lets the reader move all three stock levels, so the
    agreement has to hold across the whole range those sliders can reach."""
    rng = random.Random(41)
    cases = [[rng.randint(10, 70), rng.randint(5, 60), rng.randint(5, 60)]
             for _ in range(60)]
    got = run_js(f"""
      const cases = {json.dumps(cases)};
      console.log(JSON.stringify(cases.map(b => {{
        const best = bestPlan(PROFIT, RECIPE, b);
        return {{value: best.value, prices: prices(PROFIT, RECIPE, b, best.x)}};
      }})));
    """)
    for stock, js in zip(cases, got):
        lp = LP.build(c=w.PRIMAL.c, A=w.PRIMAL.A, b=stock, op="<=", sense="max",
                      var_names=w.PRIMAL.var_names, row_names=w.PRIMAL.row_names)
        here = solve(lp)
        assert js["value"] == pytest.approx(float(here.value), abs=1e-7)
        # a corner where more than two rules meet has more than one valid set
        # of prices, so the check there is that the page's prices are honest
        # and charge the same bill, not that they are the identical vector
        bill = sum(p * s for p, s in zip(js["prices"], stock))
        assert bill == pytest.approx(float(here.value), abs=1e-6)
        assert all(p >= -1e-9 for p in js["prices"])


@needs_node
def test_the_pages_agree_about_which_price_lists_prove_anything():
    rng = random.Random(9)
    cases = [[rng.randint(0, 12), rng.randint(0, 12), rng.randint(0, 12)]
             for _ in range(80)]
    got = run_js(f"""
      const cases = {json.dumps(cases)};
      console.log(JSON.stringify(
        cases.map(y => ceilingFrom(RECIPE, STOCK, PROFIT, y))));
    """)
    for y, js in zip(cases, got):
        here = ceiling_from(w.PRIMAL, [Fraction(v) for v in y])
        if here is None:
            assert js is None, f"{y} proves nothing, but the page printed {js}"
        else:
            assert js == pytest.approx(float(here))


@needs_node
def test_the_pages_agree_about_the_value_curve():
    """Sandbox 08 traces the curve by re-solving, which is what chapter 8
    draws; the two have to trace the same shape."""
    levels = [0, 5, 15, 20, 25, 40, 44, 45, 46, 50, 70, 80]
    got = run_js(f"""
      const levels = {json.dumps(levels)};
      console.log(JSON.stringify(levels.map(v => {{
        const b = STOCK.slice(); b[0] = v;
        const best = bestPlan(PROFIT, RECIPE, b);
        return best ? best.value : 0;
      }})));
    """)
    for level, js in zip(levels, got):
        here = solve(with_rhs(w.PRIMAL, w.WOOD, level)).value
        assert js == pytest.approx(float(here), abs=1e-7)


@needs_node
def test_the_page_never_prints_a_price_list_that_proves_nothing():
    """The bug this guards against: reading prices off whichever rows the plan
    is pressed against returns, on degenerate corners, a list that undercharges
    for a product nobody is currently building. The bill still comes out right,
    so the page's own "the same number, every time" check cannot see it.

    Swept exhaustively over every reachable setting of sandbox 06's three
    sliders, which is where it was found: 1,673 of 191,296 settings were wrong.
    """
    got = run_js("""
      let dualInfeasible = 0, billMismatch = 0, slackButPriced = 0;
      for (let p = 10; p <= 70; p++)
        for (let h = 5; h <= 60; h++)
          for (let s = 5; s <= 60; s++) {
            const b = [p, h, s];
            const best = bestPlan(PROFIT, RECIPE, b);
            if (!best) continue;
            const y = prices(PROFIT, RECIPE, b);
            if (!covers(PROFIT, RECIPE, y)) dualInfeasible++;
            const bill = y.reduce((t, v, i) => t + v * b[i], 0);
            if (Math.abs(bill - best.value) > 1e-6) billMismatch++;
            for (let i = 0; i < 3; i++) {
              const used = RECIPE[i][0] * best.x[0] + RECIPE[i][1] * best.x[1];
              if (b[i] - used > 1e-7 && y[i] > 1e-7) slackButPriced++;
            }
          }
      console.log(JSON.stringify({dualInfeasible, billMismatch, slackButPriced}));
    """)
    assert got["dualInfeasible"] == 0, "the page charges less than a product earns"
    assert got["billMismatch"] == 0, "strong duality broken on the page"
    assert got["slackButPriced"] == 0, "spare capacity carrying a price"
