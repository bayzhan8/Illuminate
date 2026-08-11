"""Every number lesson.md quotes, checked against the code that produced it.

Two rules hold throughout. Anything a reader could copy down is asserted here
against a computation, not against a number somebody typed twice. And where a
claim can be reached by a second route that shares no code with the first, it
is: the walk against brute-force corner enumeration, the barrier against the
exact rational simplex, the JavaScript on the sandbox pages against the Python.

Run `make render && make publish` before treating a failure here as real.
"""

import itertools
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import pytest

from twopaths.barrier import (Region, analytic_centre, centre_for, central_path,
                              duality_gap)
from twopaths.ellipsoid import run as ellipsoid_run
from twopaths.ellipsoid import shrink_factor
from twopaths.simplex import bland, dantzig, klee_minty, solve, steepest_edge

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

sys.path.insert(0, str(ROOT))
import build  # noqa: E402

SANDBOX = ROOT / "sandbox"
NODE = shutil.which("node") or shutil.which("nodejs")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
REGION = Region.build(A, B, PROFIT)
START = np.array([1.0, 1.0])


def _run_js(snippet: str):
    result = subprocess.run([NODE, "-e", build.MATHS + snippet],
                            capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# --- the workshop, by two routes that share no code ------------------------

def _corners_by_hand():
    """Every corner, from scratch: intersect each pair of walls and keep the
    ones that break nothing. Nothing here touches the simplex code."""
    walls = [(F(4), F(2), F(44)), (F(2), F(3), F(30)), (F(3), F(1), F(32)),
             (F(-1), F(0), F(0)), (F(0), F(-1), F(0))]
    found = set()
    for (a1, b1, c1), (a2, b2, c2) in itertools.combinations(walls, 2):
        det = a1 * b2 - a2 * b1
        if det == 0:
            continue
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        if all(a * x + b * y <= c for a, b, c in walls):
            found.add((x, y))
    return found


def test_the_workshop_has_five_corners_and_the_stated_best():
    corners = _corners_by_hand()
    assert len(corners) == 5
    best = max(corners, key=lambda p: 30 * p[0] + 20 * p[1])
    assert best == (F(9), F(4))
    assert 30 * best[0] + 20 * best[1] == 350
    assert "**9 tables and 4 chairs, worth $350**" in FLAT
    assert "Three hops, out of five corners" in FLAT


def test_the_walk_visits_the_corners_the_table_lists():
    result = solve(PROFIT, A, B, rule=dantzig)
    assert result.steps == 3
    assert result.value == 350
    assert result.x == (F(9), F(4))
    assert result.visited == [(F(0), F(0)), (F(32, 3), F(0)),
                              (F(10), F(2)), (F(9), F(4))]
    by_hand = _corners_by_hand()
    assert all(v in by_hand for v in result.visited)
    for worth in ("$0", "$320", "$340", "**$350**"):
        assert f"| {worth} |" in TEXT, worth
    assert "10⅔ tables" in TEXT
    assert 30 * F(32, 3) == 320


def test_every_rule_agrees_on_the_workshop():
    values = {solve(PROFIT, A, B, rule=r).value
              for r in (dantzig, bland, steepest_edge)}
    assert values == {350}


# --- chapter 3: the corner count -------------------------------------------

def test_the_corner_count_quoted_is_the_binomial():
    assert math.comb(60, 30) == 118_264_581_564_861_424
    assert f"{math.comb(60, 30):.2e}" == "1.18e+17"
    assert "**1.18 × 10¹⁷**" in FLAT
    assert "At 30 variables" in FLAT


def test_the_count_figure_uses_the_same_bound_as_the_prose():
    import fig03_the_count as fig
    assert fig.corner_bound(30) == math.comb(60, 30)


def test_the_prose_admits_the_observed_band_is_not_a_measurement():
    assert "not a\nmeasurement from this repository" in TEXT or \
           "not a measurement from this repository" in FLAT


# --- chapters 4 and 5: the cube, and the closed forms ----------------------

def _fibonacci(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


def test_dantzig_takes_exactly_two_to_the_n_minus_one():
    """Asserted against the formula at every size, not against stored counts."""
    for n in range(2, 13):
        assert solve(*klee_minty(n), rule=dantzig).steps == 2 ** n - 1
    assert "**2ⁿ − 1**" in FLAT
    assert "1024 corners and takes **1023\npivots**" in TEXT or \
           "1024 corners and takes **1023 pivots**" in FLAT


def test_bland_takes_exactly_twice_fibonacci_minus_one():
    """The claim that matters in chapter 5: anti-cycling is not efficiency."""
    for n in range(2, 15):
        assert solve(*klee_minty(n), rule=bland).steps == 2 * _fibonacci(n + 1) - 1
    assert "**2·Fib(n+1) − 1**" in FLAT
    assert solve(*klee_minty(10), rule=bland).steps == 177
    assert "177 rather than 1023" in FLAT


def test_the_bland_sequence_printed_in_the_prose_is_the_computed_one():
    counts = [solve(*klee_minty(n), rule=bland).steps for n in range(2, 11)]
    assert counts == [3, 5, 9, 15, 25, 41, 67, 109, 177]
    assert "3, 5, 9, 15, 25, 41, 67, 109, 177" in FLAT


def test_the_bland_growth_rate_really_is_the_golden_ratio():
    counts = [solve(*klee_minty(n), rule=bland).steps for n in range(2, 19)]
    ratio = counts[-1] / counts[-2]
    assert ratio == pytest.approx((1 + 5 ** 0.5) / 2, abs=1e-3)
    assert "about 1.618" in FLAT


def test_steepest_edge_escapes_this_cube_in_one_pivot():
    for n in range(2, 13):
        assert solve(*klee_minty(n), rule=steepest_edge).steps == 1
    assert "**one pivot**, at every size" in FLAT


def test_all_three_rules_reach_the_same_optimum_on_every_cube():
    """A step count only means anything if the answers agree."""
    for n in range(2, 13):
        problem = klee_minty(n)
        values = {solve(*problem, rule=r).value
                  for r in (dantzig, bland, steepest_edge)}
        assert len(values) == 1
        assert values == {F(100) ** (n - 1)}


def test_the_cube_really_has_two_to_the_n_corners_visited_by_dantzig():
    """Dantzig visiting 2^n - 1 edges means 2^n distinct corners seen."""
    for n in range(2, 9):
        seen = solve(*klee_minty(n), rule=dantzig).visited
        assert len({tuple(v) for v in seen}) == 2 ** n
    assert "visits **every single corner**" in FLAT


# --- chapter 6: the ellipsoid ----------------------------------------------

def _ellipsoid_for(target):
    walls = np.vstack([REGION.A, -np.eye(2), [-30.0, -20.0]])
    limits = np.concatenate([REGION.b, [0.0, 0.0], [-float(target)]])
    return ellipsoid_run(walls, limits, np.array([6.0, 6.0]), radius=20.0,
                         steps=400)


def test_the_ellipsoid_takes_the_number_of_cuts_quoted():
    steps = _ellipsoid_for(349)
    assert len(steps) - 1 == 29
    assert steps[-1].cut is None
    assert "**29\ncuts**" in TEXT or "**29 cuts**" in FLAT


def test_the_ellipsoid_ends_somewhere_legal_and_good_enough():
    steps = _ellipsoid_for(349)
    x = steps[-1].centre
    assert REGION.interior(x) or np.all(REGION.slack(x) >= -1e-9)
    assert PROFIT[0] * x[0] + PROFIT[1] * x[1] >= 349.0


def test_the_two_shrink_numbers_are_the_real_ones():
    guaranteed = shrink_factor(2)
    assert f"{guaranteed:.3f}" == "0.779"
    assert "about **0.779**" in FLAT
    steps = _ellipsoid_for(349)
    ratios = [steps[i + 1].volume / steps[i].volume for i in range(len(steps) - 1)]
    assert max(ratios) - min(ratios) < 1e-12, "the ratio should be constant"
    assert f"{ratios[0]:.4f}" == "0.7698"
    assert "**0.7698**" in FLAT
    assert all(r <= guaranteed + 1e-12 for r in ratios)


def test_the_optimal_half_ellipsoid_ratio_is_what_the_code_achieves():
    """0.7698 is not a constant of this implementation: it is the smallest
    ellipsoid that can contain half of one, in two dimensions."""
    n = 2
    best = (n / (n + 1)) * (n ** 2 / (n ** 2 - 1)) ** ((n - 1) / 2)
    steps = _ellipsoid_for(349)
    assert steps[1].volume / steps[0].volume == pytest.approx(best, rel=1e-12)
    assert "smallest ellipsoid that can contain the\nsurviving half" in TEXT or \
           "smallest ellipsoid that can contain the surviving half" in FLAT


def test_the_cost_per_digit_quoted_follows_from_that_ratio():
    ratio = 0.769800358919501
    per_digit = math.log(100) / -math.log(ratio)
    assert f"{per_digit:.1f}" == "17.6"
    assert "**17.6 cuts per decimal digit**" in FLAT


def test_the_ellipsoid_really_does_need_more_cuts_for_more_digits():
    counts = [len(_ellipsoid_for(t)) - 1
              for t in (340, 349, 349.9, 349.99, 349.999)]
    assert counts == sorted(counts)
    steps = [counts[i + 1] - counts[i] for i in range(len(counts) - 1)]
    assert np.mean(steps) == pytest.approx(17.6, abs=3.0)


# --- chapters 7 to 9: the barrier ------------------------------------------

def test_the_analytic_centre_quoted_is_the_computed_one():
    centre = analytic_centre(REGION, START)
    assert f"{centre[0]:.3f}" == "2.428" and f"{centre[1]:.3f}" == "3.209"
    assert "**(2.428, 3.209)**" in FLAT


def test_the_analytic_centre_ignores_the_objective():
    """It is a property of the shape, which is what the prose claims."""
    other = Region.build(A, B, [1, 99])
    assert np.allclose(analytic_centre(REGION, START),
                       analytic_centre(other, START), atol=1e-9)


def test_the_path_stays_strictly_inside_the_whole_way():
    curve = central_path(REGION, START, mu_from=8000.0, mu_to=1e-9, points=110)
    assert all(REGION.interior(point) for point in curve)
    assert REGION.slack(curve[-1]).min() > 0
    assert np.allclose(curve[-1], [9.0, 4.0], atol=1e-6)
    assert "never touching a wall" in FLAT


def test_the_landscape_panel_values_are_the_computed_ones():
    worths = {}
    for mu in (100.0, 10.0, 1.0):
        point = centre_for(REGION, mu, START)
        worths[mu] = PROFIT[0] * point[0] + PROFIT[1] * point[1]
    assert f"{worths[100.0]:.0f}" == "194"
    assert f"{worths[10.0]:.0f}" == "325"
    assert f"{worths[1.0]:.0f}" == "348"
    for shown in ("**$194**", "**$325**", "**$348**"):
        assert shown in FLAT, shown


def test_every_row_of_the_gap_table_is_computed():
    best = float(solve(PROFIT, A, B, rule=dantzig).value)
    expected = {
        100.0: ("3.762, 4.053", "$193.92", "$500.00", "$156.08"),
        10.0: ("8.408, 3.633", "$324.90", "$50.00", "$25.10"),
        1.0: ("9.019, 3.870", "$347.96", "$5.00", "$2.04"),
        0.1: ("9.004, 3.984", "$349.80", "$0.50", "$0.20"),
        0.01: ("9.000, 3.998", "$349.98", "$0.05", "$0.02"),
    }
    for mu, (plan, worth, promised, actual) in expected.items():
        point = centre_for(REGION, mu, START)
        value = PROFIT[0] * point[0] + PROFIT[1] * point[1]
        assert f"{point[0]:.3f}, {point[1]:.3f}" == plan, mu
        assert f"${value:,.2f}" == worth, mu
        assert f"${duality_gap(REGION, point, mu):,.2f}" == promised, mu
        assert f"${best - value:,.2f}" == actual, mu
        row = f"| {mu:g} | {plan} | {worth} | {promised} | {actual} |"
        assert row in TEXT, f"missing row: {row}"


def test_the_promise_is_never_broken():
    best = float(solve(PROFIT, A, B, rule=dantzig).value)
    for mu in (1e3, 1e2, 1e1, 1e0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        point = centre_for(REGION, mu, START)
        value = PROFIT[0] * point[0] + PROFIT[1] * point[1]
        assert best - value <= duality_gap(REGION, point, mu) + 1e-9


def test_the_bound_is_mu_times_the_number_of_walls():
    assert len(REGION.limits) == 5
    assert duality_gap(REGION, START, 1.0) == 5.0
    assert "**μ times the number of walls**" in FLAT
    assert "five walls (three rules and two floors)" in FLAT


# --- chapter 10: it never lands --------------------------------------------

def test_the_two_crossover_panels_are_a_hundredfold_apart():
    import fig10_crossover as fig
    (mu_a, away_a), (mu_b, away_b) = fig.crossover_png()
    assert (mu_a, mu_b) == (0.01, 1e-4)
    assert f"{away_a:.2e}" == "1.65e-03"
    assert f"{away_b:.2e}" == "1.65e-05"
    assert away_a / away_b == pytest.approx(100.0, rel=2e-2)
    assert "lands\nexactly 100 times closer" in TEXT or \
           "lands exactly 100 times closer" in FLAT


def test_the_distance_falls_in_step_with_mu_and_never_reaches_zero():
    corner = np.array([9.0, 4.0])
    far = {}
    for mu in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
        far[mu] = float(np.hypot(*(centre_for(REGION, mu, START) - corner)))
        assert far[mu] > 0.0
    keys = sorted(far, reverse=True)
    for a, b in zip(keys, keys[1:]):
        assert far[a] / far[b] == pytest.approx(10.0, rel=2e-2)
    assert "**there is no setting at which the\npoint becomes a corner**" in TEXT or \
           "**there is no setting at which the point becomes a corner**" in FLAT


# --- the history, in so far as a test can hold it --------------------------

def test_the_dates_are_the_ones_the_research_settled_on():
    """Not a check that history is right, only that the text was not edited
    into disagreeing with itself. The dates were verified against sources
    when the chapter was written; this pins them."""
    for year, what in (("1939", "Kantorovich"),
                       ("1940s", "computational"),
                       ("1947", "Dantzig"),
                       ("1955", "Frisch"),
                       ("1968", "Fiacco and McCormick"),
                       ("1969", "symposium"),
                       ("1972", "How good is the simplex algorithm?"),
                       ("1975", "Sveriges Riksbank Prize"),
                       ("1978", "Avis and Chv"),
                       ("1979", "Khachiyan"),
                       ("1984", "Karmarkar"),
                       ("2004", "Spielman"),
                       ("2012", "Santos"),
                       ("2022", "Zadeh"),
                       ("1967", "Walkup")):
        assert year in TEXT, year
        assert what in TEXT, what


def test_every_number_in_the_prose_is_either_computed_or_a_pinned_date():
    """The sweep that catches a figure edited in the text but not in the code.
    Every numeric token in the prose must appear verbatim in some .py file
    here, which for computed values means the test that asserts it and for
    dates means the list above."""
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", TEXT, flags=re.S)
    sources = "\n".join(p.read_text() for p in ROOT.rglob("*.py"))
    tiny = {str(n) for n in range(0, 13)} | {"20", "30", "32", "44"}
    orphans = [tok for tok in set(re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", body))
               if tok not in tiny
               and tok not in sources
               and tok.replace(",", "") not in sources]
    assert orphans == [], f"quoted but nowhere computed or pinned: {orphans}"


def test_the_von_neumann_story_is_marked_as_a_recollection():
    assert "Dantzig's own recollection" in FLAT
    assert "not independently documented" in FLAT


def test_the_prize_claim_is_stated_precisely():
    """It was not a Nobel Prize and Dantzig was not a recipient."""
    assert "Sveriges Riksbank Prize" in FLAT
    assert "was not among the recipients" in FLAT
    assert "National Medal of Science" in FLAT
    assert "Nobel" not in TEXT


def test_the_open_questions_are_still_described_as_open():
    assert "**No pivot rule is known to be polynomial, and whether one exists\nis open.**" in TEXT \
        or "**No pivot rule is known to be polynomial, and whether one exists is open.**" in FLAT
    assert "remains unsettled" in FLAT
    assert "Smale's problems" in FLAT


# --- figures ----------------------------------------------------------------

def test_lesson_image_links_all_resolve():
    assert [src for _, src in IMAGE.findall(TEXT) if not (ROOT / src).exists()] == []


def test_no_orphan_images_under_chapters():
    used = {src for _, src in IMAGE.findall(TEXT)}
    have = {str(p.relative_to(ROOT)) for p in (ROOT / "chapters").rglob("*")
            if p.suffix in {".png", ".gif"}}
    assert sorted(have - used) == []


def test_alt_text_is_a_real_description():
    assert [src for alt, src in IMAGE.findall(TEXT) if len(alt.strip()) < 40] == []


def test_every_figure_lives_in_the_chapter_that_shows_it():
    _, chapters, _ = build.split_lesson(build.TOPIC)
    for index, body in enumerate(chapters):
        folder = build.CHAPTERS[index].folder
        for _, src in IMAGE.findall(body):
            assert src.startswith(f"chapters/{folder}/"), \
                f"chapter {index} shows {src}, which is not in {folder}"


def test_every_figure_script_has_a_chapter_to_live_in():
    folders = {c.folder for c in build.CHAPTERS}
    for script in (ROOT / "figures").glob("fig*.py"):
        body = script.read_text()
        found = re.search(r'chapter_dir\("([^"]+)"\)', body)
        assert found, script.name
        assert found.group(1) in folders, f"{script.name} -> {found.group(1)}"


# --- structure --------------------------------------------------------------

def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, tail = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS) == 11
    assert front.startswith(build.TOPIC.heading)
    assert tail


def test_the_generated_chapter_files_are_up_to_date():
    _, chapters, _ = build.split_lesson(build.TOPIC)
    stale = []
    for index, body in enumerate(chapters):
        folder = build.CHAPTERS[index].folder
        path = ROOT / "chapters" / folder / "README.md"
        if not path.exists() or path.read_text() != \
                build.chapter_markdown(build.TOPIC, index, body):
            stale.append(folder)
    assert stale == [], "run: python build.py chapters"


def test_every_chapter_ends_on_a_landing():
    _, chapters, _ = build.split_lesson(build.TOPIC)
    for index, body in enumerate(chapters):
        assert "**In one sentence.**" in body, f"chapter {index} has no landing"


def test_every_invented_phrase_has_its_real_name():
    for standard in ("feasible region", "vertex", "pivot rule", "steepest edge",
                     "Klee-Minty", "smoothed analysis", "barrier parameter",
                     "central path", "analytic centre", "duality gap",
                     "crossover"):
        assert standard in TEXT, f"{standard} is never named"


def test_the_lesson_quotes_no_solver_benchmark_it_cannot_check():
    """Chapter 10 divides the labour without claiming timings for products
    whose behaviour this repository cannot verify."""
    for vendor in ("Gurobi", "CPLEX", "Xpress", "HiGHS", "COPT", "Mosek"):
        assert vendor not in TEXT, f"{vendor} appears; that is a dateable claim"


# --- the sandbox pages ------------------------------------------------------

def test_a_page_exists_for_every_sandbox():
    for box in build.SANDBOXES:
        assert (SANDBOX / f"{box.chapter:02d}.html").exists()
    assert (SANDBOX / "index.html").exists()


def test_the_pages_carry_their_own_logic():
    for page in SANDBOX.glob("*.html"):
        text = page.read_text()
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "cdn."):
            assert forbidden not in text
        for script in re.findall(r'<script src="([^"]+)"', text):
            assert script.startswith("../../assets/"), script


def test_every_sandbox_is_listed_on_the_index():
    listing = (SANDBOX / "index.html").read_text()
    for box in build.SANDBOXES:
        assert f"{box.chapter:02d}.html" in listing


@needs_node
def test_the_page_and_the_python_agree_on_every_pivot_count():
    got = _run_js("""
      const out = {};
      for (const rule of ["dantzig", "bland", "steepest"]) {
        out[rule] = [];
        for (let n = 2; n <= 12; n++) {
          const km = kleeMinty(n);
          out[rule].push(simplex(km.c, km.A, km.b, rule, 20000).steps);
        }
      }
      console.log(JSON.stringify(out));
    """)
    for name, rule in (("dantzig", dantzig), ("bland", bland),
                       ("steepest", steepest_edge)):
        assert got[name] == [solve(*klee_minty(n), rule=rule).steps
                             for n in range(2, 13)], name


@needs_node
def test_the_page_and_the_python_agree_on_the_central_path():
    got = _run_js("""
      const out = {};
      for (const e of [3, 2, 1, 0, -1, -2, -3, -4]) {
        out[String(e)] = centreFor(Math.pow(10, e), [1, 1]);
      }
      console.log(JSON.stringify(out));
    """)
    for power in (3, 2, 1, 0, -1, -2, -3, -4):
        mine = centre_for(REGION, 10.0 ** power, START)
        assert got[str(power)] == pytest.approx(list(mine), abs=1e-7), power


@needs_node
def test_the_page_never_leaves_the_region():
    got = _run_js("""
      const path = centralPath(1e4, 1e-7, 90);
      const worst = Math.min.apply(null, path.map(s => Math.min.apply(null, slack(s.x))));
      const last = path[path.length - 1];
      console.log(JSON.stringify({worst: worst, x: last.x, worth: worth(last.x)}));
    """)
    assert got["worst"] > 0
    assert got["x"] == pytest.approx([9.0, 4.0], abs=1e-5)
    assert got["worth"] == pytest.approx(350.0, abs=1e-4)
