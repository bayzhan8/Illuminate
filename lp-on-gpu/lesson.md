# The machine got wider, not faster

**Why linear programming had to change algorithms to use a GPU.**

For thirty years the way to solve a linear program faster was to buy a quicker
processor. That stopped working, and what replaced it was not a quicker
processor but a much wider one: thousands of arithmetic units, fed by a memory
system that did not get thousands of times faster.

The simplex method cannot use a machine like that. Not because nobody has
tried, but because of what it *is*: a chain of decisions where each one depends
on the last.

So the interesting question is not how to parallelise simplex. It is what a
method would have to look like to use the hardware at all, and what you give up
by using it.

**The plan.** Chapter 1 is about the hardware and why it changes which
algorithms are worth having. Chapter 2 is why simplex is the wrong shape.
Chapters 3 to 7 build a method that is the right shape, starting from the
version that does not work. Chapters 8 and 9 are whether it gets the right
answer and what it costs.

Every number below is computed by the code in this folder. The answers it is
checked against come from the exact rational simplex in
[the duality guide](../lp-duality/), which shares no line of code with anything
here.

---

## 0 · What this is

![Two curves against iteration count on the same workshop. One oscillates
violently between zero and eight hundred without ever settling. The other rises
smoothly and stops on three hundred and fifty.](chapters/00-what-this-is/hero.gif)

Two methods, on the same small problem, with the same step sizes. They differ
by one term in one line.

The red one never settles. It is still swinging between $0 and $753 after four
thousand iterations, and it will do that forever.

The blue one stops on $350, which happens to be exactly right.

That single term is most of this guide.

> **In one sentence.** A method that can use parallel hardware is available,
> but only just, and the difference between it working and not is very small.

---

## 1 · Wider, not faster

Start with the hardware, because it determines which algorithms are worth
having.

A modern accelerator has enormously more arithmetic capability than a server
processor. It does not have proportionally more memory bandwidth. Roughly: a
hundred times the arithmetic, but only about fifteen times the rate at which it
can fetch numbers to do arithmetic *on*.

That matters only if you know how much arithmetic your work does per byte it
reads. So count it.

Multiplying a sparse matrix by a vector, the way solvers store matrices, costs
about **12 bytes per stored entry**: eight for the value and four to record
which column it sits in. And it performs **2 operations**: one multiply, one
add.

Two operations per twelve bytes. **0.17 operations per byte.**

Now put that against the machines.

![A log-log chart of achievable rate against arithmetic intensity, with a
ceiling line for each of two machines. At the intensity of a sparse
matrix-vector product, one machine reaches nine percent of its arithmetic and
the other one point three percent, while their absolute rates differ by the
ratio of their bandwidths.](chapters/01-wider-not-faster/roofline.png)

The accelerator can perform **13 operations for every byte** it delivers. Give
it work that asks for 0.17 and almost all of that arithmetic sits idle: it
reaches **1.3%** of what it could do. The server processor, which can perform
1.9 operations per byte, reaches **9%** of its own.

And yet the accelerator is still the faster machine here, by **14.5×**, which
is precisely the ratio of their *bandwidths*, not the ratio of their
arithmetic, which is about a hundred.

That is the sentence to carry forward. For this kind of work, buying a machine
with more arithmetic buys you nothing. Buying one with more bandwidth buys you
exactly what it says.

Which tells you what a good algorithm looks like: one whose entire inner loop
is streaming over the matrix, and which does no other kind of work at all.

> **In one sentence.** Sparse matrix work is limited by memory bandwidth, not
> arithmetic, so the only speedup available is the bandwidth ratio.

---

## 2 · Why simplex is the wrong shape

The simplex method walks from corner to corner of the feasible region, and each
step is a chain:

1. Work out which product would improve the plan if you started making it.
2. Work out how much of it you can make before some rule binds.
3. Update the plan, and update the bookkeeping that made step 1 answerable.

You cannot start step 1 of the next iteration until step 3 of this one has
finished, because step 3 is what changes the answer to step 1. The dependency
is not incidental to the implementation; it *is* the method. Each corner is
chosen using the information produced at the previous corner.

There is a second problem underneath. The bookkeeping in step 3 is a
factorisation of the current basis, maintained incrementally, and solving with
it is a triangular solve: a sequence of substitutions where each one needs the
previous result. Sparse triangular solves have very little parallelism in them
by construction.

None of this makes simplex a bad method. It is an extremely good method, and on
most problems it is still the one to use. It is simply the wrong shape for a
machine whose advantage is doing ten thousand independent things at once.

*(The natural follow-up, why interior point methods are a different shape
again and where each one wins, is its own guide and is coming.)*

> **In one sentence.** Simplex is a chain of dependent decisions, so its speed
> comes from taking few steps rather than from taking them in parallel.

---

## 3 · A method made of one operation

So ask for the opposite. What would a method look like if the *only* thing it
ever did was multiply by the matrix?

Here is the setup. The workshop from the duality guide: three shelves, two
products, and the question of what to build. Written for a machine, it is

> choose a plan `x`, at least zero in every entry,
> so that `Ax` stays under the shelf limits `b`,
> making the profit as large as possible.

The duality guide's second idea gives the other half. Attach a price to each
shelf, collect them in `y`, and consider

> `L(x, y)` = what the plan costs, plus the prices times how much the plan
> overruns each shelf.

The plan wants this small. The prices want it large: if a shelf is overrun,
raising its price punishes the plan for it. The answer is the standstill where
neither side can improve by moving: the plan is the best one, and the prices
are the shadow prices of chapter 7 over there.

Now the point. To move the plan you need `A` transposed times `y`. To move the
prices you need `A` times `x`. And then you clamp anything that went negative
back to zero.

That is the whole vocabulary. Two matrix-vector products, some vector
addition, and a clamp. **No factorisation, no basis, no pivoting, no ordering,
nothing sequential.**

It is exactly the shape chapter 1 asked for. The only question left is whether
it works.

> **In one sentence.** Treating the plan and the prices as two players lets you
> build a method out of nothing but matrix-vector products.

---

## 4 · The obvious version does not work

The obvious thing is to move both at once. Push the plan down a little, push
the prices up a little, repeat.

To see what happens, shrink the problem until the whole state fits on a page:
one variable, one rule, `x = 3`. Then the state is a plan and a price, two
numbers, and the path they trace is a curve in a plane.

![A trajectory in the plane of plan against price, starting near the answer and
winding steadily outward in a widening spiral.](chapters/04-the-obvious-version/outward.png)

It winds outward. It starts 2.2 away from the answer and after 90 steps it is
13.1 away, and it keeps going.

The reason is visible in the update itself. The prices are told to react to the
plan `x`. But by the time they react, the plan has already moved on, so each
side is always responding to where the other one just *was*. Two players who are
each a step behind the other will circle each other forever, and the circling
grows.

On the real workshop the failure looks different but is no better. There the
clamp at zero keeps the numbers from running away, and instead the method
settles into an exact **repeating cycle of period 10**: the plan climbs to
about 17 tables, the prices spike, the plan is slammed to nothing, the prices
decay, and it begins again. The value it reports swings between **$0 and
$753**, and it never once sits at $350.

It does not diverge. It does not converge. It just keeps going.

> **In one sentence.** Two players each reacting to the other's previous move
> circle forever instead of settling.

---

## 5 · One term different

Here is the fix, and it is almost nothing.

When the prices react, do not show them the plan's current position. Show them
where the plan is *heading*: the new plan, plus the step it has just taken,
again.

If the plan moved from `x` to `x′`, the prices are shown `2x′ − x`. That is the
cheapest imaginable guess at the next position: assume it keeps going the way
it was going.

![The same trajectory in the same plane, now winding inward toward the answer
in a tightening spiral.](chapters/05-one-term-different/inward.png)

Same problem, same step sizes, same starting point, one changed term. The
spiral reverses. After 90 steps it is 0.36 away instead of 13.1.

Side by side, from the same start, it is not a subtle difference:

![Two planes side by side, each tracing a path from the same starting point.
On the left the path winds outward and leaves the frame. On the right it winds
inward and settles on the answer.](chapters/05-one-term-different/spiral.gif)

This is the **primal-dual hybrid gradient** method, and it is the algorithm
underneath the first-order LP solvers that run on GPUs.

Its per-iteration cost is unchanged: still two matrix-vector products, still no
factorisation. It has not become a more expensive method. It has become a
convergent one.

> **In one sentence.** Letting the prices anticipate the plan's next move
> rather than react to its last one turns the spiral inward, at no extra cost.

---

## 6 · It turns fast and shrinks slowly

The spiral converges. The trouble is how.

On the small problem the iteration is exactly a linear map, so it can be taken
apart completely. Its eigenvalues are a conjugate pair, and a conjugate pair
means the step is a rotation combined with a shrink. Both have closed forms.
With a step size of 0.2:

- it turns **11.5°** per iteration, so a full revolution takes **31.2** steps
- it shrinks the distance to the answer by **2.0%** per iteration

Those two numbers are the whole difficulty. It is spinning quickly and closing
in barely at all.

And you cannot fix it by taking bigger steps, because the two are locked
together.

![Two curves against step size on shared axes: degrees turned per iteration
rising steeply, and percent closer per iteration rising with
it.](chapters/06-fast-turn-slow-shrink/anatomy.png)

Raising the step size does make it contract faster. It also makes it rotate
faster, and past a threshold the method stops converging at all. The setting
that keeps it stable is the setting that makes it crawl.

So most of the work is going into going round, and only a sliver into going in.

> **In one sentence.** The iteration rotates far more than it contracts, and
> the step size cannot fix that because it drives both.

---

## 7 · Cancel the rotation

If the problem is rotation, remove the rotation.

Averaging is the tool. Average the iterates over a full revolution and the
turning cancels, because points on opposite sides of the circle pull in
opposite directions, while the inward drift does not. Then throw away the state, start
again from the average, and do it once more.

![Two convergence curves on a logarithmic scale, one decaying slowly and the
other dropping by six orders of magnitude over the same number of
iterations.](chapters/07-cancel-the-rotation/restarts.png)

Same iteration. Same two matrix products per step. Same step sizes. Restarting
every 40 iterations leaves it, after 600 iterations, about **a million times**
closer to the answer.

Nothing was added to the inner loop. The averaging is vector work, invisible
next to the matrix products. It is very close to a free improvement of six
orders of magnitude, and it is why practical first-order LP solvers all restart.

*(Real solvers choose the restart moment adaptively rather than on a fixed
schedule, and there are stronger variants than plain averaging. The mechanism
is the one above.)*

> **In one sentence.** Averaging over a revolution cancels the rotation and
> keeps the drift, which costs nothing and is worth orders of magnitude.

---

## 8 · Does it get the right answer?

It should be checked against something that cannot be wrong.

The duality guide solved this workshop in exact rational arithmetic with a
simplex method: **9 tables and 4 chairs, worth $350**, with shadow prices of
**$6.25** a plank, **$2.50** an hour and **nothing** for saw time.

![A logarithmic convergence curve falling from tens to below ten to the
fifteenth over about a thousand iterations.](chapters/08-the-same-answer/agree.png)

The first-order method finds the same plan, to fifteen decimal places.

It also finds the same prices. That is worth pausing on, because it is not an
extra: the prices are half of what the method is, so it produces the shadow
prices without being asked. The duality guide's second problem is not something
this method solves afterwards. It is the thing it was solving all along.

> **In one sentence.** It converges to the same plan and the same shadow prices
> as the exact method, because the prices were half the algorithm.

---

## 9 · What it costs

Two costs, and they are the reason this has not replaced anything.

![Two panels. On the left, the worst rule violation falling from about a plank
to zero over a few thousand iterations, against a line marking that every
simplex iterate is exactly legal. On the right, a tied optimum where the exact
method returns a corner and the first-order method returns the
midpoint.](chapters/09-what-it-costs/cost.png)

**The plan is not legal until it has converged.** A simplex iterate is always
standing on a corner of the feasible region, so it is a plan you could actually
carry out at every step. A first-order iterate approaches feasibility from
*outside*. Ten iterations in, this one proposes a plan overrunning a shelf by
0.84 planks and claims to be worth **$352.44**, more than the true optimum,
because it is cheating.

That is not a rounding error, it is a category difference. Stopping early gives
you a number that is not an answer to your question.

**And it does not return a corner.** Take a problem where a whole edge is
optimal, every point on it equally good. The exact method returns one of the
two corners. The first-order method returns the middle.

Both are optimal, so for reporting a number it makes no difference. But branch
and bound needs a corner: it needs a *basis* to warm-start the next node from,
and a point in the middle of an edge does not give it one. Which is why
first-order methods have transformed how very large linear programs get solved,
and have so far changed integer programming much less.

> **In one sentence.** You trade a legal answer at every step, and a corner at
> the end, for an inner loop that a wide machine can actually feed.

---

## 10 · Where this leaves things

The honest summary is narrow and worth stating precisely.

For linear programs large enough that forming and storing a factorisation is
the binding constraint, a method whose entire inner loop is matrix-vector
products is a genuinely different proposition, and hardware built for bandwidth
suits it. That is a real and important class of problem, and it was previously
not solvable at all.

For everything else, the established methods remain established for good
reasons: problems where a factorisation fits comfortably, problems needing
high accuracy, problems that are really integer programs wanting a basis at
every node. The chapters above are most of those reasons.

What has actually changed is that the answer to "which algorithm" now depends
on the machine, in a way it did not for thirty years.

The specific benchmark numbers in this area move quickly and I have not quoted
any, because a guide that dates in six months is worse than one that does not
try. The primary sources, if you want the current state: the PDLP paper by
Applegate and co-authors, the cuPDLP line of work, and Mittelmann's benchmark
pages, which are updated continuously.

---

## What the plain words are really called

| this guide says | everyone else says |
|---|---|
| operations per byte fetched | arithmetic intensity |
| the chart of what a machine can reach | a **roofline** model |
| a method made only of matrix products | a **first-order** method |
| the plan and the prices as two players | the **saddle point** / Lagrangian formulation |
| showing the prices where the plan is heading | extrapolation |
| the method of chapter 5 | **PDHG**, primal-dual hybrid gradient |
| the LP solver built on it | **PDLP** |
| average and start again | **restarting** |
| a plan that breaks a rule | primal infeasibility |
| a corner of the region | a **basic** solution |

## Running the code

```bash
make bootstrap    # once, from the repository root
cd lp-on-gpu && make verify
```

There is no GPU in this repository and none is needed. Everything here is about
the *shape* of the iteration, which is what determines whether a wide machine
can be used at all, and that is visible at three variables as clearly as at
three million. The tests check every claim above against the exact rational
solver from the duality guide.
