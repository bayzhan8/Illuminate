# Along the edge, or through the middle

**Two ways to solve a linear program, and the forty years of argument between them.**

In 1972 two mathematicians published a shape built to embarrass an algorithm.
It is a cube, squashed so that its faces tilt a little instead of meeting
square, and in ten dimensions it has 1024 corners. Turn the standard method for
linear programming loose on it and the method stops at every one of them: 1023
hops to cross a shape that a better-chosen rule crosses in a single hop.

The method they were embarrassing was twenty-five years old at the time and was
already drawing up refinery schedules and air force logistics. It still is. And
in all those years, on the models people actually solve, it has never once
behaved the way it behaves on that cube. The hop count keeps coming out at a
small multiple of the number of rules in the problem, which is a number you can
afford. A proven catastrophe that nobody ever meets. It took until 2004 for
anybody to explain why.

That gap, between what the theory promised and what everyone could see, is
where the second method comes from. It refuses corners altogether: it starts in
the middle of the region of legal plans and creeps towards the answer along a
curve, never touching a wall. The two were invented thirty-seven years apart,
for different reasons, by people answering different questions, and they have
been argued over ever since. Chapter 10 is where the argument ends up, and the
ending is that they were never really rivals. A large solve today runs one of
them and finishes with the other.

**The plan.** Chapters 1 to 3 build the walk and then show why it should be
hopeless, which is partly a matter of history. Chapters 4 and 5 are the proof
that it is hopeless, and the precise sense in which that proof is narrower than
it sounds. Chapter 6 is the method that was polynomial first and lost anyway.
Chapters 7 to 9 are the one that won a share. Chapter 10 is the division of
labour the two of them settled into.

Every number below is computed by the code in this folder, in exact rational
arithmetic wherever the arithmetic is exact, and asserted by a test. Historical
claims are dated, and where the only source is somebody's own recollection the
text says so.

---

## 0 · What this is

![The same five-sided region drawn twice over. A blue path hugs the boundary,
hopping between corners in three straight segments. A red curve starts near the
middle of the region and sweeps smoothly through the interior, never touching a
wall, and both finish at the same marked point.](chapters/00-what-this-is/two-routes.gif)

A workshop makes tables and chairs. It has 44 planks, 30 hours of bench time
and 32 hours of finishing. A table takes 4 planks, 2 bench hours and 3
finishing hours, and earns $30. A chair takes 2 planks, 3 bench hours and 1
finishing hour, and earns $20.

The best it can do is **9 tables and 4 chairs, worth $350**. Both routes above
find that. They have almost nothing else in common.

The blue route only ever stands at corners. It makes three hops and stops. The
red route never stands at a corner, never even touches a wall, and stops
because it got close enough rather than because it arrived.

> **In one sentence.** Two methods, one answer, and no shared idea about where
> a solution lives.

---

## 1 · A new kind of problem

![A blank plane onto which five constraint lines are added one at a time. Each
new line cuts away part of the shaded area, and after the fifth the survivor is
a five-sided region with its corners marked.](chapters/01-a-new-kind-of-problem/the-region.gif)

Nobody drew that region. It is what is left after each rule takes its cut, and
its corners are simply the places where two rules run out at the same moment.
That is worth dwelling on, because every method in this guide is in some sense
an opinion about those corners: whether to visit them, avoid them, or ignore
them entirely.

The problem itself is old in the way that arithmetic is old. What was new in
the 1940s was treating it as a *computational* question with a general method
attached, rather than as a modelling exercise to be hand-solved case by case.

**1939, Leningrad.** Leonid Kantorovich, asked by a plywood trust how to
allocate work across machines, wrote up a general treatment of what he called
problems of organising and planning production. It contained the essential
ideas, including the multipliers that we would now call dual prices. It was
published in the Soviet Union and went essentially unread in the West for well
over a decade.

**1947, Washington.** George Dantzig, working on planning problems for the US
Air Force, devised the simplex method. The word *programming* here has nothing
to do with computers: a *programme* was a schedule or plan of activities, and a
linear programme was one whose rules and objective were all linear.

Dantzig later wrote that he took the problem to John von Neumann, who on being
shown it stood at a blackboard and lectured him for over an hour on what turned
out to be duality theory, drawing on his work on games. It is a famous story
and it may well be exactly right, but the account is Dantzig's own recollection
and is not independently documented; treat it as such.

The recognition landed unevenly. In 1975 the Sveriges Riksbank Prize in
Economic Sciences went to Kantorovich and T. C. Koopmans for the theory of
optimal allocation of resources. Dantzig, whose method was by then running on
every serious computer in the world, was not among the recipients. He received
the National Medal of Science that same year.

> **In one sentence.** The region and its corners are consequences of the
> rules, not choices anybody made, and the question from 1947 onwards was what
> to do about them.

---

## 2 · Along the edge

![The five-sided region with a path drawn along its boundary. The path starts
at the origin, runs along the bottom edge, then turns twice, stopping at the
corner marked in green. Each corner along the way is labelled with what the
plan is worth.](chapters/02-along-the-edge/the-walk.gif)

![The same region and the same three-hop path shown as a still, with every
corner along the way labelled by the dollar value of the plan there: zero, then
320, then 340, then 350 at the final corner.](chapters/02-along-the-edge/the-walk.png)

The walk rests on a fact that has to be established before it makes any sense:
if a linear program has an optimum at all, then some corner achieves it.

The reason is that the objective is linear. Stand anywhere in the region that
is not a corner and there is a direction you can move in without leaving, and
along which the objective either improves or stays level. Keep going and you
run into a wall; slide along it and repeat. You cannot get stuck partway,
because a linear objective has no interior peak to get stuck on. Whatever the
best value is, a corner attains it.

That converts an infinite search into a finite one, and the simplex method is
what you get by taking the conversion seriously:

1. Stand at a corner.
2. Look along each edge leaving it. If one of them improves the objective,
   take it to the next corner.
3. If none does, stop. You are optimal.

Step 3 is the part that makes it a *method* rather than a search. When no
adjacent corner is better, no corner anywhere is better. The check is local
and the conclusion is global, and that is the whole of what duality buys you,
worked out in [the duality guide](../lp-duality/).

On the workshop, from a standing start:

| corner | plan | worth | what has run out |
|---|---|---|---|
| 0 | build nothing | $0 | nothing |
| 1 | 10⅔ tables | $320 | finishing |
| 2 | 10 tables, 2 chairs | $340 | finishing, planks |
| 3 | 9 tables, 4 chairs | **$350** | planks, bench time |

Three hops, out of five corners. At the last one every edge leads downhill, so
it stops.

> **In one sentence.** Simplex never guesses and never searches: it stands on a
> corner, improves along an edge, and knows it is finished when no edge
> improves.

---

## 3 · It should have been slow

![A logarithmic chart against the number of variables. One line, for the number
of corners a search would face, climbs steeply off the top of the chart. A band
near the bottom, for the number of hops solves are observed to take, stays
almost flat.](chapters/03-it-should-have-been-slow/the-count.png)

Here is the arithmetic that should have killed the method in its first week.

A corner is where enough rules run out at once: with *n* variables, pick *n* of
the rules and solve them as simultaneous equations. Every corner arises that
way, so counting corners is really counting the ways of choosing which rules
run out.

Take a problem with 30 variables and twice as many rules. A corner is then a
choice of 30 rules out of the 60 available, and the number of corners cannot
exceed the number of such choices: how many different committees of 30 you can
pick from 60 candidates. That count has a name and a notation, C(60, 30), read
aloud as "sixty choose thirty". At 30 variables it is about **1.18 × 10¹⁷**. A
hundred million billion, near enough.

Thirty variables is a toy. Real models have millions. If the walk had to see
any appreciable fraction of the corners, the method would be useless at any
size worth caring about.

It does not. In practice the number of hops tends to come out at a small
multiple of the number of *rules*, which is a number you can afford. That has
been the observed behaviour since the 1950s, on essentially everything anyone
has thrown at it. (The band drawn above is that rule of thumb, not a
measurement from this repository.)

So the method worked, spectacularly, and nobody could say why. Two questions
sat open:

- **Is there a bad case?** Some input on which the walk really does visit an
  exponential number of corners.
- **If bad cases exist, why does nobody ever meet one?**

The first was answered in 1972. The second took until 2004.

> **In one sentence.** The corner count says the walk should be impossible, and
> for twenty-five years the only evidence against that was that it kept
> working.

---

## 4 · Klee and Minty build a cube

![A three-dimensional cube drawn in perspective, slightly squashed so that its
faces are no longer square, with a path threading through every one of its
eight corners in turn before reaching the far one.](chapters/04-the-cube/cube.png)

Victor Klee and George Minty presented their answer at a 1969 symposium; it
appeared in print in 1972, under the title *How good is the simplex algorithm?*
The answer was: in the worst case, not good.

Their construction is a cube in *n* dimensions that has been squashed, so that
its faces tilt slightly instead of meeting at right angles. It has 2ⁿ corners,
exactly as a cube should. It is not degenerate, not badly scaled by any
standard anybody had, and not in any visible way a trick.

Run the walk on it with Dantzig's original rule, which enters the column that
improves the objective fastest per unit, and it visits **every single corner**
before it stops. This repository's simplex, in exact rational arithmetic,
confirms it: the cube in 10 dimensions has 1024 corners and takes **1023
pivots**. Exactly 2ⁿ − 1, at every size tested.

The squashing is what does it. The tilt makes the greedy rule prefer the
direction of fastest immediate improvement over the direction that would
actually get somewhere, at every corner, all the way around the cube. The rule
is not being stupid; it is being exactly as greedy as it was designed to be,
against a shape built to punish greed.

> **In one sentence.** The worst case is real, it is exponential, and it is not
> a pathological or degenerate input.

---

## 5 · The rule, not the method

![A logarithmic chart of pivot counts against cube dimension. One straight line
doubles with each dimension. A second straight line climbs more gently. A third
is flat at one pivot for every size.](chapters/05-not-the-rule/by-rule.png)

The cube proves less than it looks as though it proves.

The three lines above come from the same simplex code on the same cubes. One
function differs: which improving column to enter. That single substitution
moves the count from doubling, to a gentler climb, to a single pivot.

- **Dantzig's rule** takes exactly **2ⁿ − 1** pivots. Every corner.
- **Bland's rule**, which takes the lowest-numbered improving column, takes
  exactly **2·Fib(n+1) − 1**. At n = 10 that is 177 rather than 1023.
- **Steepest edge**, which measures improvement per unit of *movement* rather
  than per unit of variable, takes **one pivot**, at every size.

That middle formula needs unpacking, since it arrives out of nowhere. The
Fibonacci numbers are what you get by starting with 1 and 1 and making every
term the sum of the two before it: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, and on
up. Bland's count on the cube of dimension *n* is the term at position *n* + 1,
doubled, less one. At n = 10 the term is 89, so the count is 177.

Bland's rule deserves a moment, because it is easy to draw the wrong lesson
from it. Its guarantee is that it cannot cycle: it will always terminate. That
is a real and useful property, and it is why the other guides in this
repository use it. But look at the growth. 3, 5, 9, 15, 25, 41, 67, 109, 177.
Divide each of those by the one before it and watch the quotients. 5 over 3 is
one and two thirds; 9 over 5 is 1.8; 15 over 9 is back to one and two thirds.
They bounce about at first. Then they settle: by 109 over 67 they have almost
stopped moving, and 177 over 109 sits a whisker above 1.6 and is still edging
down. What they are closing in on is the golden ratio, about 1.618, which is
what ratios of consecutive Fibonacci numbers always do. So each extra dimension multiplies Bland's pivot count by
about 1.618, where Dantzig's rule multiplies by 2. It is still exponential,
just with a smaller base. Avis and Chvátal established this in 1978. **Not
cycling is not the same as being fast**, and the cube shows the difference
rather than merely asserting it.

Steepest edge escaping in one pivot is likewise not a proof of anything about
steepest edge. It means only that *this* cube was not built against *that*
rule. Deformed constructions have since been produced against essentially every
rule anyone has proposed, including randomised ones; Zadeh's rule held out
until 2022. **No pivot rule is known to be polynomial, and whether one exists
is open.**

The related geometric question is open too. The Hirsch conjecture asked whether
you always *could* get between two corners in few hops, whatever rule you used.
Klee and Walkup disposed of the unbounded case in 1967, and Francisco Santos
disproved the bounded version in 2012. The weaker polynomial Hirsch conjecture,
which asks only for a polynomial bound, remains unsettled.

Which leaves the question from chapter 3 wide open: bad cases exist for every
rule, so why does nobody meet one? The answer, from Daniel Spielman and
Shang-Hua Teng in 2004, is **smoothed analysis**. Take any input, including a
Klee-Minty cube, and jiggle it by a tiny random amount. The expected number of
pivots is then polynomial. The bad cases are real, but they are knife-edges:
perturb one and it stops being bad. Worst-case analysis had been asking a
question whose answer says very little about the inputs anybody actually has.

> **In one sentence.** The cube is an argument about a pivot rule, the bad
> cases survive for every rule anyone has tried, and they are nonetheless so
> fragile that a random nudge destroys them.

---

## 6 · Polynomial, and slower

![A sequence of increasingly elongated ellipses, each contained in the last,
tightening around a thin sliver of the workshop region near its best corner.](chapters/06-polynomial-and-slower/ellipsoids.gif)

In 1979 Leonid Khachiyan showed that linear programming is solvable in
polynomial time, using the ellipsoid method. This was genuine news. It made
newspapers outside mathematics, which is not a thing that happens to
algorithms.

The method ignores the region's shape completely. Wrap everything in an
ellipsoid and ask whether its centre is a legal plan. If it is not, then some
rule it breaks tells you the answer cannot be on that side, so throw that half
away and wrap the survivor in a new ellipsoid. Repeat. Each step shrinks the
volume by a guaranteed factor, so eventually the ellipsoid is smaller than any
region with room in it, and if you have not found a point by then there was
none.

The bound is honest and the method is dreadful. In two dimensions the
guaranteed shrink per step is exp(−1/4), about **0.779**: each cut is promised
to remove barely a fifth. This repository's implementation achieves **0.7698**
every single step, which is the smallest ellipsoid that can contain the
surviving half, and it never does better, because there is no mechanism by
which it could.

Ask it to find a plan worth at least $349 in the workshop and it takes **29
cuts**. The walk in chapter 2 reached the exact optimum of $350 in three hops.

Worse than merely slow, it is slow at a rate you can calculate in advance, and
the rate falls straight out of that 0.7698. One more decimal digit of accuracy
means pinning the answer down ten times more tightly than before. But the
ellipsoid does not shrink distances, it shrinks area, and area goes as the
square of distance, so pinning down ten times tighter costs a hundredfold cut
in area. The question is therefore how many multiplications by 0.7698 it takes
to reduce an area to a hundredth of itself. Ten of them leave about a
fourteenth, which is nowhere near enough. Another seven or so finish the job.
The count works out at **17.6 cuts per decimal digit**, and it stays 17.6
forever: the hundredth digit costs exactly what the first one did. And it never
produces an exact answer at all.

Polynomial is a statement about how the cost grows, not about how large it is,
and a method can be polynomial and still lose to an exponential one on every
instance anybody runs. Khachiyan's result reframed the theory of the subject
and changed nobody's software.

> **In one sentence.** The first polynomial method took its worst case on every
> input, which is exactly why its worst case was provable.

---

## 7 · Through the middle

![The workshop region with a smooth red curve running through its interior. The
curve begins at a marked point near the middle and bends towards the optimal
corner, with intermediate points labelled by decreasing values of mu, never
touching any wall.](chapters/07-through-the-middle/the-path.gif)

![The same central path drawn as a still, with the analytic centre marked at one
end, individual points labelled mu equals one thousand, ten and nought point
one along it, and the optimal corner marked at the
other.](chapters/07-through-the-middle/the-path.png)

In 1984 Narendra Karmarkar, at Bell Labs, published a polynomial method that
was also *fast*. That combination was new, and it restarted the argument.

The idea that ended up mattering most is not the projective transformation
Karmarkar originally used but the reformulation the field settled on shortly
after. Add to the objective a term that blows up at every wall.

One word first. The **slack** in a rule, for a particular plan, is how much of
that rule is still going spare. The workshop has 44 planks; a plan that
consumes 40 of them has 4 planks of slack. Every rule has its own slack, and so
does each of the two floors, since you cannot build a negative number of
chairs. Slack is positive everywhere inside the region and exactly zero on the
walls, which is what makes it the right thing to build a penalty out of.

So score a plan not by its profit but by this:

> **profit** + **μ** × (sum of the logs of the slack in each rule)

and hunt for the best score. The second term is the whole idea. A logarithm of
a number smaller than one is negative, and it has no floor at all: halve
the slack and the log drops by a fixed amount, halve it again and it drops by
that same amount again, and nothing ever stops it. Slack of a thousandth, a
millionth, a billionth, and the log is still marching downwards. A plan pressed
against a wall therefore scores minus infinity. Whatever plan wins is strictly
inside, with room left in every rule at once.

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

## 8 · What the barrier actually does

![Three side-by-side contour plots of the same region at decreasing values of
mu. In the first the contours form a broad bowl with its lowest point near the
middle. In the second the bowl has tilted and its minimum has slid towards the
best corner. In the third the contours are compressed against that corner.](chapters/08-what-the-barrier-does/the-landscape.png)

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

## 9 · A gap you can forecast

![A logarithmic chart with mu decreasing to the right. Two nearly parallel
straight lines descend together: an upper line for the guaranteed bound and a
lower one for the gap that actually remained.](chapters/09-a-gap-you-can-forecast/the-gap.png)

This is the property that decided real deployments, and it is not speed.

A point on the central path arrives with a receipt. The gap between what it is
worth and the best possible is at most **μ times the number of walls**. The
workshop has five walls (three rules and two floors), so the bound is 5μ:

| μ | plan | worth | promised within | actually within |
|---|---|---|---|---|
| 100 | 3.762, 4.053 | $193.92 | $500.00 | $156.08 |
| 10 | 8.408, 3.633 | $324.90 | $50.00 | $25.10 |
| 1 | 9.019, 3.870 | $347.96 | $5.00 | $2.04 |
| 0.1 | 9.004, 3.984 | $349.80 | $0.50 | $0.20 |
| 0.01 | 9.000, 3.998 | $349.98 | $0.05 | $0.02 |

Where does a bound like that come from? Two ingredients, one of which this
guide can show you and one of which it is going to quote.

The first is a fact about the path. Each wall pushes the plan away from itself,
and at a point on the central path the strength of that push is μ divided by
the slack in that rule: get twice as close and the wall shoves twice as hard.
That push is a price in exactly the sense of [the duality
guide](../lp-duality/): what one more unit of that resource would be worth. Now
multiply a wall's price by the slack left in that rule. The slack cancels, and
what remains is μ. Every wall, the same μ, exactly.

The second ingredient is the one being quoted rather than derived: duality says
that the amount a plan is leaving on the table is the sum, over the rules, of
each rule's price times the slack left in it. The duality guide builds that
sum, and at a true optimum every term in it is zero, which is why a resource
with something to spare is worth nothing. The central path is that same picture
with the zeros replaced by μ. Five walls, one μ apiece, and the total you might
still be missing is 5μ.

Divide μ by ten and you divide your remaining ignorance by ten. Before running
anything, you can say how many more rounds buy how many more digits.

Simplex offers nothing comparable. Standing at a corner, you know what you have
and you know it is not yet optimal, but the number of hops left is not a
quantity you can ask about. Every corner looks like the ones before it right up
until the last one. That is fine when the solve takes a second. It is a
different matter when it takes six hours on a model due at 6am, and it is the
reason interior point methods took over the very large end of the market rather
than the whole of it.

> **In one sentence.** The barrier tells you how far from optimal you are while
> you are still running; the walk can only tell you once it has stopped.

---

## 10 · Neither one won

![Two side-by-side plots of the same corner at scales differing by a hundred.
In each, a red curve approaches from below and stops just short of the corner
with a blue arrow bridging the remaining distance. The two pictures are
indistinguishable.](chapters/10-neither-one-won/crossover.png)

Both panels show the same corner. The right one is drawn a hundred times
larger, with the repulsion turned down a hundredfold, and the point lands
exactly 100 times closer. The picture does not change. Zooming in and
tightening the tolerance move together, so **there is no setting at which the
point becomes a corner**. It never lands.

Often that does not matter. Sometimes it matters a great deal:

- Reading off *which rules are binding*, which is what a shadow price is
  attached to, needs an actual corner. Nearly-tight is not tight.
- Warm starting. Change one number in the model and a simplex basis usually
  re-optimises in a few pivots. An interior point solve mostly starts again,
  which is why branch-and-bound trees, where thousands of nearly-identical LPs
  are solved in sequence, still run on simplex.
- Anything downstream that wants a vertex, including most of what
  [branch and price](../branch-and-price/) does.

So a modern barrier solve usually ends with **crossover**: hand the interior
point to a simplex-style routine and let it walk the short distance to a real
corner. The two methods are not competitors in the same program. They are
stages of it.

The rough division of labour today:

| | tends to win on |
|---|---|
| **simplex** | small and medium models, warm starts, anything inside a search tree, when you need a basis |
| **interior point** | very large and sparse models, first solves from cold, when you want a forecastable stopping point |
| **crossover** | whenever the second one is faster but the answer has to be a corner |

And the theoretical question underneath all of it is still open. Nobody knows
whether a pivot rule exists that makes simplex polynomial. Nobody knows whether
a *strongly* polynomial algorithm for linear programming exists at all: one
whose step count depends only on the number of rules and variables, not on how
many digits the numbers have. That is the ninth of Smale's problems for the
21st century, and it is unsolved.

Two methods, seventy-odd years, and the argument is not finished.

> **In one sentence.** The walk and the path solve different halves of the same
> job, which is why every serious solver contains both and finishes with the
> first one.

---

## What the plain words are really called

| this guide says | everyone else says |
|---|---|
| the region of legal plans | the **feasible region**, a polyhedron |
| a corner | a **vertex**, or a **basic feasible solution** |
| which column to enter | the **pivot rule** or pricing rule |
| improvement per unit of movement | the **steepest edge** rule |
| the squashed cube | the **Klee-Minty** cube |
| jiggle the input and re-ask | **smoothed analysis** |
| the repulsion strength μ | the **barrier parameter** |
| the curve of minima | the **central path** |
| the point furthest from every wall | the **analytic centre** |
| the receipt a path point carries | the **duality gap** |
| walking the last bit to a corner | **crossover** |

## Running the code

```bash
make bootstrap    # once, from the repository root
cd corners-vs-centre && make verify
```

The simplex here is exact rational arithmetic with a pluggable pivot rule, so a
step count is a step count and not an artefact of rounding near a degenerate
corner. The barrier and ellipsoid routines are floating point, as they must be,
and every claim made about them is checked against the exact optimum the
simplex returns. The two closed forms in chapter 5 are asserted against the
formulas, not against stored numbers, at every dimension up to 12.
