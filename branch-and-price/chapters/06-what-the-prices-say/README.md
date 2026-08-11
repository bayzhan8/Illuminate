<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 6 · What the prices are telling you

Solve the restricted master and it hands back more than a number. It hands back
**prices**, one per ordered length.

A price answers one specific question. Suppose the customer rang up and asked
for one more 9-foot piece: how much extra cutting would that cost, in boards?
That number is the price of a 9-foot piece. The duality guide is where these
come from and why one exists for every ordered length at once. At the first
round they come out as

| length | price |
|---|---|
| 4 ft | 1/6 |
| 9 ft | 1/2 |
| 10 ft | 1/2 |

Each one is readable straight off the lazy pattern that supplies it. The only
source of 4-foot pieces here is a board cut into six, so one more of them costs
a sixth of a board. The only source of 9-foot pieces is a board cut into two, so
one more costs half a board. The 10s the same, for the same reason.

Be clear about what these are. They are not the prices of the real problem. They
are what this impoverished three-pattern model currently believes, and they will
move as better patterns arrive.

Now the move the whole method rests on. Take *any* pattern, written down or not.

Cutting a board with it costs one board. The pieces that come off it are worth,
at these prices, some amount. So the pattern is worth adding exactly when

> the pieces it yields are worth **more than one board.**

Check it on the three patterns the model already holds. Six 4-foot pieces at 1/6
each: worth exactly 1. Two 9s at 1/2 each: exactly 1. Two 10s at 1/2: exactly 1.
Three sums, all landing on 1, and none of them a help.

That is not a coincidence and it is worth seeing why: a pattern the model is
already leaning on *cannot* be worth more than the board it eats, or the prices
would not have come out of that model in the first place. Solving forced them to
be consistent with everything on the table.

One board in, pieces worth some amount out. The difference between the two is
what everyone else calls the pattern's **reduced cost**: below zero when the
pieces beat the board, which is when the pattern is worth having, and zero for
the three just checked.

What the name buys you is small compared with what the comparison buys you. It
uses the prices and the pattern's own contents, and nothing else. No solve, no
model, no list. Which means a pattern nobody has ever written down can still be
judged by it — and that is the crack the rest of the method goes through.

> **In one sentence.** A pattern is worth adding when its pieces are worth more
> than a board, a test that needs only the prices and the pattern itself.

---

Chapter 6 of 11

Previous: [Start with a few](../05-start-with-a-few/README.md)  
Next: [The same test, from the other side](../07-the-same-from-the-dual/README.md)  
Contents: [branch-and-price](../../README.md)
