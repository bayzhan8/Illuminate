<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · Charging for the ingredients

The ceiling comes from the other side of the ledger.

Stop building things. Instead put a price on each of the three things in stock:
so much per plank, so much per hour of work, so much per hour of saw time. Any
prices you like, as long as none is negative.

Those prices imply a price for a table, because a table *is* 4 planks, 2 hours
and 3 of saw time. Try $7 a plank, $3 an hour, nothing for the saw. Then a
table's ingredients are worth 4×7 + 2×3 = $34, and a chair's are worth
2×7 + 3×3 = $23.

Now notice something. A table sells for $30 and its ingredients are priced at
$34. A chair sells for $20 and its ingredients are priced at $23. At these
prices, both products are worth more as raw material than as furniture.

Suppose that is true of every product. Then take *any* plan the workshop might
carry out and follow it through two steps.

**Step one.** Whatever the plan builds, the ingredients it consumes are worth
at least what the finished goods sell for. That is true product by product, and
a plan is nothing but a number of each, so adding up preserves it.

**Step two.** The ingredients it consumes came out of the building, so they are
worth at most what is in the building — you cannot use more planks than you own,
and no price is negative.

Chain those together. What the plan earns is at most what its ingredients are
worth, and what its ingredients are worth is at most the value of everything on
the shelves. So the plan earns at most the value of everything on the shelves.

And notice what the argument never asked. It never asked which plan. It holds
for the best plan, the worst plan and every plan in between, all at once. So
the value of the building at these prices is a number *no plan can beat*.

That is a ceiling, and it came from prices rather than from plans.

The condition it needs is the one we just checked:

> **every product is priced at least as high as it sells for**

Both halves of that matter, and the animation exists to make the failure
concrete.

![Two panels. On the left, bars showing what the current prices charge for one
table and one chair, each against a line showing what that product earns. On
the right, the ceiling those prices prove, falling as the prices
change.](mixing.gif)

Watch the left panel first. Raising the plank price alone covers tables long
before it covers chairs. While either bar is short, the prices prove nothing
whatever. A price list that covers one product and not the other proves no
upper limit at all, which makes it worth exactly as much as no price list.

Then watch what happens once both are covered. There is room to trade a lower
plank price for a higher hourly rate, stay legal the whole way, and bring the
ceiling down.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/03.html)**
Set the three prices by hand and find out how low you can push the ceiling
before one of the products slips under its price.

> **In one sentence.** A price list that covers every product proves an upper
> limit on what the workshop can earn, without reference to any plan.

---

Chapter 3 of 11

Previous: [A good plan cannot prove itself best](../02-no-way-to-check/README.md)  
Next: [Every honest price list is a ceiling](../04-every-mix-is-a-ceiling/README.md)  
Contents: [lp-duality](../../README.md)
