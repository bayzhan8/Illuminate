"""Consistency checks: lesson.md against bandp, and the generated files
against their generator.

Run `python build.py all` before treating any failure here as real.
"""

import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from bandp import mill as m

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
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


# --- the numbers in the prose ----------------------------------------------

def test_the_order_in_the_table_is_the_order_in_the_code():
    assert m.BOARDS.width == 25
    assert m.BOARDS.widths == (4, 9, 10)
    assert m.BOARDS.demands == (3, 6, 7)
    assert "| short pieces | 4 ft | 3 |" in TEXT
    assert "| medium pieces | 9 ft | 6 |" in TEXT
    assert "| long pieces | 10 ft | 7 |" in TEXT


def test_the_naive_bound_arithmetic_in_the_prose_is_right():
    assert m.NAIVE_BOUND == Fraction(136, 25)
    assert "(3×4 + 6×9 + 7×10) ÷ 25 = 136 ÷ 25 = **5.44 boards**" in TEXT
    assert m.decimal(m.NAIVE_BOUND, 2) == "5.44"


def test_the_two_bounds_table_matches_the_code():
    assert f"| the obvious model, relaxed | {m.decimal(m.NAIVE_BOUND, 2)} boards | " \
           f"{math.ceil(m.NAIVE_BOUND)} | {m.ANSWER} |" in TEXT
    assert m.decimal(m.DW_BOUND, 1) == "6.5"
    assert "6.5 boards" in TEXT


def test_the_number_of_patterns_drawn_matches_the_prose():
    assert len(m.PATTERNS) == 6
    assert "there are only\nsix worth using" in TEXT or "only\nsix" in TEXT


def test_the_first_round_prices_in_the_table_are_the_computed_ones():
    first = m.ROUNDS[0]
    assert [str(d) for d in first.duals] == ["1/6", "1/2", "1/2"]
    for width, price in zip(m.BOARDS.widths, first.duals):
        assert f"| {width} ft | {price} |" in TEXT


def test_the_first_pattern_the_knapsack_asks_for_is_the_one_quoted():
    first = m.ROUNDS[0]
    assert m.BOARDS.describe(first.best_pattern) == "4×4 + 1×9"
    assert first.best_value == Fraction(7, 6)
    assert "**four 4-foot pieces and one\n9-foot piece**" in TEXT
    assert "4×(1/6) + 1×(1/2) = **7/6**" in TEXT


def test_the_sequence_of_master_values_is_the_one_the_prose_narrates():
    values = [m.decimal(r.value, 3) for r in m.ROUNDS]
    assert values[0] == "7.000" and values[-1] == "6.500"
    assert "**7 boards**, then 6.875, then 6.5" in TEXT
    assert m.decimal(m.ROUNDS[1].value, 3) == "6.875"


def test_the_number_of_patterns_added_matches_the_prose():
    added = sum(1 for r in m.ROUNDS if r.added)
    assert added == 3
    assert "Three patterns\nwere added" in TEXT or "Three patterns" in TEXT


def test_the_mill_count_in_the_prose_is_the_computed_one():
    assert m.thousands(m.MILL_PATTERNS) == "3,972,952,644,549"
    assert "**3,972,952,644,549 patterns.**" in TEXT


def test_the_bigger_order_numbers_match():
    assert m.SCALE.width == 55 and len(m.SCALE.widths) == 4
    assert (m.SCALE_TOUCHED, len(m.SCALE_PATTERNS)) == (6, 30)
    assert "thirty usable patterns, and the loop settles after touching six" in TEXT
    assert f"Twenty-four patterns were never written down" in TEXT
    assert len(m.SCALE_PATTERNS) - m.SCALE_TOUCHED == 24


def test_the_tree_size_matches_the_figure():
    assert m.SCALE_SEARCH.explored == 11
    assert "eleven boxes" in TEXT


def test_the_bug_count_the_chapter_confesses_to_is_the_real_one():
    """Chapter 8 quotes how badly the first version of the solver did. If that
    claim is going to be in the prose it has to be reproducible."""
    import itertools

    from bandp.cutting import Instance
    from bandp.search import branch_and_price, integer_optimum_by_enumeration
    checked = 0
    for width in (16, 18, 20, 22, 24):
        for widths in itertools.combinations(range(5, width // 2 + 2), 3):
            for demands in [(3, 4, 5), (5, 3, 4), (2, 5, 7),
                            (4, 6, 3), (7, 4, 3), (6, 5, 4)]:
                inst = Instance(width, widths, demands)
                exact = integer_optimum_by_enumeration(inst)
                if exact is None:
                    continue
                checked += 1
                assert branch_and_price(inst).best == exact
    assert checked == 1230, checked
    assert "**476 of 1230**" in TEXT


# --- structure -------------------------------------------------------------

def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, _ = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS) == 10
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


def test_every_figure_lives_in_the_chapter_that_shows_it():
    """A figure filed under the wrong chapter still renders on the one page and
    goes missing from the chapter file, which is only visible on GitHub."""
    _, chapters, _ = build.split_lesson(build.TOPIC)
    for index, body in enumerate(chapters):
        folder = build.CHAPTERS[index].folder
        for _, src in IMAGE.findall(body):
            assert src.startswith(f"chapters/{folder}/"), \
                f"chapter {index} shows {src}, which is not in {folder}"


def test_every_invented_phrase_has_its_real_name():
    for standard in ("column", "restricted master problem", "reduced cost",
                     "pricing problem", "column generation", "branch-and-price",
                     "Dantzig–Wolfe", "Benders decomposition"):
        assert standard in TEXT, f"{standard} is never named"


def test_the_lesson_credits_its_source():
    assert "Conforti, Cornuéjols and Zambelli" in TEXT


def test_the_lesson_admits_the_branching_rule_is_weak():
    assert "Ryan–Foster" in TEXT
    assert "weak" in TEXT


# --- the sandbox pages -----------------------------------------------------

def test_a_page_exists_for_every_sandbox():
    for box in build.SANDBOXES:
        assert (SANDBOX / f"{box.chapter:02d}.html").exists()
    assert (SANDBOX / "index.html").exists()


def test_the_pages_carry_their_own_logic():
    for page in SANDBOX.glob("*.html"):
        text = page.read_text()
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "cdn."):
            assert forbidden not in text, f"{page.name} reaches out via {forbidden}"
        for script in re.findall(r'<script src="([^"]+)"', text):
            assert script.startswith("../../assets/"), script


def test_every_sandbox_is_linked_from_its_chapter():
    for box in build.SANDBOXES:
        assert f"sandbox/{box.chapter:02d}.html" in TEXT


def test_the_baked_in_rounds_are_the_real_ones():
    """Sandbox 07 ships the loop's numbers rather than recomputing them, so
    they have to be checked against a live solve."""
    baked = json.loads(build.rounds_json())
    assert len(baked) == len(m.ROUNDS)
    for row, here in zip(baked, m.ROUNDS):
        assert row["held"] == len(here.patterns)
        assert row["value"] == pytest.approx(float(here.value))
        assert row["best"] == m.BOARDS.describe(here.best_pattern)
        assert row["added"] == here.added
    page = (SANDBOX / "07.html").read_text()
    assert "ROUNDS_JSON" not in page, "the rounds were never substituted in"
    assert '"held": 3' in page or '"held":3' in page


@needs_node
def test_the_pages_build_the_same_pattern_the_python_does():
    """The knapsack is written twice, once in each language."""
    cases = [[float(d) for d in r.duals] for r in m.ROUNDS]
    result = subprocess.run(
        [NODE, "-e", build.MATHS + f"""
          const cases = {json.dumps(cases)};
          console.log(JSON.stringify(cases.map(p => {{
            const k = knapsack(p, BOARD, WIDTHS);
            return {{value: k.value, pattern: k.pattern}};
          }})));
        """], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    for js, here in zip(json.loads(result.stdout), m.ROUNDS):
        assert js["value"] == pytest.approx(float(here.best_value), abs=1e-9)
        assert js["pattern"] == list(here.best_pattern)


@needs_node
def test_the_pages_list_the_same_patterns_the_python_does():
    result = subprocess.run(
        [NODE, "-e", build.MATHS +
         "console.log(JSON.stringify(allPatterns(BOARD, WIDTHS)));"],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert sorted(json.loads(result.stdout)) == sorted(list(p) for p in m.PATTERNS)


def test_the_derivation_of_six_and_a_half_in_chapter_three():
    """Chapter 3 shows where 6.5 comes from instead of asserting it. Both
    halves of that argument are checked here: the mix that reaches 13/2, and
    the counting argument that nothing beats it."""
    flat = " ".join(TEXT.split())
    whole, half = (1, 1, 1), (1, 0, 2)        # a 4/9/10 board, and a 4/10/10
    assert whole in m.PATTERNS and half in m.PATTERNS

    # the offcut the prose quotes for the pattern it cuts six boards with
    assert sum(n * w for n, w in zip(whole, m.BOARDS.widths)) == 23
    assert "which uses 23 of the 25 feet available" in flat

    # and the claim that only one pattern yields two 10-foot pieces
    assert [p for p in m.PATTERNS if p[2] >= 2] == [half]

    # six of the first and half of the second cover the order, for 13/2 boards
    made = [6 * a + Fraction(1, 2) * b for a, b in zip(whole, half)]
    assert made == [Fraction(13, 2), 6, 7]
    assert all(q >= d for q, d in zip(made, m.BOARDS.demands))
    assert 6 + Fraction(1, 2) == m.DW_BOUND

    # the lower bound: three pieces of 9ft or more never fit on a 25ft board,
    # so 13 such pieces need at least 13/2 boards, fractional cutting included
    longs = [i for i, w in enumerate(m.BOARDS.widths) if w >= 9]
    assert 3 * min(m.BOARDS.widths[i] for i in longs) > m.BOARDS.width
    assert max(sum(p[i] for i in longs) for p in m.PATTERNS) == 2
    assert sum(m.BOARDS.demands[i] for i in longs) == 13
    assert Fraction(13, 2) == m.DW_BOUND
