"""Chapter 1: the dot product two ways, multiply-and-add and length x length x cos.

A plan x of fixed length swings from the 3-ply axis, through the direction of
the lathe arrow a, to the 5-ply axis. Both readouts give the same number every
frame, and the shadow bar shows which one is the picture.
"""

import math

import matplotlib.pyplot as plt

from matplotlib.patches import Arc

from illuminate.draw import PLAN, TEXT, TEXT_DIM, animate, chapter_dir, figure, margin_note
from linprog import mill as f
from scene import (Stages, arrow, claim, direction_line, dot, draw_axes, foot, norm,
                   right_angle, unit)

OUT = chapter_dir("01-inside-the-walls")
plt.rcParams["font.family"] = [plt.rcParams["font.family"][0], "DejaVu Sans Mono"]   # Plex Mono has no θ
A = tuple(float(v) for v in f.MILL.A[0])
NA = norm(A)
L = 14.0
PHI_A = math.degrees(math.atan2(A[1], A[0]))
STAGES = Stages((0, 12), (28, 16), (18, 0))
TITLE = "the dot product a·x two ways: multiply-and-add, or a shadow"


def phi(k, s):
    return (0.0, s * PHI_A, PHI_A + s * (90 - PHI_A))[k]


def sub(k, s, done):
    if done:
        return "x kept length 14 throughout: its direction alone decided the lathe time"
    if k == 0:
        return "x is a plan of length 14 along the 3-ply axis; θ is its angle to a"
    if k == 1 and s >= 1:
        return "x points along a: θ = 0, cos θ = 1, the shadow is all of x"
    if k == 1:
        return "turn x towards a: θ shrinks, the shadow grows, more lathe time"
    return "turn x past a: θ grows again, the shadow shrinks, less lathe time"


def dot_gif():
    fig, ax = figure(7.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.2)
    note = margin_note(fig, y=0.02, size=9.5)
    note.set_family("DejaVu Sans Mono")
    frames = STAGES.total

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        done = i == frames - 1
        if done:
            s = 1.0
        p_deg = phi(k, s)
        x = (L * math.cos(math.radians(p_deg)), L * math.sin(math.radians(p_deg)))
        ax.clear()
        draw_axes(ax)
        direction_line(ax, A, TEXT_DIM, "the line through a", reach=20.5)
        p = foot(x, A)
        ax.plot([0, p[0]], [0, p[1]], color=PLAN, lw=7, alpha=0.35, solid_capstyle="butt", zorder=3)
        ax.plot([x[0], p[0]], [x[1], p[1]], color=TEXT_DIM, lw=1.0, dashes=(3, 2), zorder=5)
        if norm((x[0] - p[0], x[1] - p[1])) > 0.8:
            right_angle(ax, p, unit((-A[0], -A[1])), unit((x[0] - p[0], x[1] - p[1])))
        arrow(ax, (0, 0), x, PLAN, "x", dx=0.3, dy=0.3)
        arrow(ax, (0, 0), A, TEXT, "a = (1, 2)", dx=0.5, dy=-0.4)
        lo, hi = sorted((p_deg, PHI_A))
        if hi - lo > 3:
            ax.add_patch(Arc((0, 0), 6.4, 6.4, theta1=lo, theta2=hi, color=TEXT, lw=1.2, zorder=6))
            mid = math.radians((lo + hi) / 2)
            ax.text(4.0 * math.cos(mid), 4.0 * math.sin(mid), "θ", fontsize=11, color=TEXT,
                    ha="center", va="center", zorder=7)
        ax.text(p[0] * 0.55 + 0.7, p[1] * 0.55 - 0.6, "shadow", color=PLAN, fontsize=9.5,
                rotation=PHI_A, ha="center", va="center", zorder=7)
        used = dot(A, x)
        cos = math.cos(math.radians(p_deg - PHI_A))
        claim(ax, TITLE, sub(k, s, done))
        note.set_text(
            f"multiply-and-add   {A[0]:g} × {x[0]:4.1f} + {A[1]:g} × {x[1]:4.1f} = {used:4.1f} lathe hours\n"
            f"shadow picture     |a| × |x| cos θ = {NA:.2f} × {L:g} × {cos:.2f} = {used:4.1f}\n"
            f"shadow length      |x| cos θ = {L * cos:4.1f}    θ = {abs(p_deg - PHI_A):4.1f}°")
        return []

    animate(fig, update, frames, OUT / "dot.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    dot_gif()
