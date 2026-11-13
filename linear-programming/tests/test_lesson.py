"""The prose against the code. Regenerate with `python build.py all` first."""

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from linprog import mill as f

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[(.*?)\]\(([^)]+)\)")
CHAPTER_REFERENCE = re.compile(
    r"\bchapters?\s+(\d+)(?:\s+(to|and)\s+(\d+)|\s*([–—-])\s*(\d+))?",
    re.IGNORECASE,
)
ROADMAP_CHAPTER = re.compile(
    r"\*\*chapters?\s+(\d+)(?:\s+(to|and)\s+(\d+)|\s*([–—-])\s*(\d+))?\*\*",
    re.IGNORECASE,
)
SIBLING_LINK = re.compile(r"\]\((\.\./[^)\s]+)\)")

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


def test_the_mill_table_matches_the_program():
    assert "| one batch of 3-ply | 1 hour | 1 hour | 3,000 roubles |" in FLAT
    assert "| one batch of 5-ply | 2 hours | 1 hour | 5,000 roubles |" in FLAT
    assert "| **the mill has** | **32 hours** | **20 hours** | |" in FLAT
    assert f.PRODUCTS == ("3-ply", "5-ply")
    assert f.RESOURCES == ("lathe", "press")
    assert f.USE == {"3-ply": (1, 1), "5-ply": (2, 1)}
    assert f.STOCK == (32, 20) and f.VALUE == (3, 5)


def test_the_over_lathe_example_adds_up():
    p = (6, 14)
    assert f.MILL.used(1, p) == 20
    assert f.MILL.used(0, p) == 34 and -f.MILL.slack(0, p) == 2
    assert "6 + 28 = 34 lathe hours, two more than the mill has" in FLAT


def test_the_greedy_numbers_are_the_computed_ones():
    assert f"gone after {f.batches(f.ALL_FIVE_BATCHES)} batches of 5-ply" in FLAT
    assert (f"worth {f.money(f.ALL_FIVE_VALUE)} and leaves "
            f"{f.ALL_FIVE_IDLE_PRESS} press hours unused") in FLAT


def test_the_best_plan_is_quoted_as_computed():
    assert f.money(f.BEST_VALUE) == "84,000 roubles"
    assert (f"{f.BEST[0]} batches of 3-ply and {f.BEST[1]} of 5-ply, "
            f"worth {f.money(f.BEST_VALUE)}") in FLAT


def test_the_corner_table_is_every_corner_and_its_value():
    rows = re.findall(r"\|\s*\**[^|]+?\**\s*\|\s*\**(\d+)\**\s*\|\s*\**(\d+)\**"
                      r"\s*\|\s*\**([\d,]+ roubles)\**\s*\|", TEXT)
    quoted = {(int(t), int(five)): value for t, five, value in rows}
    assert quoted == {tuple(int(v) for v in p): f.money(f.MILL.value(p)) for p in f.CORNERS}


def test_the_hero_alt_text_describes_the_walk_drawn():
    stops = [f.money(f.MILL.value(p)) for p in f.WALK.corners[1:]]
    alt = IMAGE.findall(TEXT)[0][0]
    assert all(s in alt for s in stops)


def test_the_lesson_splits_into_the_chapters_build_expects():
    front, chapters, _ = build.split_lesson(build.TOPIC)
    assert len(chapters) == len(build.CHAPTERS)
    assert front.startswith(build.TOPIC.heading)


def test_every_chapter_reference_names_registered_chapters():
    registered = {chapter.number for chapter in build.CHAPTERS}
    maximum = max(registered)
    references = list(CHAPTER_REFERENCE.finditer(TEXT))
    assert references
    for reference in references:
        first = int(reference.group(1))
        relation = reference.group(2)
        second = reference.group(3)
        dash_end = reference.group(5)
        if relation == "to" or dash_end is not None:
            last = int(second if relation == "to" else dash_end)
            assert first <= last, reference.group()
            cited = range(first, last + 1)
        elif relation == "and":
            cited = (first, int(second))
        else:
            cited = (first,)
        assert all(0 <= number <= maximum and number in registered
                   for number in cited), reference.group()


def test_chapter_zero_roadmap_covers_every_chapter_without_gaps():
    roadmap = TEXT.split(
        "Getting there takes a few ideas, and each chapter adds one:", 1
    )[1].split("\n\nEach idea comes", 1)[0]
    maximum = max(chapter.number for chapter in build.CHAPTERS)
    covered = []
    for reference in ROADMAP_CHAPTER.finditer(roadmap):
        first = int(reference.group(1))
        relation = reference.group(2)
        second = reference.group(3)
        dash_end = reference.group(5)
        if relation == "to" or dash_end is not None:
            last = int(second if relation == "to" else dash_end)
            covered.extend(range(first, last + 1))
        elif relation == "and":
            covered.extend((first, int(second)))
        else:
            covered.append(first)
    assert sorted(covered) == list(range(1, maximum + 1))


def test_relative_sibling_links_resolve_to_index_pages():
    links = SIBLING_LINK.findall(TEXT)
    assert links
    for link in links:
        target = (ROOT / urlsplit(link).path).resolve()
        assert target.is_dir(), link
        assert (target / "index.html").is_file(), link


def test_where_to_go_next_section_has_its_prose_and_rendered_anchors():
    start = TEXT.index("## Where to go next")
    section = " ".join(
        TEXT[start:TEXT.index("\n## Glossary", start)].split()
    )
    assert "## Where to go next" in section
    for link in (
        "[simplex against interior point](../corners-vs-centre/)",
        "[LP on a GPU](../lp-on-gpu/)",
        "[branch-and-price](../branch-and-price/)",
    ):
        assert link in section

    rendered = (ROOT / "index.html").read_text()
    assert "<h2>Where to go next</h2>" in rendered
    toc = rendered.split("</nav>", 1)[0]
    assert "Where to go next" not in toc


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
    for phrase in ("plan", "region of possible plans", "wall", "line of equal value", "corner"):
        assert f"| {phrase}" in glossary or f"| the {phrase}" in glossary


def test_em_dash_density_is_low():
    words = len(TEXT.split())
    assert TEXT.count("—") * 1000 / words < 3


def test_the_shadow_lengths_are_rounded_from_the_exact_values():
    import math
    for i, root in ((0, "√5"), (1, "√2")):
        a, b = f.MILL.A[i], f.MILL.b[i]
        size = math.sqrt(a[0] ** 2 + a[1] ** 2)
        assert f"{b} ÷ {root} ≈ {float(b) / size:.1f}" in FLAT


def test_the_arrow_decomposition_is_the_prices():
    y, (lathe, press) = f.PRICES, f.MILL.A
    assert (f"c = {y[0]} × ({lathe[0]}, {lathe[1]}) + "
            f"{y[1]} × ({press[0]}, {press[1]})") in FLAT


def test_the_dot_product_numbers_quoted_are_computed():
    import math
    a, length = [float(v) for v in f.MILL.A[0]], 14
    three_ply, along, five_ply = a[0] * length, math.hypot(*a) * length, a[1] * length
    for v in (three_ply, along, five_ply):
        assert f"{v:.1f}" in FLAT
    assert f"8 ÷ √5 ≈ {8 / math.hypot(*a):.1f}" in FLAT


def test_the_turned_arrow_gallery_is_quoted_as_computed():
    from linprog.lp import LP, vertices
    names = {(0, 16): "all 5-ply", (8, 12): "8 batches of 3-ply and 12 of 5-ply",
             (20, 0): "all 3-ply"}
    alt = [a for a, s in IMAGE.findall(TEXT) if s.endswith("turns.png")][0]
    for c in ((1, 3), (3, 5), (1, 1), (3, 1)):
        lp = LP.build(c=c, A=[list(r) for r in f.MILL.A], b=list(f.MILL.b))
        top = max(lp.value(p) for p in vertices(lp))
        best = [tuple(int(v) for v in p) for p in vertices(lp) if lp.value(p) == top]
        assert f"c = ({c[0]}, {c[1]})" in alt and f.money(top) in alt
        if len(best) == 1:
            assert f"c = ({c[0]}, {c[1]}): {'the best plan is ' if c == (1, 3) else ''}{names[best[0]]}" in alt
