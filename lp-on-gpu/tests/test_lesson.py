"""Consistency checks: lesson.md against firstorder, and generated files
against their generator.

Run `python build.py all` before treating any failure here as real.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from firstorder import story as s

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

sys.path.insert(0, str(ROOT))
import build  # noqa: E402

SANDBOX = ROOT / "sandbox"
NODE = shutil.which("node") or shutil.which("nodejs")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


def _run_js(snippet: str):
    result = subprocess.run([NODE, "-e", build.MATHS + snippet],
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# --- figures ---------------------------------------------------------------

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


# --- the numbers in the prose ----------------------------------------------

def test_the_arithmetic_intensity_arithmetic_is_right():
    assert s.INTENSITY == pytest.approx(2 / 12)
    assert f"{s.INTENSITY:.2f}" == "0.17"
    assert "**12 bytes per stored entry**" in FLAT
    assert "**2 operations**" in FLAT
    assert "**0.17 operations per byte.**" in FLAT


def test_the_two_machine_percentages_are_computed():
    lean = s.usable_fraction_for(256e9, 137.5e9) * 100
    rich = s.usable_fraction_for(26e12, 2e12) * 100
    assert f"{lean:.0f}" == "9" and f"{rich:.1f}" == "1.3"
    assert "**1.3%** of what it could do" in FLAT
    assert "**9%** of its own" in FLAT


def test_the_machine_balances_quoted_are_the_real_ones():
    """The number of operations each machine can do per byte it delivers.
    An earlier draft said 190 here, which was not either machine."""
    rich = 26e12 / 2e12
    lean = 256e9 / 137.5e9
    assert f"{rich:.0f}" == "13" and f"{lean:.1f}" == "1.9"
    assert "**13 operations for every byte**" in FLAT
    assert "1.9 operations per byte" in FLAT
    assert s.INTENSITY / rich == pytest.approx(0.0128, abs=5e-4)


def test_the_bandwidth_ratio_quoted_is_the_real_one():
    ratio = 2e12 / 137.5e9
    assert f"{ratio:.1f}" == "14.5"
    assert "**14.5×**" in FLAT
    arithmetic = 26e12 / 256e9
    assert round(arithmetic) == 102
    assert "about a hundred" in FLAT


def test_the_cycle_numbers_match_the_code():
    assert s.CYCLE_PERIOD == 10
    assert "**repeating cycle of period 10**" in FLAT
    assert f"{s.CYCLE_HIGH:.0f}" == "753"
    assert "**$0 and\n$753**" in TEXT or "**$0 and $753**" in FLAT
    assert s.CYCLE_LOW < 1.0


def test_the_spiral_numbers_match_the_code():
    assert f"{s.SPIRAL['rotation_degrees']:.1f}" == "11.5"
    assert f"{s.SPIRAL['iterations_per_turn']:.1f}" == "31.2"
    assert f"{(1 - s.SPIRAL['contraction']) * 100:.1f}" == "2.0"
    assert "**11.5°** per iteration" in FLAT
    assert "**31.2** steps" in FLAT
    assert "**2.0%** per iteration" in FLAT


def test_the_toy_spiral_distances_quoted_are_the_drawn_ones():
    import fig04_the_spiral as fig
    out = fig.walk(False)
    inn = fig.walk(True)
    answer = np.array(fig.ANSWER)
    start = np.hypot(*(np.array(fig.START) - answer))
    assert f"{start:.1f}" == "2.2"
    assert f"{np.hypot(*(out[-1] - answer)):.1f}" == "13.1"
    assert f"{np.hypot(*(inn[-1] - answer)):.2f}" == "0.36"
    assert "2.2 away from the answer and after 90 steps it is" in FLAT
    assert "13.1 away" in FLAT
    assert "0.36 away instead of 13.1" in FLAT


def test_the_headline_agreement_with_the_exact_solver():
    assert s.TRUE_PLAN.tolist() == [9.0, 4.0]
    assert s.TRUE_VALUE == 350.0
    assert s.TRUE_PRICES.tolist() == [6.25, 2.5, 0.0]
    assert "**9 tables and 4 chairs, worth $350**" in FLAT
    assert "**$6.25** a plank" in FLAT and "**$2.50** an hour" in FLAT


def test_the_early_iterate_really_does_cheat():
    x, _ = s.converging_run(10).last
    value = -float(s.WORKSHOP.c @ x)
    violation = s.WORKSHOP.violation(x)
    assert value > s.TRUE_VALUE and violation > 0
    assert f"{violation:.2f}" == "0.84"
    assert f"{value:.2f}" == "352.44"
    assert "0.84 planks" in FLAT
    assert "**$352.44**" in FLAT


def test_the_restart_gain_quoted_is_the_measured_one():
    import fig06_restarts as fig
    gain = fig.restarts_png()
    assert gain > 1e5
    assert "**a million times**" in FLAT


def test_the_tie_lands_where_the_prose_says():
    interior, corner = s.tie_answers()
    assert interior == pytest.approx([0.5, 0.5], abs=1e-6)
    assert "returns the middle" in FLAT


# --- structure -------------------------------------------------------------

def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, tail = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS) == 14
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
    for index, body in enumerate(chapters[:-1]):        # the last is a summary
        assert "**In one sentence.**" in body, f"chapter {index} has no landing"


def test_every_invented_phrase_has_its_real_name():
    for standard in ("arithmetic intensity", "roofline", "first-order",
                     "saddle point", "PDHG", "PDLP", "restarting", "basic"):
        assert standard in TEXT, f"{standard} is never named"


def test_the_lesson_does_not_quote_benchmark_numbers_it_cannot_check():
    """This area moves fast and the guide deliberately stays out of it."""
    assert "none are quoted\nhere" in TEXT or "none are quoted here" in FLAT
    for vendor in ("Gurobi", "CPLEX", "Xpress", "COPT", "cuOpt"):
        assert vendor not in TEXT, f"{vendor} appears; that is a dateable claim"


def test_the_lesson_is_honest_that_there_is_no_gpu_here():
    assert "no GPU in this repository" in FLAT


# --- the sandbox pages -----------------------------------------------------

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


def test_every_sandbox_is_linked_or_deliberately_not():
    """These two are reachable from the sandbox index rather than the prose,
    because both chapters they belong to already carry a figure of the same
    thing. The index must therefore list them."""
    listing = (SANDBOX / "index.html").read_text()
    for box in build.SANDBOXES:
        assert f"{box.chapter:02d}.html" in listing


@needs_node
def test_the_page_and_the_python_agree_on_the_step_size():
    got = _run_js("console.log(JSON.stringify({n: norm2(A)}));")
    assert got["n"] == pytest.approx(s.WORKSHOP.norm, rel=1e-9)


@needs_node
def test_the_page_converges_to_the_same_answer():
    got = _run_js("""
      const tau = 0.9 / norm2(A);
      const path = run(4000, tau, true, 0);
      const last = path[path.length - 1];
      console.log(JSON.stringify({x: last[0], y: last[1]}));
    """)
    assert got["x"] == pytest.approx(s.TRUE_PLAN.tolist(), abs=1e-8)
    assert got["y"] == pytest.approx(s.TRUE_PRICES.tolist(), abs=1e-8)


@needs_node
def test_the_page_cycles_when_the_term_is_switched_off():
    got = _run_js("""
      const tau = 0.9 / norm2(A);
      const path = run(4000, tau, false, 0).slice(-1000).map(p => value(p[0]));
      console.log(JSON.stringify({hi: Math.max(...path), lo: Math.min(...path)}));
    """)
    assert got["hi"] == pytest.approx(s.CYCLE_HIGH, rel=1e-6)
    assert got["lo"] == pytest.approx(max(s.CYCLE_LOW, 0.0), abs=1e-6)

def test_the_readme_chapter_table_matches_the_chapters():
    """The topic README is hand-written, so nothing else catches it going stale
    when a chapter is split. Every chapter must be listed, once, in build order.

    The links point at the published page rather than at chapters/, because the
    chapter markdown is no longer pushed to GitHub; a relative link would 404
    for every chapter whose folder holds no image and is therefore untracked."""
    readme = (ROOT / "README.md").read_text()
    linked = re.findall(r"\]\(https://[^)]*/#ch(\d+)\)", readme)
    assert linked == [str(c.number) for c in build.CHAPTERS], \
        "run the chapter table in README.md past build.CHAPTERS again"
    for chapter in build.CHAPTERS:
        assert (ROOT / "chapters" / chapter.folder).is_dir(), chapter.folder
