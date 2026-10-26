"""The sandbox JavaScript against src/linprog. Needs node for the comparisons."""

import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from linprog import mill as f
from linprog.lp import best_by_enumeration, vertices

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

NODE = shutil.which("node") or shutil.which("nodejs")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_js(snippet):
    r = subprocess.run([NODE, "-e", build.MATHS + snippet], capture_output=True,
                       text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_a_page_exists_for_every_sandbox_and_is_linked():
    lesson = (ROOT / "lesson.md").read_text()
    for box in build.SANDBOXES:
        assert (ROOT / "sandbox" / f"{box.chapter:02d}.html").exists()
        assert f"sandbox/{box.chapter:02d}.html" in lesson


def test_the_pages_carry_their_own_logic():
    for page in (ROOT / "sandbox").glob("*.html"):
        text = page.read_text()
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "cdn."):
            assert forbidden not in text
        assert all(s.startswith("../../assets/")
                   for s in re.findall(r'<script src="([^"]+)"', text))


@needs_node
def test_the_page_has_the_same_mill():
    got = run_js("console.log(JSON.stringify([USE, STOCK, VALUE]))")
    assert got == [[list(r) for r in f.MILL.A], list(f.STOCK), list(f.VALUE)]


@needs_node
def test_the_page_finds_the_same_best_corners_at_every_slider_setting():
    steps = [0.5 + 0.25 * k for k in range(31)]          # the sliders' range
    cases = [[a, b] for a in steps for b in steps]
    got = run_js(f"""
      const cases = {json.dumps(cases)};
      console.log(JSON.stringify(cases.map(c => bestCorners(c, USE, STOCK))));
    """)
    for c, js in zip(cases, got):
        lp = f.MILL.with_c(c)
        top = best_by_enumeration(lp)[1]
        tied = sorted(tuple(float(v) for v in p) for p in vertices(lp) if lp.value(p) == top)
        assert js["value"] == pytest.approx(float(top))
        assert sorted(tuple(p) for p in js["at"]) == tied, c


@needs_node
def test_money_formatting_matches():
    got = run_js("console.log(JSON.stringify([money(84), money(3), money(0.5)]))")
    assert got == [f.money(84), f.money(3), "500 roubles"]
