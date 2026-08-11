"""House style for every figure: cream paper, black ink, one typeface.

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

# --- the palette -----------------------------------------------------------

PAPER = "#fffff8"     # the site's page colour
INK = "#000000"
INK2 = "#404040"
MUTED = "#707070"
RULE = "#C0BDAD"      # the site's soft border

PLAN = "#1B4F9C"      # blue: primal, plans, what a workshop can actually do
PRICE = "#B4341F"     # rust: dual, prices, what a ceiling costs
OK = "#2E6B33"        # status only, always beside a word or a tick
WARN = "#A9761A"      # status only

PLAN_FILL = "#1B4F9C22"
PRICE_FILL = "#B4341F22"

FONTS = Path(__file__).resolve().parents[2] / "assets" / "fonts"


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
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "text.color": INK,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK2,
    "axes.linewidth": 1.1,
    "axes.grid": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": False,
    "legend.fontsize": 10,
    "figure.dpi": 110,
})


# --- building blocks -------------------------------------------------------

def figure(width: float = 8.2, height: float = 4.6):
    """A figure whose pixel size is even in both directions.

    An odd pixel width comes out of the GIF encoder sheared by a pixel per
    row, which looks like a rendering bug and is really an encoder detail.
    """
    dpi = plt.rcParams["figure.dpi"]
    width = round(width * dpi / 2) * 2 / dpi
    height = round(height * dpi / 2) * 2 / dpi
    return plt.subplots(figsize=(width, height))


def style(ax, xlabel: str = "", ylabel: str = "", grid: bool = True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    if grid:
        ax.grid(True, color=RULE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
        ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=INK2, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=INK2, labelpad=8)
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
                 color=MUTED, pad=12, fontweight="semibold")


def tag(ax, x, y, text, color=INK, ha="left", va="center", size=10.5, weight="normal"):
    """A direct label on the mark itself, so colour is never the only cue."""
    return ax.text(x, y, text, color=color, ha=ha, va=va, fontsize=size,
                   fontweight=weight, zorder=8)


def plate(ax, x, y, text, color=INK, ha="left", va="bottom", size=10):
    """Text in a square-cornered box, matching the site's bordered cards."""
    return ax.text(x, y, text, color=color, ha=ha, va=va, fontsize=size, zorder=9,
                   bbox=dict(boxstyle="square,pad=0.45", facecolor=PAPER,
                             edgecolor=color, linewidth=1.1))


def readout(fig, x=0.014, y=0.03, size=10.5, color=INK2, ha="left"):
    """A live number parked in the margin under the axes.

    Figures here are read like a caption and a plate, not like a dashboard, so
    the changing number belongs with the caption.  Keeping it out of the axes
    also removes any question of it landing on a line as the drawing moves.
    Reserve the space with ``fig.subplots_adjust(bottom=...)`` before calling.
    """
    return fig.text(x, y, "", ha=ha, va="bottom", fontsize=size, color=color,
                    family=FAMILY, zorder=20)


# --- output ----------------------------------------------------------------

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
    fig.savefig(path, facecolor=PAPER, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)
    print(f"  wrote {path.relative_to(path.parents[3])}")
    return path


def animate(fig, update, frames: int, path: Path, fps: int = 12,
            hold: float = 2.5, loop_smoothly: bool = False) -> Path:
    """Write a GIF that pauses on its conclusion before looping.

    These animations are arguments, and an argument needs a beat at the end.
    ``hold`` requests extra frames past the last real one; the update functions
    clamp their index, so those come out identical and the encoder collapses
    them into a single long-duration frame -- the pause costs nothing in file
    size.  Pass ``loop_smoothly`` for a figure whose motion is itself the
    content, where stopping would be the wrong reading.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    extra = 0 if loop_smoothly else max(1, round(fps * hold))
    anim = FuncAnimation(fig, update, frames=frames + extra, interval=1000 / fps,
                         blit=False)
    # GIF has no interframe compression worth the name, so rendering resolution
    # is file size. 92dpi keeps the type crisp at the width these are shown at.
    anim.save(path, writer=PillowWriter(fps=fps), dpi=92,
              savefig_kwargs={"facecolor": PAPER})
    plt.close(fig)
    shrink_gif(path)
    print(f"  wrote {path.relative_to(path.parents[3])} "
          f"({path.stat().st_size / 1024:.0f} kB)")
    return path


def shrink_gif(path: Path, colours: int = 48) -> None:
    """Re-encode onto one shared palette, which is most of the file size.

    Matplotlib writes anti-aliased frames in full colour, so the encoder builds
    a fresh palette per frame and stores thousands of near-identical creams.
    These drawings only really contain a handful of colours, so one palette
    sampled across the whole animation covers every frame; dithering is turned
    off because it invents noise in flat areas, and noise is exactly what does
    not compress.  Typically about a quarter of the original size, with no
    visible difference on flat-colour line art.
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


def chapter_dir(slug: str) -> Path:
    d = Path(__file__).resolve().parents[2] / "chapters" / slug
    d.mkdir(parents=True, exist_ok=True)
    return d
