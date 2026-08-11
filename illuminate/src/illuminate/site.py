"""One lesson file per topic, turned into everything a reader sees.

Each topic writes a ``lesson.md`` and a small ``build.py`` that says what its
chapters are called and what its interactive pages do.  Everything structural
-- splitting the lesson, generating the chapter files, the page shell, the
sandbox shell, the navigation -- lives here, so a second topic is a
configuration rather than a copy.

The site is served from the repository root rather than from a ``docs`` folder.
That means the image paths written in ``lesson.md`` are the same paths the
published page uses: a figure has exactly one home and nothing is rewritten or
stored twice.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

from markdown_it import MarkdownIt

SITE = "https://bayzhan8.github.io/Illuminate"
REPO = "https://github.com/bayzhan8/Illuminate"

renderer = MarkdownIt("commonmark").enable("table")

# Applied before first paint so a dark-mode reader never sees a cream flash.
# Kept as a constant rather than inlined in the templates because its braces
# would otherwise have to be doubled to survive str.format.
THEME_BOOT = """<script>
  try {
    var t = localStorage.getItem("illuminate-theme");
    document.documentElement.dataset.theme = t ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  } catch (e) {}
</script>"""


@dataclass
class Chapter:
    number: int
    folder: str
    title: str


@dataclass
class Sandbox:
    chapter: int
    title: str
    lede: str
    try_this: str
    controls: str
    widget: str
    note: str


@dataclass
class Topic:
    """Everything the shared machinery needs to know about one topic."""

    slug: str                     # folder name, e.g. "branch-and-price"
    root: Path                    # that folder, absolute
    title: str                    # page <title>
    blurb: str                    # meta description
    chapters: list[Chapter]
    sandboxes: list[Sandbox] = field(default_factory=list)
    maths: str = ""               # JavaScript shared by every sandbox
    heading: str = ""             # the h1 the lesson starts with, for checking

    @property
    def lesson(self) -> Path:
        return self.root / "lesson.md"


# --- reading the lesson ----------------------------------------------------

def split_lesson(topic: Topic) -> tuple[str, list[str], str]:
    """(front matter, one block of markdown per chapter, everything after).

    Chapters are delimited by a horizontal rule and recognised by their
    heading, so the lesson stays a document a person can read top to bottom
    rather than a file full of markers for a build script.
    """
    parts = re.split(r"\n---\n", topic.lesson.read_text())
    front, chapters, tail = parts[0], [], []
    for part in parts[1:]:
        (chapters if re.match(r"\s*## \d+ · ", part) else tail).append(part.strip())
    if len(chapters) != len(topic.chapters):
        raise SystemExit(f"{topic.slug}: lesson.md has {len(chapters)} chapters, "
                         f"build.py expects {len(topic.chapters)}")
    return front.strip(), chapters, "\n\n---\n\n".join(t for t in tail if t)


# --- chapter files ---------------------------------------------------------

def chapter_markdown(topic: Topic, index: int, body: str) -> str:
    chapter = topic.chapters[index]
    # images are addressed from the chapter's own folder, so drop the prefix
    body = body.replace(f"chapters/{chapter.folder}/", "")
    nav = []
    if index > 0:
        previous = topic.chapters[index - 1]
        nav.append(f"← [{previous.title}](../{previous.folder}/README.md)")
    nav.append("[all chapters](../..#chapters)")
    if index < len(topic.chapters) - 1:
        following = topic.chapters[index + 1]
        nav.append(f"[{following.title}](../{following.folder}/README.md) →")
    return "\n".join([
        "<!-- generated from ../../lesson.md by ../../build.py; do not edit -->",
        "", body, "", "---", "", " · ".join(nav),
    ]) + "\n"


def build_chapters(topic: Topic) -> None:
    _, chapters, _ = split_lesson(topic)
    for index, body in enumerate(chapters):
        folder = topic.root / "chapters" / topic.chapters[index].folder
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "README.md").write_text(chapter_markdown(topic, index, body))
    print(f"  wrote {len(chapters)} chapter files")


# --- the reading page ------------------------------------------------------

PAGE = """<!doctype html>
<html lang="en" data-page="lesson">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{blurb}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/site.css">
{boot}
</head>
<body>
<header class="bar">
  <a class="brand" href="../">ILLUMINATE</a>
  <button class="toggle" id="theme" type="button" aria-label="Switch colour scheme">DARK</button>
</header>
<main class="prose">
{body}
</main>
<footer class="foot">
  <a href="{site}">Illuminate</a> ·
  <a href="{repo}/tree/main/{slug}">source and tests</a>
</footer>
<script src="../assets/site.js"></script>
</body>
</html>
"""


def decorate(body: str) -> str:
    """Structural passes the Markdown itself should not have to carry."""
    # Every image becomes a bordered plate. The alt text stays alt text: it
    # describes the picture for someone who cannot see it, and repeating it as
    # a visible caption would only say again what the prose beside it says.
    body = re.sub(
        r'<p><img src="([^"]+)" alt="([^"]*)"\s*/?></p>',
        lambda m: (f'<figure class="plate">'
                   f'<img src="{m.group(1)}" alt="{m.group(2)}" loading="lazy">'
                   f'</figure>'),
        body)
    body = re.sub(
        r'<h2>(\d+) · ([^<]+)</h2>',
        lambda m: (f'<h2 id="ch{m.group(1)}"><span class="num">{m.group(1)}</span>'
                   f'{m.group(2)}</h2>'),
        body)
    body = body.replace("<table>", '<div class="scroll"><table>')
    body = body.replace("</table>", "</table></div>")
    body = body.replace("<blockquote>", '<blockquote class="aside">')
    return body


def build_page(topic: Topic) -> None:
    front, chapters, tail = split_lesson(topic)
    body = decorate(renderer.render("\n\n".join([front] + chapters + [tail])))
    (topic.root / "index.html").write_text(PAGE.format(
        title=html.escape(topic.title), blurb=html.escape(topic.blurb),
        body=body, site=SITE, repo=REPO, slug=topic.slug, boot=THEME_BOOT))
    print(f"  wrote {topic.slug}/index.html")


# --- the interactive pages -------------------------------------------------

SANDBOX_PAGE = """<!doctype html>
<html lang="en" data-page="sandbox">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Illuminate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/site.css">
{boot}
</head>
<body>
<header class="bar">
  <a class="brand" href="../../">ILLUMINATE</a>
  <button class="toggle" id="theme" type="button" aria-label="Switch colour scheme">DARK</button>
</header>
<main class="sandbox">
  <a class="back" href="../index.html#ch{chapter}">← back to chapter {chapter}</a>
  <h1>{title}</h1>
  <p class="lede">{lede}</p>
  <p class="try"><strong>Try this.</strong> {try_this}</p>
  <canvas id="c" width="660" height="380"></canvas>
  <div class="controls">{controls}</div>
  <pre class="out" id="out"></pre>
  <p class="note">{note}</p>
  <nav class="pager">{pager}</nav>
</main>
<script src="../../assets/site.js"></script>
<script>
{maths}
{plot}
{widget}
</script>
</body>
</html>
"""

SANDBOX_INDEX = """<!doctype html>
<html lang="en" data-page="sandbox-index">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Things to play with — Illuminate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/site.css">
{boot}
</head>
<body>
<header class="bar">
  <a class="brand" href="../../">ILLUMINATE</a>
  <button class="toggle" id="theme" type="button" aria-label="Switch colour scheme">DARK</button>
</header>
<main class="prose">
<h1>Things to play with</h1>
<p>{count} pages from this guide, each one a chapter you can push around. They
run entirely in the page.</p>
<ul class="chapters">{items}</ul>
<p><a href="../index.html">← back to the guide</a></p>
</main>
<script src="../../assets/site.js"></script>
</body>
</html>
"""


def slider(ident, label, lo, hi, step, value):
    return (f'<div class="row"><label for="{ident}">{label}</label>'
            f'<input type="range" id="{ident}" min="{lo}" max="{hi}" '
            f'step="{step}" value="{value}">'
            f'<output class="val" id="{ident}v"></output></div>')


def build_sandbox(topic: Topic) -> None:
    if not topic.sandboxes:
        return
    out_dir = topic.root / "sandbox"
    out_dir.mkdir(exist_ok=True)
    for position, box in enumerate(topic.sandboxes):
        pager = []
        if position > 0:
            before = topic.sandboxes[position - 1]
            pager.append(f'<a href="{before.chapter:02d}.html">← {before.title}</a>')
        pager.append(f'<a href="index.html">all {len(topic.sandboxes)}</a>')
        if position < len(topic.sandboxes) - 1:
            after = topic.sandboxes[position + 1]
            pager.append(f'<a href="{after.chapter:02d}.html">{after.title} →</a>')
        (out_dir / f"{box.chapter:02d}.html").write_text(SANDBOX_PAGE.format(
            chapter=box.chapter, title=html.escape(box.title),
            lede=html.escape(box.lede), try_this=html.escape(box.try_this),
            controls=box.controls, note=html.escape(box.note),
            pager=" · ".join(pager), maths=topic.maths, plot=PLOT,
            widget=box.widget, boot=THEME_BOOT))

    items = "\n".join(
        f'<li><a href="{b.chapter:02d}.html"><span class="num">{b.chapter}</span>'
        f'{html.escape(b.title)}</a>'
        f'<span class="sub">{html.escape(b.lede)}</span></li>'
        for b in topic.sandboxes)
    (out_dir / "index.html").write_text(SANDBOX_INDEX.format(
        items=items, count=len(topic.sandboxes), boot=THEME_BOOT))
    print(f"  wrote {len(topic.sandboxes)} sandbox pages + index")


# --- the drawing helper every sandbox gets ---------------------------------

PLOT = r"""
// --- a very small drawing helper, in the site's colours -------------------
function palette() {
  const dark = document.documentElement.dataset.theme === "dark";
  return dark
    ? { paper: "#1a1816", ink: "#e8e6e0", ink2: "#a8a599", muted: "#787366",
        rule: "#4a4540", plan: "#4A87CC", price: "#C25A42", ok: "#4E8F55" }
    : { paper: "#fffff8", ink: "#000000", ink2: "#404040", muted: "#707070",
        rule: "#C0BDAD", plan: "#1B4F9C", price: "#B4341F", ok: "#2E6B33" };
}

function Plot(canvas, xlo, xhi, ylo, yhi, pad) {
  const dpr = window.devicePixelRatio || 1;
  const cssW = canvas.clientWidth || 660, cssH = canvas.clientHeight || 380;
  canvas.width = Math.round(cssW * dpr);
  canvas.height = Math.round(cssH * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  pad = pad || { l: 54, r: 22, t: 18, b: 42 };
  const P = palette();
  const X = x => pad.l + (x - xlo) / (xhi - xlo) * (cssW - pad.l - pad.r);
  const Y = y => cssH - pad.b - (y - ylo) / (yhi - ylo) * (cssH - pad.t - pad.b);
  const font = n => `${n}px "IBM Plex Mono", ui-monospace, monospace`;
  return {
    ctx, X, Y, P, W: cssW, H: cssH, pad, font,
    clear() { ctx.clearRect(0, 0, cssW, cssH); },
    grid(stepX, stepY) {
      ctx.strokeStyle = P.rule; ctx.lineWidth = 1; ctx.setLineDash([1, 4]);
      for (let x = xlo; x <= xhi + 1e-9; x += stepX) {
        ctx.beginPath(); ctx.moveTo(X(x), pad.t); ctx.lineTo(X(x), cssH - pad.b); ctx.stroke();
      }
      for (let y = ylo; y <= yhi + 1e-9; y += stepY) {
        ctx.beginPath(); ctx.moveTo(pad.l, Y(y)); ctx.lineTo(cssW - pad.r, Y(y)); ctx.stroke();
      }
      ctx.setLineDash([]);
    },
    axes(xlabel, ylabel, stepX, stepY) {
      ctx.strokeStyle = P.ink; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, cssH - pad.b);
      ctx.lineTo(cssW - pad.r, cssH - pad.b); ctx.stroke();
      ctx.fillStyle = P.muted; ctx.font = font(11); ctx.textAlign = "center";
      if (stepX) for (let x = xlo; x <= xhi + 1e-9; x += stepX)
        ctx.fillText(String(Math.round(x)), X(x), cssH - pad.b + 17);
      ctx.textAlign = "right";
      if (stepY) for (let y = ylo; y <= yhi + 1e-9; y += stepY)
        ctx.fillText(String(Math.round(y)), pad.l - 9, Y(y) + 4);
      ctx.fillStyle = P.ink2; ctx.font = font(12); ctx.textAlign = "center";
      if (xlabel) ctx.fillText(xlabel, (pad.l + cssW - pad.r) / 2, cssH - 8);
      if (ylabel) { ctx.save(); ctx.translate(14, (pad.t + cssH - pad.b) / 2);
        ctx.rotate(-Math.PI / 2); ctx.fillText(ylabel, 0, 0); ctx.restore(); }
    },
    polygon(pts, fill, stroke) {
      if (!pts.length) return;
      ctx.beginPath(); ctx.moveTo(X(pts[0][0]), Y(pts[0][1]));
      for (const p of pts.slice(1)) ctx.lineTo(X(p[0]), Y(p[1]));
      ctx.closePath();
      if (fill) { ctx.globalAlpha = 0.14; ctx.fillStyle = fill; ctx.fill(); ctx.globalAlpha = 1; }
      if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.8; ctx.stroke(); }
    },
    rect(x0, y0, x1, y1, fill, alpha) {
      ctx.save(); ctx.globalAlpha = alpha === undefined ? 1 : alpha;
      ctx.fillStyle = fill;
      ctx.fillRect(X(x0), Y(y1), X(x1) - X(x0), Y(y0) - Y(y1));
      ctx.restore();
    },
    line(x0, y0, x1, y1, color, width, dash) {
      ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = width || 1.4;
      if (dash) ctx.setLineDash(dash);
      ctx.beginPath(); ctx.moveTo(X(x0), Y(y0)); ctx.lineTo(X(x1), Y(y1));
      ctx.stroke(); ctx.restore();
    },
    dot(x, y, color, r) {
      ctx.beginPath(); ctx.arc(X(x), Y(y), r || 6, 0, 7);
      ctx.fillStyle = color; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = P.paper; ctx.stroke();
    },
    label(x, y, text, color, align, size) {
      ctx.fillStyle = color; ctx.font = font(size || 12);
      ctx.textAlign = align || "left"; ctx.fillText(text, X(x), Y(y));
    }
  };
}

function sortRound(pts) {
  if (!pts.length) return pts;
  const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
  const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
  return pts.slice().sort((a, b) =>
    Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx));
}
"""


# --- entry point -----------------------------------------------------------

def main(topic: Topic, argv: list[str]) -> None:
    jobs = {"chapters": build_chapters, "page": build_page, "sandbox": build_sandbox}
    wanted = argv or ["all"]
    if wanted == ["all"]:
        wanted = list(jobs)
    for job in wanted:
        if job not in jobs:
            raise SystemExit(f"unknown job {job!r}; try: {', '.join(jobs)} or all")
        jobs[job](topic)
