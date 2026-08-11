<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · The same test, from the other side

There is a second way to say all of that, and it is worth carrying both, because
each one makes a different thing obvious.

Duality puts a rule on what a price list is allowed to be. Prices are legal only
when no board anywhere can be cut into pieces worth more than the board costs. A
list that fails that test is promising value out of nowhere, and a price list
that promises value out of nowhere can be used to argue for anything.

The rule has a name, **dual feasibility**, and the thing to notice is its shape:
it is one condition per pattern. One for each way of cutting a board. All four
trillion of them.

The prices from chapter 6 pass that test for every pattern in the restricted
master. Solving that model is what forced them to. What is *open* is every
pattern left out of it, because a price list has no way of knowing which
patterns exist — it is a list of numbers, one per length, and nothing in it
records what it has never been shown.

So there are two cases, and they are the two halves of the method.

**If the prices pass for the unwritten patterns too**, the list is legal for the
full model. Then the duality guide's check applies exactly as written: a plan
and a price list that agree end the search. The number the restricted master
reported is the full model's number, proved without the full model ever being
built.

**If some unwritten pattern fails**, the prices were only legal because that
pattern was missing. Writing it down is precisely what will force them to move.

Which is why the two framings are one search. Hunting for a pattern worth more
than a board, and hunting for a broken dual condition, are the same hunt seen
from opposite sides — and the next chapter is how you run it without a list.

> **In one sentence.** A price list cannot tell which patterns it has never been
> shown, so the whole method is the search for one that would embarrass it.

---

Chapter 7 of 11

Previous: [What the prices are telling you](../06-what-the-prices-say/README.md)  
Next: [Asking for a pattern is a knapsack](../08-a-knapsack/README.md)  
Contents: [branch-and-price](../../README.md)
