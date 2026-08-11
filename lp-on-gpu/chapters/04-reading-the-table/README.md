<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 4 · Reading the table two ways

So ask for the opposite of chapter 3. What would a method look like if the
*only* thing it ever did was multiply by the matrix?

Answering that needs some notation, and this chapter spends all of it. Four
symbols, `A`, `x`, `b` and `y`, and one mark on top of the first. Nothing else
in this guide is written in symbols at all, so if you get through this chapter
the rest is English.

The problem is the workshop from the duality guide, which builds tables and
chairs out of three things it has a limited amount of:

|  | planks | hours of work | saw time | sells for |
|---|---|---|---|---|
| a table | 4 | 2 | 3 | $30 |
| a chair | 2 | 3 | 1 | $20 |
| **in stock** | **44** | **30** | **32** | |

Call the six recipe numbers `A`: three rows, one per shelf, and two columns,
one per product. A plan is two numbers, how many tables and how many chairs,
and it is called `x`. The stock levels, 44, 30 and 32, are a list called `b`.

**Read the table across, and you get `Ax`.** A row of `A` is a shelf, and it
tells you which products drain it. So `Ax` means "run the plan through the
recipes and report what it consumes". Build 5 tables and 2 chairs and the plank
row gives 4×5 + 2×2 = 24 planks; the other two rows give the hours and the saw
time. `Ax` is a shopping list, one entry per shelf, and it is the thing that
has to stay under `b`.

So the workshop's question, written for a machine, is:

> choose a plan `x`, at least zero in every entry,
> so that `Ax` stays under the shelf limits `b`,
> making the profit as large as possible.

**Read the table down, and you get `Aᵀy`.** The duality guide's second idea
gives the other half: put a price on each shelf, so much per plank, so much per
hour of work, so much per hour of saw time, and collect the three prices in a
list called `y`. Now a *column* of `A` is a product, and it tells you what that
product is made of: a table is 4 planks, 2 hours and 3 of saw time. Multiply a
column by the prices and add up, and you have what one table's ingredients cost.
Doing that for every column at once is what `A` transposed times `y` means,
written `Aᵀy`.

Transposing is not an operation performed on anything. It is a decision to read
the same six numbers down instead of across. That is the whole content of the
little mark, and it is worth insisting on, because it is the reason the method
in this guide costs what it does: the two directions share one copy of the
matrix, so streaming over it serves both.

`A` turns a plan into a bill for shelves. `Aᵀ` turns shelf prices into a price
per product.

One worked case you can check on the back of an envelope, using the prices that
turn out to be right in chapter 11 — $6.25 a plank, $2.50 an hour, nothing for
the saw. A table's ingredients cost

> 4×6.25 + 2×2.50 + 3×0 = 25 + 5 + 0 = $30

which is exactly what a table sells for. At those prices, building a table
breaks even to the penny. That is no coincidence, and the duality guide is where
it comes from.

> **In one sentence.** One table of six numbers, read across, turns a plan into
> a bill; read down, it turns prices into a cost per product.

---

Chapter 4 of 13

Previous: [Why simplex is the wrong shape](../03-the-wrong-shape/README.md)  
Next: [Two players, one score](../05-two-players/README.md)  
Contents: [lp-on-gpu](../../README.md)
