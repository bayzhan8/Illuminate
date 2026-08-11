"""House style for every figure in every topic: cream paper, black ink, one typeface.

The figures are meant to look like plates pasted into a notebook rather than
like output from a plotting library, because that is what the surrounding site
looks like.  Practically that means: the paper colour is the page's paper
colour, the typeface is the page's typeface, corners are square, nothing has a
drop shadow, and the grid is faint enough to read past.

Two colours carry meaning and only two, all the way through the guide:
**blue is the plan** and **rust is the prices**.  They were checked with a
colour-vision simulator rather than by eye -- every pair of them stays more
than twenty perceptual units apart under protanopia, deuteranopia and
tritanopia, on both the light and the dark surface.  Green appears only as a
status mark, never as a third series, and never without a word or a tick
beside it saying what it means.

Images cannot restyle themselves when a reader flips the page to dark mode, so
they do not try: every figure is rendered on cream and the page mats it in a
bordered plate that stays cream in both modes.  A figure that inverted would
have to invert its ink too, and then the two colours above would need a second
validated pair; a mat is cheaper and reads as deliberate.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# the palette

SURFACE = "#fffff8"     # the site's page colour
TEXT = "#000000"
TEXT_DIM = "#404040"
TEXT_FAINT = "#707070"
HAIRLINE = "#C0BDAD"      # the site's soft border

PLAN = "#1B4F9C"      # blue: primal, plans, what a workshop can actually do
PRICE = "#B4341F"     # rust: dual, prices, what a ceiling costs
OK = "#2E6B33"        # status only, always beside a word or a tick
WARN = "#A9761A"      # status only

PLAN_FILL = "#1B4F9C22"
PRICE_FILL = "#B4341F22"

FONTS = Path(__file__).resolve().parent / "fonts"


def _install_fonts() -> str:
    """Register the vendored typeface, and fall back quietly if it is missing.

    The font ships with the repository (it is under the SIL Open Font Licence,
    see assets/fonts/OFL.txt) so that a clone renders byte-identical figures
    instead of picking up whatever monospace the machine happens to have.
    """
    for ttf in sorted(FONTS.glob("*.ttf")):
        fm.fontManager.addfont(str(ttf))
    have = {f.name for f in fm.fontManager.ttflist}
    for name in ("IBM Plex Mono", "Menlo", "DejaVu Sans Mono"):
        if name in have:
            return name
    return "monospace"


FAMILY = _install_fonts()

plt.rcParams.update({
    "font.family": FAMILY,
    "font.size": 11,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": TEXT,
    "axes.edgecolor": TEXT,
    "axes.labelcolor": TEXT_DIM,
    "axes.linewidth": 1.1,
    "axes.grid": False,
    "xtick.color": TEXT_FAINT,
    "ytick.color": TEXT_FAINT,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": False,
    "legend.fontsize": 10,
    "figure.dpi": 110,
})


# building blocks

def figure(width: float = 8.2, height: float = 4.6):
    """A figure rounded to an even pixel size in both directions.

    Pillow's GIF writer needs even dimensions. Odd ones produce a one-pixel
    per-row skew, so the rounding happens here rather than being remembered
    at each call site.
    """
    dpi = plt.rcParams["figure.dpi"]
    width = round(width * dpi / 2) * 2 / dpi
    height = round(height * dpi / 2) * 2 / dpi
    return plt.subplots(figsize=(width, height))


def style(ax, xlabel: str = "", ylabel: str = "", grid: bool = True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(TEXT)
    ax.spines["bottom"].set_color(TEXT)
    if grid:
        ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
        ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=TEXT_DIM, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=TEXT_DIM, labelpad=8)
    return ax


TRACK = " "  # hair space: matplotlib has no letter-spacing, so fake it


def heading(ax, text: str):
    """A small tracked-out uppercase label, the way the site titles its sections.

    The site sets these at 0.12em of extra letter-spacing.  Matplotlib has no
    such property, so the tracking is inserted as hair spaces between the
    characters -- about a tenth of an em each, which lands close.  A plain
    space, the obvious thing to reach for, is a full quarter-em and turns a
    six-word heading into something twice the width of its own panel.
    """
    ax.set_title(TRACK.join(text.upper()), loc="left", fontsize=9.5,
                 color=TEXT_FAINT, pad=12, fontweight="semibold")


def tag(ax, x, y, text, color=TEXT, ha="left", va="center", size=10.5, weight="normal"):
    """A direct label on the mark itself, so colour is never the only cue."""
    return ax.text(x, y, text, color=color, ha=ha, va=va, fontsize=size,
                   fontweight=weight, zorder=8)


def plate(ax, x, y, text, color=TEXT, ha="left", va="bottom", size=10):
    """Text in a square-cornered box, matching the site's bordered cards."""
    return ax.text(x, y, text, color=color, ha=ha, va=va, fontsize=size, zorder=9,
                   bbox=dict(boxstyle="square,pad=0.45", facecolor=SURFACE,
                             edgecolor=color, linewidth=1.1))


def margin_note(fig, x=0.014, y=0.03, size=10.5, color=TEXT_DIM, ha="left"):
    """A text handle in the bottom margin, for values that change per frame.

    Needs ``fig.subplots_adjust(bottom=...)`` to have reserved the space.
    Placing it outside the axes means it cannot collide with the drawing at
    any frame, which is otherwise a per-figure thing to get wrong.
    """
    return fig.text(x, y, "", ha=ha, va="bottom", fontsize=size, color=color,
                    family=FAMILY, zorder=20)


# output

def _short(path: Path) -> str:
    """<topic>/chapters/<chapter>/<file>, however deep the repository sits."""
    return "/".join(path.parts[-4:])

def save(fig, path: Path, tight: bool = True) -> Path:
    """Write a PNG.

    Pass ``tight=False`` when the figure has already set its own margins with
    ``subplots_adjust``.  ``tight_layout`` reflows the axes to fit the largest
    text in them, so on a panel carrying a big annotation box it will happily
    shrink the drawing to a strip to make the words fit -- which is backwards.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if tight:
        fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)
    print(f"  wrote {_short(path)}")
    return path


def animate(fig, update, frames: int, path: Path, fps: int = 12,
            hold: float = 2.5, loop_smoothly: bool = False) -> Path:
    """Write a GIF, appending duplicate trailing frames so the last one lasts.

    ``hold`` is a duration in seconds. Callers must saturate their own frame
    index (``i = min(i, frames - 1)``) or the extra frames will index past the
    end. Because they render identically, the encoder folds them into one
    long-duration frame and the pause is free.

    ``loop_smoothly=True`` suppresses the hold, for cyclic motion where a pause
    would read as a stutter.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    extra = 0 if loop_smoothly else max(1, round(fps * hold))
    anim = FuncAnimation(fig, update, frames=frames + extra, interval=1000 / fps,
                         blit=False)
    # GIF has no interframe compression worth the name, so rendering resolution
    # is file size. 92dpi keeps the type crisp at the width these are shown at.
    anim.save(path, writer=PillowWriter(fps=fps), dpi=92,
              savefig_kwargs={"facecolor": SURFACE})
    plt.close(fig)
    shrink_gif(path)
    print(f"  wrote {_short(path)} ({path.stat().st_size / 1024:.0f} kB)")
    return path


def shrink_gif(path: Path, colours: int = 48) -> None:
    """Re-encode the whole animation onto a single quantised palette.

    Matplotlib emits anti-aliased 24-bit frames; the default encoder then
    derives a palette per frame and spends most of the file on thousands of
    almost-identical background tones. Sampling one palette across the
    animation and mapping every frame onto it cuts these to roughly a quarter,
    with no visible change on flat-colour line art.

    Dithering is disabled: it introduces high-frequency noise into flat regions,
    which is the worst possible input for LZW.
    """
    from PIL import Image, ImageSequence

    src = Image.open(path)
    frames, durations = [], []
    for frame in ImageSequence.Iterator(src):
        durations.append(frame.info.get("duration", 80))
        frames.append(frame.convert("RGB"))
    if not frames:
        return

    # sample across the animation so late-appearing colours reach the palette
    picks = [frames[round(k * (len(frames) - 1) / 7)] for k in range(8)]
    width, height = frames[0].size
    swatch = Image.new("RGB", (width, height * len(picks)))
    for k, frame in enumerate(picks):
        swatch.paste(frame, (0, height * k))
    palette = swatch.quantize(colors=colours, method=Image.Quantize.MEDIANCUT)

    flat = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    # No disposal method is set on purpose. Asking for "restore to background"
    # makes every frame a full repaint; leaving it alone lets the encoder store
    # only the rectangle that actually changed, which on these drawings is a
    # thin band around one moving line.
    flat[0].save(path, save_all=True, append_images=flat[1:], loop=0,
                 duration=durations, optimize=True)


def chapter_dir(slug: str, topic_root: Path | None = None) -> Path:
    """The folder a chapter's images belong in.

    Figure scripts live in ``<topic>/figures/`` and are run from there, so the
    topic root is two levels up from the calling script unless it is given.
    """
    if topic_root is None:
        import __main__
        topic_root = Path(getattr(__main__, "__file__", ".")).resolve().parents[1]
    d = Path(topic_root) / "chapters" / slug
    d.mkdir(parents=True, exist_ok=True)
    return d
