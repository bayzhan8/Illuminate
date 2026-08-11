<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · One variable per pattern

So model the decision differently. Instead of *which pieces go on which board*,
decide **how many boards to cut with each pattern.**

Every pattern is a way of cutting a board that is already legal: the pieces fit,
by construction. So the model has nothing left to say about fitting. It only
has to say that enough pieces come out:

> **choose** how many boards to cut with each pattern, to **minimise** the
> total number of boards, so that for each length, the pieces produced across
> all patterns **cover the order**.

Relax *that*, allowing a fractional number of boards cut with a pattern, and
the answer is **6.5 boards.**

Where does the half come from? Look back at the six patterns drawn in chapter 1
and take two of them. Cut six boards into a 4, a 9 and a 10, which uses 23 of
the 25 feet available. Then cut half a board into a 4 and two 10s, the one
pattern on that page that gets two 10-foot pieces out of a single board.

Count what comes out. Nine-foot pieces: one from each of the six boards, so
six, and six were ordered. Ten-foot pieces: six from those boards, and a half
board that would have given two gives one, so seven, and seven were ordered.
Four-foot pieces: six and a half of them where three were ordered, so three and
a half are surplus and go in the bin. Every order is met, and the boards used
add up to 6 + 1/2.

Nothing does better, and you can see why without solving anything. Call a piece
*long* if it is 9 feet or 10. Three long pieces never fit on one board, since
the three shortest are 9 + 9 + 9 = 27 feet and a board is 25. So a board
carries at most two of them however it is cut, which the six drawings bear out.
Cutting half a board with a pattern yields half of each of its pieces, so that
ceiling survives the relaxation: two long pieces per board of cutting, whole
boards or not.

The order wants 6 nines and 7 tens. Thirteen long pieces at two to a board
needs 13/2 boards, and 13/2 is 6.5. The mix above sits exactly on that ceiling,
which is why it cannot be beaten.

Two relaxations of the same order, an enormous distance apart. Integrality was
not discarded this time. It was absorbed into the variables: every pattern
is a whole-board decision already made correctly, so relaxing the *count* of
patterns cannot un-decide it. What remains to relax does far less harm.

| | says you need at least | so, at least | true answer |
|---|---|---|---|
| the obvious model, relaxed | 5.44 boards | 6 | 7 |
| one variable per pattern, relaxed | **6.5 boards** | **7** | 7 |

Here the second relaxation settles the question by itself, which is the reason
to put up with everything that follows.

*(The standard name for this reformulation is **Dantzig–Wolfe decomposition**.
Chapter 9 comes back to it; for now the idea is all you need.)*

> **In one sentence.** Deciding in whole patterns rather than in individual
> pieces absorbs the integrality, so relaxing what is left costs much less.

---

Chapter 3 of 9

Previous: [The obvious model, and why it is too weak](../02-the-obvious-model/README.md)  
Next: [Too many to write down](../04-too-many-to-write-down/README.md)  
Contents: [branch-and-price](../../README.md)
