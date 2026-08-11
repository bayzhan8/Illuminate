<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · Every honest price list is a ceiling

That claim is the load-bearing step, so it deserves to be seen rather than
asserted. It is also two ideas rather than one, and separating them is what
makes it obvious.

Take any plan; it does not have to be a good one. Take any price list that
covers both products. Line up three numbers.

![Three bars. What the plan earns, three hundred and forty dollars. What those
prices charge for the ingredients the plan uses, three hundred and eighty six.
What those prices charge for everything in the building, three hundred and
ninety eight.](chain.png)

The plan builds 10 tables and 2 chairs, earning **$340**. The prices are $7 a
plank, $3 an hour, nothing for saw time. Then:

- **$340 ≤ $386**, because every product is priced at least what it earns, so
  the ingredients a plan eats are worth at least what the plan makes.
- **$386 ≤ $398**, because a plan cannot use more of anything than there is.

So $340 ≤ $398.

Now notice what the argument never used: that this was a *good* plan, or that
these were *cheap* prices. It holds for every plan and every covering price
list simultaneously.

That is the payoff. Find a plan worth $350 and a price list charging $350, and
no plan can beat $350 while you are holding one that reaches it. You are
finished, you know you are finished, and you never examined a second plan.

*(The standard name for this is **weak duality**. You can forget the name; the
two bullets above are the whole content.)*

> **In one sentence.** Any honest price list is a ceiling over every possible
> plan at once, which is why a matching plan and price list end the search.

---

Chapter 4 of 10

Previous: [Charging for the ingredients](../03-mixing-the-rules/README.md)  
Next: [The gap closes, every time](../05-the-gap-closes/README.md)  
Contents: [lp-duality](../../README.md)
