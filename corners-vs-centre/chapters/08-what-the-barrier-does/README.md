<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 8 · What the barrier actually does

![Three side-by-side contour plots of the same region at decreasing values of
mu. In the first the contours form a broad bowl with its lowest point near the
middle. In the second the bowl has tilted and its minimum has slid towards the
best corner. In the third the contours are compressed against that corner.](the-landscape.png)

The path is the trail of minima. The surface is what produces them, and it
explains why this works at all.

At μ = 100 the penalty dominates and the surface is a broad bowl sitting in the
middle of the region. Its minimum is worth **$194**, which is nowhere near
optimal and is not trying to be. At μ = 10 the bowl has tilted towards profit
and its bottom has slid to a point worth **$325**. At μ = 1 the contours are
crushed into the corner and the minimum is worth **$348**.

At every stage there is exactly one minimum and the surface around it is
smooth and curved. That is the whole trick. A smooth bowl with one bottom is
what Newton's method is for: build the local quadratic model, jump to its
minimum, repeat. It converges in a handful of steps, and the number of steps
does not depend on how many corners the region has, because nothing in the
computation ever mentions a corner.

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

Chapter 8 of 10

Previous: [Through the middle](../07-through-the-middle/README.md)  
Next: [A gap you can forecast](../09-a-gap-you-can-forecast/README.md)  
Contents: [corners-vs-centre](../../README.md)
