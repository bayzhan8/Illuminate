<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 12 · What the barrier actually does

![Three side-by-side contour plots of the same region at decreasing values of
mu. In the first the contours form a broad bowl with its lowest point near the
middle. In the second the bowl has tilted and its minimum has slid towards the
best corner. In the third the contours are compressed against that corner.](the-landscape.png)

The path is the trail of minima. The surface is what produces them, and it
explains why this works at all. (Solvers flip every sign and hunt for the
smallest score rather than the largest, which is why these are pictures of
bowls with a bottom rather than hills with a peak. Same problem, drawn upside
down.)

At μ = 100 the penalty dominates and the surface is a broad bowl sitting in the
middle of the region. Its minimum is worth **$194**, which is nowhere near
optimal and is not trying to be. At μ = 10 the bowl has tilted towards profit
and its bottom has slid to a point worth **$325**. At μ = 1 the contours are
crushed into the corner and the minimum is worth **$348**.

At every stage there is exactly one minimum and the surface around it is
smooth and curved. That is the whole trick, because a smooth bowl with one
bottom is precisely what Newton's method is for.

Newton's method goes like this. Stand anywhere on the surface and measure two
things about the ground under your feet: which way it slopes, and how fast that
slope is changing. Those two measurements are enough to fit a parabola through
where you stand, or in two variables a bowl, and the bottom of a fitted bowl is
something you can solve for directly. Jump to it. You have not arrived, since
the fitted bowl was only a local likeness of the real surface, but you are
nearer than you were, so measure again where you land and fit a fresh one. The
likeness improves as you close in, and near the bottom each step roughly
doubles the number of correct digits. A handful of steps is usually the whole
story.

The number of steps does not depend on how many corners the region has, because
nothing in the computation ever mentions a corner.

The one safeguard that matters is damping. A full Newton step will cheerfully
walk through a wall, where the objective is not merely worse but undefined, so
each step is halved until it lands somewhere legal. That is the entire
defensive apparatus.

Compare what the two methods are counting. Simplex counts *corners visited*,
and how many that will be is a combinatorial question about the shape. The
barrier counts *Newton solves*, and how many that will be is a question about
how fast you turn μ down.

> **In one sentence.** Turning the boundary into a smooth penalty converts a
> combinatorial problem into a sequence of calculus problems, and calculus
> problems come with step counts you can predict.

---

Chapter 12 of 14

Previous: [The central path](../11-the-central-path/README.md)  
Next: [A gap you can forecast](../13-a-gap-you-can-forecast/README.md)  
Contents: [corners-vs-centre](../../README.md)
