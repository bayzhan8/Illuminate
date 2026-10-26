"""The prose against the code. Regenerate with `python build.py all` first."""

import re
import sys
from pathlib import Path

from linprog import farm as f

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

sys.path.insert(0, str(ROOT))
import build  # noqa: E402


def test_lesson_image_links_all_resolve():
    assert [s for _, s in IMAGE.findall(TEXT) if not (ROOT / s).exists()] == []


def test_no_orphan_images_under_chapters():
    used = {s for _, s in IMAGE.findall(TEXT)}
    have = {str(p.relative_to(ROOT)) for p in (ROOT / "chapters").rglob("*")
            if p.suffix in {".png", ".gif"}}
    assert sorted(have - used) == []


def test_alt_text_is_a_real_description():
    assert [s for alt, s in IMAGE.findall(TEXT) if len(alt.strip()) < 40] == []


def test_the_farm_table_matches_the_program():
    assert "| an acre of wheat | 1 unit | 1 acre | $3,000 |" in FLAT
    assert "| an acre of corn | 2 units | 1 acre | $5,000 |" in FLAT
    assert "| **the farm has** | **32 units** | **20 acres** | |" in FLAT
    assert f.USE == {"wheat": (1, 1), "corn": (2, 1)}
    assert f.STOCK == (32, 20) and f.PROFIT == (3, 5)


def test_the_too_much_water_example_adds_up():
    p = (6, 14)
    assert f.FARM.used(1, p) == 20
    assert f.FARM.used(0, p) == 34 and -f.FARM.slack(0, p) == 2
    assert "6 + 28 = 34 units of water, two more than the farm has" in FLAT


def test_the_greedy_numbers_are_the_computed_ones():
    assert f"gone after {f.acres(f.ALL_CORN_ACRES)} acres" in FLAT
    assert f"earns {f.money(f.ALL_CORN_PROFIT)} and leaves {f.ALL_CORN_IDLE_LAND} acres" in FLAT


def test_the_best_plan_is_quoted_as_computed():
    assert f.money(f.BEST_PROFIT) == "$84,000"
    assert f"{f.BEST[0]} acres of wheat and {f.BEST[1]} of corn, worth $84,000" in FLAT


def test_the_corner_table_is_every_corner_and_its_value():
    rows = re.findall(r"\| \**[a-z ]+\** \| \**(\d+)\** \| \**(\d+)\** \| \**(\$[\d,]+)\** \|", TEXT)
    quoted = {(int(w), int(c)): v for w, c, v in rows}
    assert quoted == {tuple(int(v) for v in p): f.money(f.FARM.value(p)) for p in f.CORNERS}


def test_the_hero_alt_text_describes_the_walk_drawn():
    stops = [f.money(f.FARM.value(p)) for p in f.WALK.corners[1:]]
    alt = IMAGE.findall(TEXT)[0][0]
    assert all(s in alt for s in stops)


def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, _ = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS)
    assert front.startswith(build.TOPIC.heading)


def test_the_generated_chapter_files_are_up_to_date():
    _, chapters, _ = build.split_lesson(build.TOPIC)
    stale = []
    for index, body in enumerate(chapters):
        path = ROOT / "chapters" / build.CHAPTERS[index].folder / "README.md"
        if not path.exists() or path.read_text() != build.chapter_markdown(build.TOPIC, index, body):
            stale.append(path.name)
    assert stale == [], "run: python build.py chapters"


def test_every_invented_phrase_has_its_real_name():
    glossary = TEXT.split("## Glossary")[1]
    for phrase in ("plan", "region of possible plans", "wall", "line of equal profit", "corner"):
        assert f"| {phrase}" in glossary or f"| the {phrase}" in glossary


def test_em_dash_density_is_low():
    words = len(TEXT.split())
    assert TEXT.count("—") * 1000 / words < 3


def test_the_shadow_lengths_are_rounded_from_the_exact_values():
    import math
    for i, root in ((0, "√5"), (1, "√2")):
        a, b = f.FARM.A[i], f.FARM.b[i]
        size = math.sqrt(a[0] ** 2 + a[1] ** 2)
        assert f"{b} ÷ {root} ≈ {float(b) / size:.1f}" in FLAT


def test_the_arrow_decomposition_is_the_prices():
    y, (w, l) = f.PRICES, f.FARM.A
    assert (f"c = {y[0]} × ({w[0]}, {w[1]}) + {y[1]} × ({l[0]}, {l[1]})") in FLAT
