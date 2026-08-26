"""Consistency checks between lesson.md and the code. Not mathematics.

A failure here means the page and the program have diverged. Regenerate with
`python build.py all` before debugging anything; most failures in this file
are a stale generated artefact rather than a real disagreement.

The reason this file exists separately from test_lp.py: nothing it checks is
visible by reading the page. A figure reference that no longer resolves, or a
quoted number the solver stopped producing, leaves prose that still scans
perfectly.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from lpduality import workshop as w

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lesson.md"
TEXT = LESSON.read_text()
# phrases are checked against a whitespace-flattened copy, so that
# re-wrapping a paragraph never breaks a test about its content
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

sys.path.insert(0, str(ROOT))
import build  # noqa: E402


# --- figures ---------------------------------------------------------------

def test_lesson_image_links_all_resolve():
    missing = [src for _, src in IMAGE.findall(TEXT) if not (ROOT / src).exists()]
    assert missing == []


def test_no_orphan_images_under_chapters():
    """An unreferenced image means `make figures` is rebuilding dead weight."""
    used = {src for _, src in IMAGE.findall(TEXT)}
    have = {str(p.relative_to(ROOT)) for p in (ROOT / "chapters").rglob("*")
            if p.suffix in {".png", ".gif"}}
    assert sorted(have - used) == []


def test_alt_text_is_a_real_description():
    thin = [src for alt, src in IMAGE.findall(TEXT) if len(alt.strip()) < 40]
    assert thin == []


# --- the numbers in the prose ----------------------------------------------

def test_the_headline_numbers_are_the_computed_ones():
    assert w.money(w.BEST_PROFIT) == "$350"
    assert f"{w.PLAN[0]} tables and {w.PLAN[1]} chairs" == "9 tables and 4 chairs"
    assert "9 tables and 4 chairs" in FLAT
    assert "$350" in FLAT


def test_the_prices_in_the_prose_are_the_computed_ones():
    plank, hour, saw = (w.money(p) for p in w.PRICES)
    assert (plank, hour, saw) == ("$6.25", "$2.50", "$0")
    assert "$6.25 a plank" in FLAT
    assert "$2.50 an hour" in FLAT


def test_the_stock_table_matches_the_program():
    for resource in w.RESOURCES:
        assert resource in FLAT
    row = "| **in stock** | **44** | **30** | **32** | |"
    assert row in FLAT
    assert [int(v) for v in w.PRIMAL.b] == [44, 30, 32]


def test_the_recipes_in_the_table_match_the_program():
    assert w.RECIPE["tables"] == (4, 2, 3)
    assert w.RECIPE["chairs"] == (2, 3, 1)
    assert "| a table | 4 | 2 | 3 | $30 |" in FLAT
    assert "| a chair | 2 | 3 | 1 | $20 |" in FLAT


def test_the_spare_saw_time_the_prose_claims_is_the_real_amount():
    spare = w.PRIMAL.slack(w.SAW, w.PLAN)
    assert spare == 1
    assert "31 of the 32 hours of saw time" in FLAT


def test_the_ingredient_arithmetic_in_chapter_three():
    """$7 a plank and $3 an hour price a table at $34 and a chair at $23."""
    prices = (7, 3, 0)
    table = sum(p * w.PRIMAL.A[i][0] for i, p in enumerate(prices))
    chair = sum(p * w.PRIMAL.A[i][1] for i, p in enumerate(prices))
    assert (table, chair) == (34, 23)
    assert table > w.PRIMAL.c[0] and chair > w.PRIMAL.c[1]   # both covered
    assert "4×7 + 2×3 = $34" in FLAT and "2×7 + 3×3 = $23" in FLAT


def test_the_weak_duality_worked_example_adds_up():
    """Chapter 4 quotes three numbers; all three come from the program."""
    plan, prices = (10, 2), (7, 3, 0)
    earns = w.PRIMAL.objective(plan)
    used = sum(p * w.PRIMAL.row_value(i, plan) for i, p in enumerate(prices))
    whole = sum(p * b for p, b in zip(prices, w.PRIMAL.b))
    assert (earns, used, whole) == (340, 386, 398)
    assert earns <= used <= whole
    for number in ("$340", "$386", "$398"):
        assert number in FLAT


def test_the_price_range_in_the_prose_is_the_computed_one():
    from fractions import Fraction
    assert (w.WOOD_FROM, w.WOOD_TO) == (Fraction(20), Fraction(316, 7))
    assert "20 to 45 ⅐" in FLAT
    headroom = w.WOOD_TO - w.PRIMAL.b[w.WOOD]
    assert headroom == Fraction(8, 7)
    assert "1 ⅐ planks away" in FLAT


def test_the_three_slopes_quoted_in_the_table_are_the_computed_ones():
    """The chapter 8 table shows a column of figures, so it keeps its cents."""
    slopes = [w.money(s.slope, cents=True) for s in w.WOOD_CURVE]
    assert slopes == ["$10.00", "$6.25", "$0.00"]
    plain = TEXT.replace("**", "")   # the middle cell is bold, being the live one
    for cell in slopes:
        assert f"| {cell} |" in plain


def test_the_impossible_order_is_the_size_the_prose_says():
    assert "order arrives for 12 tables" in FLAT
    assert int(w.PRIMAL.b[w.WOOD] / w.RECIPE["tables"][0]) == 11
    assert "make eleven tables" in FLAT


def test_the_random_sample_size_matches_the_figure():
    import inspect

    import fig05_they_always_meet as fig
    default = inspect.signature(fig.always_png).parameters["count"].default
    assert default == 320
    assert f"{default} more" in FLAT
    assert f"across all {default}" in FLAT


# --- structure -------------------------------------------------------------

def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, tail = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS) == 12
    assert front.startswith(build.TOPIC.heading)
    assert tail


def test_the_generated_chapter_files_are_up_to_date():
    """These files are generated. A hand edit is a bug, not a change."""
    _, chapters, _ = build.split_lesson(build.TOPIC)
    stale = []
    for index, body in enumerate(chapters):
        folder = build.CHAPTERS[index].folder
        path = ROOT / "chapters" / folder / "README.md"
        expected = build.chapter_markdown(build.TOPIC, index, body)
        if not path.exists() or path.read_text() != expected:
            stale.append(folder)
    assert stale == [], "run: python build.py chapters"


def test_every_chapter_folder_has_its_file():
    for chapter in build.CHAPTERS:
        assert (ROOT / "chapters" / chapter.folder / "README.md").exists()


def test_every_invented_phrase_has_its_real_name():
    """The glossary is what lets a reader leave and read anything else."""
    for standard in ("primal", "dual", "weak duality", "strong duality",
                     "complementary slackness", "shadow price",
                     "Farkas certificate", "unbounded", "degeneracy"):
        assert standard in TEXT, f"{standard} is never named"


def test_the_lesson_does_not_oversell_the_evidence():
    """Chapter 5 shows 320 examples of a theorem. It has to say so, and it has
    to point at where the proof actually turns up."""
    assert "320 pieces of evidence, not a proof" in FLAT
    assert "chapter 10 shows its shape" in FLAT

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


def test_the_far_corner_the_prose_describes_is_the_real_one():
    """An earlier draft said "build 11 tables and every plank is gone". Eleven
    tables needs 33 saw-hours against 32, so it is not even feasible, and the
    rightmost corner is set by the saw with planks to spare."""
    from fractions import Fraction
    assert 11 * w.RECIPE["tables"][2] > w.PRIMAL.b[w.SAW]        # 33 > 32
    corner = Fraction(w.PRIMAL.b[w.SAW], w.RECIPE["tables"][2])  # 32/3
    assert corner == Fraction(32, 3)
    spare = w.PRIMAL.b[w.WOOD] - corner * w.RECIPE["tables"][0]
    assert spare == Fraction(4, 3)
    assert "10⅔ of them" in FLAT
    assert "a plank and a third to spare" in FLAT
    assert "but the saw" in FLAT


def test_the_unbounded_pairing_is_stated_as_one_direction_only():
    """Primal unbounded => dual infeasible. The converse needs feasibility, and
    chapter 10's own example has both sides empty."""
    assert "if the plan side runs away, the price side has nothing whatever to offer" in FLAT
    assert "Both sides can be empty at once" in FLAT
