"""Cross-checks the sandbox page's JavaScript against the Python.

The page carries its own copy of the bound-tightening chain from chapter 4,
because it runs client-side with nothing behind it. Two copies of a formula
drift the moment one is edited alone, so both are run over the same spread of
inputs here. Requires `node`; without it only the structure assertions run.
"""

import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

SANDBOX = ROOT / "sandbox"
NODE = shutil.which("node") or shutil.which("nodejs")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_js(snippet: str):
    result = subprocess.run([NODE, "-e", build.MATHS + snippet],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# --- what the Python says --------------------------------------------------

def implied_open(demand, big_m) -> F:
    """The fractional bound the link row puts on the switch."""
    return F(demand, big_m)


def forced_open(demand, big_m) -> int:
    """And the whole number the integrality then rounds it up to."""
    return math.ceil(implied_open(demand, big_m))


# --- structure -------------------------------------------------------------

def test_a_page_exists_for_every_sandbox():
    for box in build.SANDBOXES:
        assert (SANDBOX / f"{box.chapter:02d}.html").exists()
    assert (SANDBOX / "index.html").exists()


def test_the_page_carries_its_own_logic():
    """Nothing is fetched at run time; a webfont may fail and nothing else."""
    for page in SANDBOX.glob("*.html"):
        html = page.read_text()
        for src in re.findall(r'<script[^>]*\bsrc="([^"]+)"', html):
            assert not src.startswith(("http://", "https://", "//")), src
        assert "fetch(" not in html and "XMLHttpRequest" not in html


def test_the_sandbox_the_lesson_links_to_is_the_one_that_exists():
    lesson = (ROOT / "lesson.md").read_text()
    linked = set(re.findall(r"/solvers/sandbox/(\d+)\.html", lesson))
    assert linked == {f"{box.chapter:02d}" for box in build.SANDBOXES}


# --- the two copies of the arithmetic --------------------------------------

@needs_node
def test_the_fractional_bound_matches_the_python():
    cases = [(d, m) for d in (0, 1, 7, 25, 60, 99, 100, 101, 120)
             for m in (10, 25, 100, 175, 200)]
    got = run_js(
        "console.log(JSON.stringify("
        + json.dumps(cases)
        + ".map(([d, m]) => impliedOpen(d, m))))")
    want = [float(implied_open(d, m)) for d, m in cases]
    assert got == pytest.approx(want, rel=1e-12, abs=1e-12)


@needs_node
def test_the_rounded_bound_matches_the_python():
    cases = [(d, m) for d in range(0, 121) for m in (10, 25, 100, 200)]
    got = run_js(
        "console.log(JSON.stringify("
        + json.dumps(cases)
        + ".map(([d, m]) => forcedOpen(d, m))))")
    want = [forced_open(d, m) for d, m in cases]
    assert got == want


@needs_node
def test_the_switch_is_forced_on_exactly_when_there_is_demand():
    """The claim chapter 4 makes: any demand at all settles the switch."""
    cases = [(d, 100) for d in range(0, 101)]
    got = run_js(
        "console.log(JSON.stringify("
        + json.dumps(cases)
        + ".map(([d, m]) => forcedOpen(d, m))))")
    assert got[0] == 0
    assert all(v == 1 for v in got[1:])


@needs_node
def test_demand_above_the_big_m_leaves_no_legal_setting():
    cases = [(d, 100) for d in (101, 110, 120)]
    got = run_js(
        "console.log(JSON.stringify("
        + json.dumps(cases)
        + ".map(([d, m]) => forcedOpen(d, m))))")
    # a yes/no switch cannot exceed one, so these models are impossible
    assert all(v > 1 for v in got)


@needs_node
def test_the_page_agrees_with_the_real_presolve_on_the_worked_instance():
    """The sandbox is a cartoon of one row. It still has to agree with the
    engine on the case the guide actually walks through."""
    from solvers import library as L

    got = run_js("console.log(JSON.stringify(forcedOpen(25, 100)))")
    assert got == 1
    j = [c.name for c in L.SMALL.cols].index("openB1")
    assert L.SMALL_PRESOLVED.fixed[j] == got
