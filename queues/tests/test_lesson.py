"""Consistency checks: lesson.md against queues, and generated files against
their generator.

Run `python build.py all` before treating any failure here as real.
"""

import json
import re
import shutil
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

from queues import desk as d

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
# phrases are checked against a whitespace-flattened copy, so that
# re-wrapping a paragraph never breaks a test about its content
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

sys.path.insert(0, str(ROOT))
import build  # noqa: E402

SANDBOX = ROOT / "sandbox"
NODE = shutil.which("node") or shutil.which("nodejs")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


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

def test_the_desk_is_the_desk_the_prose_describes():
    assert d.SERVICE_RATE == 10
    assert d.MEAN_SERVICE * 60 == 6           # six minutes
    assert "**six minutes**" in FLAT
    assert float(d.BUSY.load) == 0.9


def test_the_blow_up_table_matches_the_code():
    rows = [(F(5), "50%", "1", "**6 min**"),
            (F(8), "80%", "4", "24 min"),
            (F(9), "90%", "9", "**54 min**"),
            (F(19, 2), "95%", "19", "114 min"),
            (F(99, 10), "99%", "99", "**594 min**")]
    for rate, busy, present, wait in rows:
        q = d.DESKS[rate]
        assert f"{float(q.load) * 100:.0f}%" == busy
        assert d.number(q.number_in_system) == present
        assert d.minutes(q.time_waiting) == wait.replace("**", "")
        assert f"| {busy} | {present} | {wait} |" in FLAT


def test_the_three_step_ups_in_the_prose_are_the_real_ratios():
    quiet, busy = d.DESKS[F(5)].time_waiting, d.DESKS[F(9)].time_waiting
    assert busy / quiet == 9                       # "nine times"
    assert "**nine times**" in FLAT
    near, nearer = d.DESKS[F(9)].time_waiting, d.DESKS[F(19, 2)].time_waiting
    assert nearer / near > 2 and "**doubled**" in FLAT
    last = d.DESKS[F(99, 10)].time_waiting
    assert round(float(last / nearer)) == 5 and "**five times**" in FLAT


def test_the_percentage_increases_between_rows_are_right():
    """The prose quotes how much more work each step up is."""
    from fractions import Fraction as F
    def more(a, b):
        return float((b - a) / a * 100)
    assert f"{more(F(9), F(19, 2)):.1f}" == "5.6"
    assert f"{more(F(19, 2), F(99, 10)):.1f}" == "4.2"
    assert f"{more(F(5), F(9)):.0f}" == "80"
    assert "added 80% more work" in FLAT
    assert "added 5.6% more work" in FLAT
    assert "added 4.2% more work" in FLAT


def test_constant_service_halves_it_and_the_prose_says_the_number():
    assert d.STEADY_BUSY * 2 == d.BUSY.time_waiting
    assert d.minutes(d.STEADY_BUSY) == "27 min"
    assert "**27 minutes**. Exactly half." in FLAT


def test_the_variability_ladder_matches_the_code():
    waits = [d.minutes(w) for _, w, _ in d.LADDER]
    assert waits == ["27 min", "40.5 min", "54 min", "135 min", "702 min"]
    for shown in ("**27 min**", "40.5 min", "**54 min**", "135 min", "**702 min**"):
        assert f"| {shown} |" in FLAT


def test_the_spread_factor_quoted_is_the_computed_one():
    smallest, largest = d.LADDER[0][1], d.LADDER[-1][1]
    assert round(float(largest / smallest)) == 26
    assert "twenty-six" in FLAT


def test_the_pooling_numbers_match():
    (_, apart_quiet, pooled_quiet), (_, apart_busy, pooled_busy) = d.POOLING
    assert d.minutes(apart_busy) == "54 min"
    assert f"{float(pooled_busy) * 60:.1f}" == "25.6"
    assert "**54 minutes** in separate lines, **25.6 minutes** in one line" in FLAT
    assert f"{float(apart_quiet) * 60:.1f}" == "4.9"
    assert f"{float(pooled_quiet) * 60:.1f}" == "1.5"
    assert "**4.9 minutes** against **1.5 minutes**" in FLAT
    assert float(apart_quiet / pooled_quiet) > 3


def test_the_pooling_counterexample_matches():
    assert f"{float(d.DEDICATED):.2f}" == "3.64"
    assert f"{float(d.COMBINED):.2f}" == "5.50"
    assert "| **3.64 hours** |" in FLAT and "| **5.50 hours** |" in FLAT
    assert round(float(d.COMBINED / d.DEDICATED), 1) == 1.5
    assert "**1.5 times worse**" in FLAT


def test_the_two_counts_figure_total_is_the_one_quoted():
    import fig02_draw_a_box as fig
    assert sum(fig.STAYS) == pytest.approx(11.6)
    assert len(fig.ARRIVALS) == 8
    assert "**11.60 person-hours** for the eight customers" in FLAT


def test_the_coverage_numbers_are_the_measured_ones():
    """Chapter 7 quotes what the figure actually computed. Re-run it."""
    import fig07_measuring as fig
    naive, batched, _, _, _ = fig.coverage_study()
    assert naive < 15 and batched > 90
    assert f"**{naive:.0f}% of the time**" in FLAT
    assert f"**{batched:.0f}% coverage**" in FLAT


def test_the_correlation_length_claim_is_about_right():
    import numpy as np

    from queues.simulate import correlation_length, lindley
    rng = np.random.default_rng(31)
    length = correlation_length(lindley(9.0, 10.0, 600_000, rng))
    assert 250 < length < 600, length
    assert "four hundred consecutive customers" in FLAT


def test_the_kanban_and_inventory_arithmetic_in_the_prose():
    assert 6 / 12 == 0.5 and 18 / 12 == 1.5          # half a week -> a week and a half
    assert "6/12 = half a week" in FLAT
    assert "18/12, a week and a half" in FLAT
    assert 9_000_000 / 100_000 == 90                 # days of supply
    assert "90 days of supply" in FLAT


# --- structure -------------------------------------------------------------

def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, _ = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS) == 14
    assert front.startswith(build.TOPIC.heading)


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


def test_every_invented_phrase_has_its_real_name():
    for standard in ("Little's law", "utilisation", "M/M/1", "M/D/1",
                     "Pollaczek–Khinchine", "Kingman", "Erlang C",
                     "batch means", "congestion multiplier"):
        assert standard in TEXT, f"{standard} is never named"


def test_the_lesson_states_what_the_law_does_not_need():
    for absence in ("No distributional assumptions", "No independence",
                    "No queue discipline", "No steady state"):
        assert absence in TEXT


def test_the_lesson_does_not_claim_the_figure_needs_first_come_first_served():
    """The picture serves in order so the tiling is visible. The theorem does
    not, and conflating the two would be the easiest error to make here."""
    assert "the identity does not care" in FLAT


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


def test_every_sandbox_is_linked_from_its_chapter():
    for box in build.SANDBOXES:
        assert f"sandbox/{box.chapter:02d}.html" in TEXT


@needs_node
def test_the_pages_compute_the_same_waits_the_python_does():
    rates = [float(r) for r in (F(5), F(8), F(9), F(19, 2), F(99, 10))]
    got = _run_js(f"""
      const rates = {json.dumps(rates)};
      console.log(JSON.stringify(rates.map(r => waitRandom(r))));
    """)
    for rate, js in zip((F(5), F(8), F(9), F(19, 2), F(99, 10)), got):
        assert js == pytest.approx(float(d.DESKS[rate].time_waiting), rel=1e-12)


@needs_node
def test_the_pages_agree_about_the_variability_dial():
    cases = [(9.0, float(cv2)) for cv2, _, _ in d.LADDER]
    got = _run_js(f"""
      const cases = {json.dumps(cases)};
      console.log(JSON.stringify(cases.map(([r, c]) => waitWithSpread(r, c))));
    """)
    for (_, wait, _), js in zip(d.LADDER, got):
        assert js == pytest.approx(float(wait), rel=1e-12)


@needs_node
def test_the_pages_agree_about_pooling():
    from queues.formulas import MMC
    cases = [(2, 18.0), (3, 27.0), (5, 45.0), (10, 90.0)]
    got = _run_js(f"""
      const cases = {json.dumps(cases)};
      console.log(JSON.stringify(cases.map(([c, r]) => waitPooled(r, c))));
    """)
    for (servers, rate), js in zip(cases, got):
        here = MMC.build(F(rate).limit_denominator(100), 10, servers).time_waiting
        assert js == pytest.approx(float(here), rel=1e-9)


def _run_js(snippet: str):
    result = subprocess.run([NODE, "-e", build.MATHS + snippet],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_the_two_job_example_in_chapter_five_is_the_row_it_claims_to_be():
    """Chapter 5 explains the c-squared ladder with a concrete mix: nine jobs
    in ten take 2 minutes and the tenth takes 42. That mix has to be exactly
    the 135-minute row of the table, or the explanation explains a different
    number from the one printed."""
    from queues import formulas as ff

    short, long_, mean = F(2), F(42), F(6)
    assert (9 * short + long_) / 10 == mean                    # six minutes
    second = (9 * short ** 2 + long_ ** 2) / 10
    assert second == 180
    assert second / mean ** 2 - 1 == 4                         # c-squared of 4

    # the clock-weighted picture the prose draws: busy time inside the long job
    assert long_ / (9 * short + long_) == F(7, 10)
    clock_weighted = (9 * short / 60) * short + (long_ / 60) * long_
    assert clock_weighted == 30                                # minutes
    assert clock_weighted / 2 == 15                            # leftover

    # and the leftovers, multiplied by the congestion factor, are the ladder
    congestion = d.BUSY.load / (1 - d.BUSY.load)
    assert congestion == 9
    assert [congestion * x for x in (F(3), F(6), F(15))] == [27, 54, 135]

    # 135 is what the formula returns for this mix, in minutes
    wait = ff.wait_from_variability(F(9), F(1, 10), F(4))
    assert wait * 60 == 135
    assert "| some customers much longer | 135 min |" in FLAT


def test_chapter_seven_quotes_the_run_length_the_figure_actually_uses():
    """The prose used to say a million waits; the coverage study runs 200,000.
    Read the figure's own constants rather than trusting the sentence."""
    script = (ROOT / "figures" / "fig07_measuring.py").read_text()
    run_length = int(re.search(r"RUN_LENGTH = ([\d_]+)", script)[1].replace("_", ""))
    trials = int(re.search(r"TRIALS = ([\d_]+)", script)[1])
    assert (run_length, trials) == (200_000, 300)
    assert "two hundred thousand measured waits" in FLAT
    assert "three hundred times" in FLAT
    # and the deflation the prose does with it: 200,000 / 400 correlated waits
    assert run_length // 400 == 500
    assert "worth about five hundred" in FLAT

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
