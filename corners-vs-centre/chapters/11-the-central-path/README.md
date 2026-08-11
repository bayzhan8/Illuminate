<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 11 · The central path

![The workshop region with a smooth red curve running through its interior. The
curve begins at a marked point near the middle and bends towards the optimal
corner, with intermediate points labelled by decreasing values of mu, never
touching any wall.](the-path.gif)

![The same central path drawn as a still, with the analytic centre marked at one
end, individual points labelled mu equals one thousand, ten and nought point
one along it, and the optimal corner marked at the
other.](the-path.png)

One setting of μ gives one point. Sweep it and the points join up.

- **μ enormous.** Profit is irrelevant; the point sits as far from every wall
  as it can get. For the workshop that is **(2.428, 3.209)**, the *analytic
  centre*, which is a property of the shape alone.
- **μ shrinking.** The walls push more weakly, and the point drifts towards
  profitable territory.
- **μ approaching zero.** The penalty stops mattering and the point approaches
  the true optimum, which is on the boundary, without ever getting there.

The curve traced out is the **central path**.

Now the thing worth being careful about, because it is what separates this from
every other method that produces a sequence of approximations. Every point on
that curve is *exact*. It is not a rough answer waiting to be refined. It is the
precise, perfectly-attained optimum of a genuinely different and perfectly
well-posed problem: the one where the walls repel with strength μ.

So the method never approximates anything. It solves an easy nearby problem
exactly, then changes the problem to a less nearby one and solves that exactly
too. What is being reduced between rounds is not error. It is the distance
between the question you can answer and the question you were asked.

Two things worth noticing about where this came from. The barrier idea was not
new in 1984. Ragnar Frisch proposed the logarithmic barrier in 1955, and
Fiacco and McCormick had built a general nonlinear framework on it by 1968.
What was new was the complexity analysis and the demonstration that this could
beat simplex on real problems. And the resemblance to Karmarkar's method was
not a coincidence anyone had to guess at: within two years it had been shown
that his method is equivalent to a projected Newton barrier method.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/corners-vs-centre/sandbox/11.html)**
Drag μ from one end to the other and watch the point leave the centre of the
shape and go looking for money.

> **In one sentence.** Sweeping μ traces a curve every point of which is an
> exact answer to a slightly wrong question.

---

Chapter 11 of 14

Previous: [The wall that pushes back](../10-the-wall-that-pushes-back/README.md)  
Next: [What the barrier actually does](../12-what-the-barrier-does/README.md)  
Contents: [corners-vs-centre](../../README.md)
