<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 5 · Start with a few, and let the prices ask for more

Start with a model that is obviously too small.

Take a few patterns — say the lazy ones, each board cut into copies of a single
length — and solve *that*. This is the **restricted master**: the real model,
restricted to the columns someone has bothered to write down.

Our order has three lazy patterns: a board cut into six 4-foot pieces, a board
cut into two 9s, a board cut into two 10s. With only those three on the table
there is nothing to decide, because each ordered length has exactly one source.
Three 4-foot pieces, six to a board, is half a board of cutting. Six 9-foot
pieces, two to a board, is three boards. Seven 10-foot pieces, two to a board,
is three and a half. Add them up: 7 boards, which answers a smaller question
than the one we asked.

That is an honest upper bound, since those patterns really do fill the order.
It is not the answer to the strong model, which has three more patterns nobody
has written down. Whether any of them would help, answered without adding them,
is the whole method.

Solve the restricted master and read off its **prices**, one per ordered
length. A price answers one specific question. Suppose the customer rang up and
asked for one more 9-foot piece: how much extra cutting would that cost, in
boards? That number is the price of a 9-foot piece. The duality guide is where
these come from and why they exist for every ordered length at once. At the
first round they come out as

| length | price |
|---|---|
| 4 ft | 1/6 |
| 9 ft | 1/2 |
| 10 ft | 1/2 |

Each one is readable straight off the lazy pattern that supplies it. The only
source of 4-foot pieces here is a board cut into six, so one more of them costs
a sixth of a board. The only source of 9-foot pieces is a board cut into two,
so one more costs half a board. The 10s the same, for the same reason. These
are not the prices of the real problem. They are what this impoverished
three-pattern model currently believes, and they will move as better patterns
arrive.

Now take *any* pattern, written down or not.

Cutting a board with it costs one board. The pieces that come off it are worth,
at these prices, some amount. So the pattern is worth adding exactly when

> the pieces it yields are worth **more than one board.**

Try it on the three patterns the model already holds. Six 4-foot pieces at 1/6
each: worth exactly 1. Two 9s at 1/2 each: exactly 1. Two 10s: exactly 1. Not a
surprise and not a help. A pattern the model is already leaning on cannot be
worth more than the board it eats, or the prices would not have come out of
that model in the first place.

One board in, pieces worth some amount out. The difference between the two is
what everyone else calls the pattern's **reduced cost**: below zero when the
pieces beat the board, which is when the pattern is worth having, and zero for
the three just checked. What the name buys you is small compared with what the
comparison buys you: it uses the prices and the pattern's own contents and
nothing else, so a pattern nobody has written down can still be judged by it.

There is a second way to say all of this, and it is worth carrying both.

Duality puts a rule on what a price list is allowed to be. Prices are legal
only when no board anywhere can be cut into pieces worth more than the board
costs. A list that fails that test is promising value out of nowhere, and it
can be used to argue for anything. The rule has a name, **dual feasibility**,
and it is one condition per pattern: one for each way of cutting a board.

The prices we just read off pass the test for every pattern in the restricted
master. Solving that model is what forced them to. What is open is the patterns
left out of it, because a price list has no way of knowing which patterns
exist. If it passes for those too, it is legal for the full model, and then the
duality guide's check applies: the number the restricted master reported is the
full model's number, proved without the full model ever being built.

If some unwritten pattern fails the test, the prices were only legal because
that pattern was missing. Writing it down is exactly what will force them to
move. Hunting for a pattern worth more than a board and hunting for a broken
dual condition are one search, seen from the two sides.

> **In one sentence.** The prices from a small model can judge a pattern that
> model has never seen, which turns "is anything missing" into arithmetic.

---

Chapter 5 of 9

Previous: [Too many to write down](../04-too-many-to-write-down/README.md)  
Next: [Asking for a pattern is a knapsack](../06-a-knapsack/README.md)  
Contents: [branch-and-price](../../README.md)
