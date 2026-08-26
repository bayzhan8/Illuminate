"""Consistency checks: lesson.md against the code, and the generated files
against their generator.

Run `python build.py all` before treating any failure here as real.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from solvers import library as L
from solvers.presolve import postsolve, presolve
from solvers.solve import solve_mip

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
# phrases are checked against a whitespace-flattened copy, so re-wrapping a
# paragraph never breaks a test about its content
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

def test_the_shape_of_the_model_is_the_shape_the_prose_quotes():
    p = L.SMALL_PRESOLVED
    assert p.before == (20, 21, 42)
    assert p.after == (7, 9, 14)
    assert "**20 rows, 21 columns and 42 nonzeros become 7, 9 and 14.**" in FLAT
    assert "twenty rows and twenty-one columns" in FLAT
    # the two counts the opening makes of what disappears
    assert p.before[0] - p.after[0] == 13 and p.before[1] - p.after[1] == 12
    assert "Thirteen of the twenty rows go" in FLAT
    assert "Twelve of the twenty-one columns go" in FLAT
    # "two thirds of the model is gone" is about the nonzeros, and is exact
    assert p.after[2] * 3 == p.before[2]
    assert "Two thirds of the model is deleted" in FLAT


def test_the_round_counts_are_the_computed_ones():
    """The count is the depth of the cascade, so every reduction has to get a
    look each round. An `any(...)` over a generator would short-circuit and
    inflate this number into an artefact of the ORDER list."""
    assert L.SMALL_PRESOLVED.rounds == 3
    assert L.BIG_PRESOLVED.rounds == 6
    assert L.BIG_PRESOLVED.rounds > L.SMALL_PRESOLVED.rounds
    assert "**3 rounds**" in FLAT and "**6**" in FLAT
    assert "three rounds deep" in FLAT


def test_the_answer_and_the_two_bounds_match_the_code():
    assert L.SMALL_ANSWER.value == 290
    assert L.SMALL_RELAXATION == 248
    assert L.SMALL_REDUCED_RELAXATION == 263
    assert "**$290**" in FLAT and "**$248**" in FLAT and "**$263**" in FLAT
    gap = L.SMALL_ANSWER.value - L.SMALL_RELAXATION
    closed = L.SMALL_REDUCED_RELAXATION - L.SMALL_RELAXATION
    assert (closed, gap) == (15, 42)
    assert f"**${closed} of a ${gap} gap closed**" in FLAT


def test_the_node_counts_are_the_computed_ones():
    assert L.SMALL_ANSWER.nodes == 9
    assert L.SMALL_REDUCED_ANSWER.nodes == 5
    assert "**9 nodes**" in FLAT and "**5**" in FLAT


def test_the_forced_setup_chain_is_arithmetic_the_reader_can_check():
    """Chapter 4 walks 25/100 = 0.25 and rounds it up. All three must be real."""
    demand = L.DEMAND[("B", 1)]
    assert (demand, L.BIG_M) == (25, 100)
    assert "`openB1 ≥ makeB1 / 100 ≥ 25 / 100 = 0.25`" in FLAT
    j = [c.name for c in L.SMALL.cols].index("openB1")
    assert L.SMALL_PRESOLVED.fixed[j] == 1
    # and it really is round 9, as the prose says
    forced = [r for r in L.SMALL_PRESOLVED.log
              if r.target == "openB1" and r.kind == "tightened bound"]
    assert forced and forced[0].round == 2
    fixed = [r for r in L.SMALL_PRESOLVED.log
             if r.target == "openB1" and r.kind == "fixed column"]
    assert fixed and fixed[0].round == 3
    assert "happens in round 3" in FLAT


def test_the_model_description_matches_the_instance():
    assert L.DEMAND[("A", 2)] == 40 and L.DEMAND[("A", 1)] == 0
    assert L.DEMAND[("B", 1)] == L.DEMAND[("B", 2)] == 25
    assert all(L.DEMAND[("C", t)] == 0 for t in L.PERIODS)
    assert L.CAPACITY[1] == L.CAPACITY[2] == 100
    assert "40 units of A in period 2 and nothing in period 1, 25 units of B in" in FLAT
    assert "**nothing at all for product C**" in FLAT
    assert "`makeA1 + makeB1 + makeC1 ≤ 100`" in FLAT
    assert "`makeA2 − 100 × openA2 ≤ 0`" in FLAT


def test_the_reductions_the_chapter_names_all_actually_fire():
    kinds = L.SMALL_PRESOLVED.counts()
    assert set(kinds) == {"dropped row", "fixed column", "tightened bound"}
    assert kinds["dropped row"] == 13
    assert kinds["fixed column"] == 12
    # six opening/closing stock rows go first, as chapter 2 claims
    stock_rows = {"startA", "endA", "startB", "endB", "startC", "endC"}
    singletons = [r for r in L.SMALL_PRESOLVED.log
                  if r.kind == "dropped row" and r.target in stock_rows]
    assert len(singletons) == 6
    assert all(r.round == 1 for r in singletons)
    assert "Six rows go" in FLAT
    assert "Six columns go" in FLAT


def test_presolve_really_does_preserve_the_answer():
    """The claim the whole guide rests on, re-checked here rather than assumed."""
    reduced = solve_mip(L.SMALL_REDUCED)
    x = postsolve(L.SMALL_PRESOLVED, reduced.x)
    assert L.SMALL.violations(x) == []
    assert L.SMALL.objective(x) == L.SMALL_ANSWER.value
    assert "an answer to the small model can be turned back into" in FLAT


def test_the_fuzz_count_quoted_in_the_tail_is_the_one_that_runs():
    source = (ROOT / "tests" / "test_solvers.py").read_text()
    block = source[:source.index("def test_presolve_agrees_with_enumerating")]
    seeds = int(re.findall(r'parametrize\("seed", range\((\d+)\)\)', block)[-1])
    assert seeds >= 400
    assert "four hundred random\ninstances" in TEXT or "four hundred random" in FLAT


# --- the generated files ---------------------------------------------------

def test_chapter_files_match_what_build_would_write_today():
    _, chapters, _ = build.split_lesson(build.TOPIC)
    for index, body in enumerate(chapters):
        chapter = build.CHAPTERS[index]
        on_disk = (ROOT / "chapters" / chapter.folder / "README.md")
        assert on_disk.exists(), f"{chapter.folder} has no README"
        assert on_disk.read_text() == build.chapter_markdown(build.TOPIC, index, body)


def test_every_chapter_in_build_has_a_heading_in_the_lesson():
    headings = re.findall(r"^## (\d+) · (.+)$", TEXT, flags=re.M)
    assert len(headings) == len(build.CHAPTERS)
    for (number, title), chapter in zip(headings, build.CHAPTERS):
        assert int(number) == chapter.number
        assert title.strip() == chapter.title


def test_each_chapter_ends_on_its_one_sentence_summary():
    _, chapters, _ = build.split_lesson(build.TOPIC)
    for index, body in enumerate(chapters):
        assert "> **In one sentence.**" in body, f"chapter {index} has no summary"

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
