<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 3 · A method made of one operation

So ask for the opposite. What would a method look like if the *only* thing it
ever did was multiply by the matrix?

To answer that, this chapter has to write down what the matrix *is*, so the
rest of the guide can talk about it. The problem is the workshop from the
duality guide, which builds tables and chairs out of three things it has a
limited amount of:

|  | planks | hours of work | saw time | sells for |
|---|---|---|---|---|
| a table | 4 | 2 | 3 | $30 |
| a chair | 2 | 3 | 1 | $20 |
| **in stock** | **44** | **30** | **32** | |

Call the six recipe numbers `A`: three rows, one per shelf, and two columns,
one per product. A plan is two numbers, how many tables and how many chairs,
and it is called `x`. Then `Ax` means "run the plan through the recipes and
report what it consumes". Build 5 tables and 2 chairs and the plank row gives
4×5 + 2×2 = 24 planks; the other two rows give the hours and the saw time. So
`Ax` is a shopping list, one entry per shelf, and the stock levels are another
such list called `b`. The workshop's question, written for a machine, is

> choose a plan `x`, at least zero in every entry,
> so that `Ax` stays under the shelf limits `b`,
> making the profit as large as possible.

The duality guide's second idea gives the other half: put a price on each
shelf, so much per plank, so much per hour of work, so much per hour of saw
time, and collect the three prices in a list called `y`.

Prices need the same table read the other way. A row of `A` is a shelf and
tells you which products drain it. A *column* of `A` is a product and tells you
what that product is made of: a table is 4 planks, 2 hours and 3 of saw time.
Multiply a column by the prices and add up, and you have what one table's
ingredients cost. Doing that for every column at once is what `A` transposed
times `y` means, written `Aᵀy`. Transposing is not an operation performed on
anything; it is a decision to read the same six numbers down instead of across.
`A` turns a plan into a bill for shelves. `Aᵀ` turns shelf prices into a price
per product.

One worked case, using the prices that turn out to be right in chapter 8,
$6.25 a plank, $2.50 an hour, nothing for the saw: a table's ingredients cost
4×6.25 + 2×2.50 + 3×0 = $30, which is exactly what a table sells for. At those
prices, building a table breaks even to the penny. No coincidence, and the
duality guide is where it comes from.

Now score any pair of plan and prices with a single number:

> `L(x, y)` = what the plan costs, plus the prices times how much the plan
> overruns each shelf.

The first half is the plan's own score, with profit counted as a negative cost
so that a workshop trying to earn the most is a plan trying to cost the least.
The second half is a fine. Overrun the plank shelf by three planks with planks
priced at $6.25 and you are charged $18.75 for it. Leave planks spare and the
term goes the other way, which is the prices saying they would rather be zero
on a shelf nobody is fighting over.

The plan wants this small. The prices want it large: if a shelf is overrun,
raising its price punishes the plan for it. The answer is the standstill where
neither side can improve by moving: the plan is the best one, and the prices
are the shadow prices of chapter 7 over there.

Now the point. To improve the plan you need to know, at the current prices,
whether a product earns more than its ingredients cost, and that comparison is
the profit against `Aᵀy`. To improve the prices you need to know which shelves
are overdrawn, and that is `Ax` against `b`. Two questions, two readings of the
same table, one matrix-vector product each. Then you clamp anything that went
negative back to zero, because there are no negative chairs and no negative
prices.

That is the whole vocabulary. Two matrix-vector products, some vector
addition, and a clamp. **No factorisation, no basis, no pivoting, no ordering,
nothing sequential.**

It is exactly the shape chapter 1 asked for. The only question left is whether
it works.

> **In one sentence.** Treating the plan and the prices as two players lets you
> build a method out of nothing but matrix-vector products.

---

Chapter 3 of 10

Previous: [Why simplex is the wrong shape](../02-the-wrong-shape/README.md)  
Next: [The obvious version does not work](../04-the-obvious-version/README.md)  
Contents: [lp-on-gpu](../../README.md)
