<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · The wall that pushes back

In 1984 Narendra Karmarkar, at Bell Labs, published a polynomial method that
was also *fast*. That combination was new, and it restarted the argument.

The idea that ended up mattering most is not the projective transformation
Karmarkar originally used but the reformulation the field settled on shortly
after, and it starts from a complaint about corners. Every method so far has
had to treat a wall as a hard edge: you are on the legal side or you are not,
and the moment you touch one the rules change. That is what makes the problem
combinatorial. So get rid of the edges. Make the walls push.

One word and one letter first, and between them they are the only new notation
in this guide. The **slack** in a rule, for a particular plan, is how much of
that rule is still going spare. The
workshop has 44 planks; a plan that consumes 40 of them has 4 planks of slack.
Every rule has its own slack, and so does each of the two floors, since you
cannot build a negative number of chairs. Slack is positive everywhere inside
the region and exactly zero on the walls, which is what makes it the right
thing to build a penalty out of.

So score a plan not by its profit but by this:

> **profit** + **μ** × (sum of the logs of the slack in each rule)

and hunt for the best score. The letter is **μ**, Greek lowercase mu, and it is
simply a dial: a number you choose that says how hard the walls push. Read it as
"how strongly the walls repel" every time it appears.

The second term is the whole idea, and the logarithm in it is doing something
specific that no ordinary penalty would.

A logarithm of a number smaller than one is negative, and it has no floor at
all. Halve the slack and the log drops by a fixed amount. Halve it again and it
drops by that same amount again. Slack of a thousandth, a millionth, a
billionth, and the log is still marching downwards with no sign of bottoming
out. Compare that with penalising, say, the reciprocal of the slack, or its
square: those also grow, but a plan can still buy its way through them if the
profit on the other side is large enough. Nothing outbids a term with no lower
bound. A plan pressed against a wall scores minus infinity, and no amount of
profit is worth minus infinity.

So whatever plan wins this score is strictly inside, with room left in every
rule at once, and it got there without anybody writing down a rule that says
*stay inside*. The boundary has stopped being a constraint and become a force.

That is the trade the rest of this guide turns on. μ is the strength of the
force, and it is yours to set.

> **In one sentence.** Replacing each wall with a penalty that has no floor
> turns "stay legal" from a rule to be enforced into a force to be balanced.

---

Chapter 10 of 14

Previous: [Polynomial, and slower](../09-polynomial-and-slower/README.md)  
Next: [The central path](../11-the-central-path/README.md)  
Contents: [corners-vs-centre](../../README.md)
