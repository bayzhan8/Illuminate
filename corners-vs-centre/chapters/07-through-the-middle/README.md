<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · Through the middle

![The workshop region with a smooth red curve running through its interior. The
curve begins at a marked point near the middle and bends towards the optimal
corner, with intermediate points labelled by decreasing values of mu, never
touching any wall.](the-path.gif)

![The same central path drawn as a still, with the analytic centre marked at one
end, individual points labelled mu equals one thousand, ten and nought point
one along it, and the optimal corner marked at the
other.](the-path.png)

In 1984 Narendra Karmarkar, at Bell Labs, published a polynomial method that
was also *fast*. That combination was new, and it restarted the argument.

The idea that ended up mattering most is not the projective transformation
Karmarkar originally used but the reformulation the field settled on shortly
after. Add to the objective a penalty that blows up at every wall:

> maximise **profit**, minus **μ** × (sum of the logs of the slack in each rule)

The logarithm is infinite at a wall, so no minimiser of that expression can
touch one. Every solution of the penalised problem is strictly inside.

Now vary μ:

- **μ enormous.** Profit is irrelevant; the point sits as far from every wall
  as it can get. For the workshop that is **(2.428, 3.209)**, the *analytic
  centre*, which is a property of the shape alone.
- **μ shrinking.** The walls push more weakly, and the point drifts towards
  profitable territory.
- **μ approaching zero.** The penalty stops mattering and the point approaches
  the true optimum, which is on the boundary, without ever getting there.

The curve traced out is the **central path**, and the key thing about it is
what each of its points *is*. It is not an approximation being refined. Every
point on that curve is the exact optimum of a genuinely different, perfectly
well-posed problem: the one where walls repel with strength μ. The method
solves an easy nearby problem exactly, then makes the problem less nearby.

Two things worth noticing. The barrier idea was not new in 1984: Ragnar Frisch
proposed the logarithmic barrier in 1955, and Fiacco and McCormick had built a
general nonlinear framework on it by 1968. What was new was the complexity
analysis and the demonstration that this could beat simplex on real problems.
And the resemblance to Karmarkar's method was not a coincidence anyone had to
guess at: within two years it had been shown that his method is equivalent to a
projected Newton barrier method.

> **In one sentence.** Replace the walls with a repulsion you control, solve
> that exactly, then turn the repulsion down.

---

Chapter 7 of 10

Previous: [Polynomial, and slower](../06-polynomial-and-slower/README.md)  
Next: [What the barrier actually does](../08-what-the-barrier-does/README.md)  
Contents: [corners-vs-centre](../../README.md)
