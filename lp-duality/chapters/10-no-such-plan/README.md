<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · A plan that cannot exist

The second failure is the more interesting one, because of *how* it gets
settled.

![A scale of tables showing that the planks reach eleven and the order starts at
twelve, with nothing in between.](no-such-plan.png)

Suppose an order arrives for 12 tables.
Forty-four planks make eleven tables, so the order cannot be met. Nothing about
that is surprising. What is worth watching is that it gets settled by
arithmetic you can do on the back of an envelope, rather than by a search that
eventually gives up.

Two rules do all the work here. Written out flat, with no symbols:

> **The plank rule.** Each table takes 4 planks and each chair takes 2, and
> there are 44 planks in the building. So four times the number of tables, plus
> twice the number of chairs, comes to 44 at most.
>
> **The order.** The number of tables must be 12 or more.

Now take a quarter of the plank rule. Cutting every number in it to a quarter
of itself leaves it just as true, so four times the tables becomes plain
tables, twice the chairs becomes half the chairs, and 44 becomes 11.

> **A quarter of the plank rule.** The number of tables, plus half the number
> of chairs, comes to 11 at most.

Hold that against the order. Tables plus half the chairs come to 11 at most,
while the tables on their own are already 12 or more. Take the tables away from
both of those. What is left on one side is half the chairs, and what is left on
the other is 11 minus 12:

> **half of the chairs, at most −1.**

Chairs get counted, and counts do not go below zero. Even building no chairs at
all gives 0, and 0 is bigger than −1. So the two rules describe no pair of
numbers whatsoever, and there is no plan to find. That is short enough to check
in a minute, and it settles the question for every plan at once, forever.

Look again at what that proof was made of: a quarter of one rule, plus all of
another, added together. A weighted mixture of the rules, exactly like the
price lists of chapter 3, except that this mixture lands on something absurd
instead of on a ceiling. It is called a **Farkas certificate**, and the fact
that one always exists when a system is impossible is the fact strong duality
is built on.

One footnote to chapter 8 before leaving the subject, because it is the way
this bites people in practice. At a bend in that curve the price is not
unique. Standing exactly at 45 ⅐ planks, one more plank is
worth nothing and one fewer costs $6.25, and both numbers are legitimate
prices. A solver will hand you one of them without mentioning the other. This
is called **degeneracy**, and it is why a sensitivity report should be read as
a range and never as a point.

> **In one sentence.** Impossibility always has a short arithmetic proof, built
> by mixing the rules exactly the way a price list mixes them.

---

Chapter 10 of 11

Previous: [Profit that runs away](../09-profit-runs-away/README.md)  
Next: [Where this leads](../11-where-this-leads/README.md)  
Contents: [lp-duality](../../README.md)
