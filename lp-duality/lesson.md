# Two problems, one number

**Linear programming duality, built from a workshop with three shelves.**

A workshop has 44 planks, 30 hours of labour and 32 hours of saw time, and it
makes tables and chairs out of them. The most money it can pull out of that
stock is $350.

Half of that claim is easy. Find a plan worth $350, add up the takings, and
there it is. The other half is knowing that nothing does better, and that half
is genuinely hard, because the plans cannot be checked one at a time. There are
infinitely many of them.

What settles it is a second question about the same workshop, one that never
mentions a plan. It asks what the contents of the building are worth. Its
answer is $350 as well.

*Every planning problem has a second problem hiding inside it, about prices.
Solving either one solves both.*

That fact is why a solver can tell you what a bottleneck is costing you rather
than only what to do about it. It is why big problems can be cut into pieces
and stitched back together. And it is what column generation and Benders
decomposition are made of.

This guide builds the whole thing from a workshop with three shelves and two
products, and never writes an equation.

**The plan.** Chapters 1 and 2 set up the problem and show why it cannot be
solved by trying things. Chapter 3 invents the second problem, and chapters 4
and 5 are the two halves of the theorem. Chapters 6 to 8 are what practitioners
actually use it for. Chapters 9 and 10 fence off what it does not say.

The numbers below are produced by the code in this folder and asserted by its
tests. Exact rationals throughout, so "equal" means equal.

---

## 0 · What this is

![Two panels side by side. On the left the workshop's possible plans, with a
profit line climbing until it rests on a corner. On the right the buyer's
possible prices, with a cost line falling until it rests on a corner. Both stop
at three hundred and fifty dollars.](chapters/00-what-this-is/hero.gif)

A workshop has 44 planks, 30 hours of labour and 32 hours of saw time, and it
turns those into tables and chairs. Two people are looking at it, and they are
asking different questions.

**The owner** wants to know what to build. Any combination of tables and chairs
the stock will stretch to is a candidate, and the owner is hunting for the one
that earns the most money. That is the left panel: a line of constant profit
being pushed outwards until the stock will not allow any more. It comes to rest
at **$350**.

**A buyer** has walked in wanting to purchase the entire contents of the
building — the planks, the labour hours, the saw hours — and has to name a price
for each. Naturally the buyer wants the total bill to be as small as possible.
But it has to be an offer the owner would take. The owner will refuse any price
list that undervalues a product: if the buyer prices a table's worth of
ingredients at $25 when a table sells for $30, the owner simply keeps the
materials and builds tables instead. So the buyer is pushing a bill *down*
against that restriction, and cannot push it below the point where some product
would be worth more built than sold. That is the right panel. It also comes to
rest at **$350**.

Nothing in the setup makes those the same question. One is about how much
furniture to make; the other is about what raw materials are worth. One is a
largest, the other a smallest. Neither calculation ever consults the other.

They stop at the same number. Not close to it. On it.

The reason to care is not the coincidence itself but what falls out of it. If
the two answers always agree, then a price list becomes a **receipt**. Hand
someone a plan earning $350 and a price list billing $350 and they can check, in
a few multiplications, that no plan anywhere on earth beats $350 — without
looking at a single other plan. The rest of this guide is where that receipt
comes from, why it always exists, and the four or five other things it turns out
to be good for.

> **In one sentence.** Two questions about the same workshop that share no
> ingredients have the same answer, and each one's answer certifies the other's.

---

## 1 · The workshop

A workshop builds tables and chairs.

|  | planks | hours of work | saw time | sells for |
|---|---|---|---|---|
| a table | 4 | 2 | 3 | $30 |
| a chair | 2 | 3 | 1 | $20 |
| **in stock** | **44** | **30** | **32** | |

That is the whole problem. Three things there is a limited amount of, two
things to make out of them, one question: what is the most money that can come
out of this building?

Every possible plan is a point on a picture.

![The set of plans the workshop could actually carry out, drawn as a shaded
region with straight edges and sharp corners, with the three limits drawn as
straight lines.](chapters/01-the-workshop/region.png)

Build 5 tables and 2 chairs and you have used 24 planks, 16 hours and 17 of saw
time. All three fit, so that plan sits somewhere inside the shaded region.
Build 11 tables and you have consumed every plank with nothing left for chairs;
that is the far corner on the right.

The edges are straight because building twice as much uses twice as much. That
proportionality is the only assumption in this guide, and it is what gives the
picture flat sides and sharp corners rather than curves.

Now find the best plan. Take all the plans worth some particular amount — that
is a straight line — and push it outwards.

![A line of equal profit sweeping across the region until it is about to leave,
resting finally on a single corner.](chapters/01-the-workshop/sweep.gif)

The last plan the line still touches is the best one: **9 tables and 4 chairs,
worth $350.**

It stops on a corner. That is not luck, and it is why every method in this
repository spends its time on corners.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/01.html)**
Change what a table and a chair sell for, and watch the best corner jump from
one to the next.

> **In one sentence.** The plans form a region with flat sides, and the best one
> is always at a corner.

---

## 2 · A good plan cannot prove itself best

You have a plan worth $350. How do you know there is nothing better?

The obvious move is to try more plans. So try a lot of them.

![A curve showing the best profit found so far against the number of plans
tried. It rises quickly, then flattens, and stays flat.](chapters/02-no-way-to-check/guessing.png)

The curve flattens, and that is exactly the problem.

**A flat curve looks the same whether you have found the best plan or have
merely stopped getting lucky.** Nothing in the search distinguishes those two.

Nor can you finish the job by being more thorough. The region is a continuum. 7
tables and 4½ chairs sits in it, and so does everything between that and its
neighbours. Enumeration is not slow here; it is not defined.

The deeper issue is what a plan is able to say. A plan you can actually build
is a statement of the form *at least this much is possible*. Stack up as many
as you like and you still only have a floor.

What is needed is a statement of the opposite kind, saying *no more than this
is possible*, and no plan will ever be one.

> **In one sentence.** Plans give you floors, never ceilings, so no amount of
> searching can certify that you are finished.

---

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
change.](chapters/03-mixing-the-rules/mixing.gif)

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

## 4 · Every honest price list is a ceiling

That claim is the load-bearing step, so it deserves to be seen rather than
asserted. It is also two ideas rather than one, and separating them is what
makes it obvious.

Take any plan; it does not have to be a good one. Take any price list that
covers both products. Line up three numbers.

![Three bars. What the plan earns, three hundred and forty dollars. What those
prices charge for the ingredients the plan uses, three hundred and eighty six.
What those prices charge for everything in the building, three hundred and
ninety eight.](chapters/04-every-mix-is-a-ceiling/chain.png)

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

## 5 · The gap closes, every time

So plans push up from below and price lists press down from above. The question
is whether they meet, or stop with a gap that nothing can close.

![Real plans appearing along a dollar scale from the left, and real price lists
appearing from the right, with the band of remaining possibilities shrinking
until it is a single point at three hundred and fifty
dollars.](chapters/05-the-gap-closes/meet.gif)

They meet. The best plan earns $350, the cheapest honest price list charges
$350, and the space between them has nothing left in it.

It would be fair to suspect this workshop of being rigged. So here are 320
more, invented at random, with different numbers of products, different numbers
of shelves and different recipes. Each was solved twice from scratch: once for
its best plan, and once, as a separate problem, for its cheapest prices.

![A scatter plot of the best plan's profit against the cheapest price list's
bill for three hundred and twenty random workshops. Every point lies on the
diagonal.](chapters/05-the-gap-closes/always.png)

Every point is on the diagonal. Both sides are computed in exact fractions, so
the largest disagreement across all 320 is zero. Not small. Zero.

Be clear about what that picture is, though. It is not a proof. It is 320
pieces of evidence, and a warning that any explanation had better account for
all of them. The proof exists, and chapter 9 shows its shape by looking at what
happens when the conditions fail.

This is the theorem the subject rests on, and it is called **strong duality**.

Two problems, then. The one about plans is the **primal**; the one about prices
is the **dual**. Each is built from the other by turning it inside out, and the
little table from chapter 1 is the place to watch that happen.

The plans problem reads that table **across**. The first row says a table takes
4 planks, 2 hours and 3 of saw time; the unknowns are how many tables and how
many chairs.

The prices problem reads the same table **down**. The planks column says planks
go out 4 to a table and 2 to a chair; the unknowns are what to charge for a
plank, an hour of work and an hour of saw time.

That single change of reading direction is the whole swap. Piece by piece, on
these numbers:

- The workshop had three limits, one per shelf. The prices problem has three
  unknowns, one price per shelf. Rows became variables.
- The workshop had two unknowns, tables and chairs. The prices problem has two
  rules, one per product: a table's ingredients must be charged at $30 or more,
  a chair's at $20 or more. Variables became rows.
- $30 and $20 were the thing the workshop pushed up. They are now the floors
  those two rules have to clear.
- 44, 30 and 32 were the limits the workshop pushed against. They are now the
  thing being pushed down, since the bill for the whole building is 44 plank
  prices plus 30 hourly rates plus 32 saw rates.
- Every *at most* turned into an *at least*, and looking for the largest number
  turned into looking for the smallest.

Do that swap twice and you are back where you started, which is the sense in
which neither one is the original.

> **In one sentence.** The best plan and the cheapest honest price list always
> agree exactly, which is what makes the second problem worth solving.

---

## 6 · Which rules are actually holding you back

Now the dual starts paying for itself.

The best plan is 9 tables and 4 chairs. Look at what it consumes: all 44
planks, all 30 hours, and 31 of the 32 hours of saw time. One hour of saw time
sits there unused.

Now look at the prices: $6.25 a plank, $2.50 an hour, and nothing at all for
saw time.

![The region of legal plans with the two limits the best plan is pressed against drawn
solid and priced, and the limit it is clear of drawn dashed and priced at
zero.](chapters/06-who-is-binding/binding.png)

Spare saw time, zero saw price. Planks fully consumed, planks priced.

**A resource with something left over is worth nothing; a resource that is all
used up is worth something.** Which, once said, is obvious. If saw time is not
what is stopping you, nobody would pay you for another hour of it.

The same rule runs the other way, for products rather than resources. A product
that gets built is priced at what it earns and no more. A product priced
*above* what it earns is one you are better off not building, and in the best
plan its quantity is zero.

This pairing is called **complementary slackness**. In practice it is the first
thing anyone looks at, because it answers the question people actually have:
not "what should I do" but "what is in my way".

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/06.html)**
Change the stock levels and watch which rules become binding, and which prices
switch on and off in response.

> **In one sentence.** The prices identify the bottleneck by being zero on
> exactly the constraints that have slack.

---

## 7 · What one more plank is worth

The prices are more than a ranking. They are exact rates.

The plank price is $6.25, meaning one more plank in stock is worth $6.25 of
extra profit. To the penny, and you can watch it happen.

![The plank limit sliding outward, the region growing, and the best corner
sliding along with it while the profit climbs at a steady rate, until the rate
suddenly stops.](chapters/07-what-one-more-is-worth/shadow.gif)

Add a plank. The plank line moves out, the best corner slides along the hours
line, and the profit goes up by $6.25. Add another. Same again.

So where does $6.25 come from? Not from a plank being worth that. It comes from
what the extra plank lets the workshop rearrange. The best plan is pressed
against two rules at once, planks and hours, and hours are still just as
scarce as before, so the plan cannot simply grow. It has to trade one product
for the other along the hours line.

Every plank that arrives buys the same trade, in the same proportions, so the
easiest way to see the rate is to scale the trade up until it comes out in
whole furniture. At that size it reads: 3 more tables, 2 fewer chairs, 8 more
planks. Check it against the recipes in the chapter 1 table:

- **Planks.** The 3 new tables need 12. The 2 dropped chairs give back 4. Net
  cost, 8 planks, which is exactly what arrived.
- **Hours.** The 3 tables need 6. The 2 chairs give back 6. Net zero, so the
  hours are as full after the trade as before, and the plan is still legal.
- **Money.** 3 tables at $30 is $90 in. 2 chairs at $20 is $40 out. The trade
  is worth $50.

Fifty dollars for eight planks. That is $6.25 a plank, and it is where the
number comes from. How far you can keep making that trade is a separate
question, and chapter 8 answers it.

This is what a dual variable *is*, and why the name **shadow price** stuck.

It is worth being careful about what kind of number that is. Planks might cost
$3 at the yard. Here the forty-fifth one is worth $6.25, because of what else
this workshop happens to be short of. It is not a market price. It is a price
*to this workshop, given everything else it has*, and that is the number you
want when deciding what to buy, what to negotiate for, and what a bottleneck is
costing.

Watch the end of that animation, though. The rate stops.

> **In one sentence.** A dual variable is the exact rate at which the answer
> improves per extra unit of that resource.

---

## 8 · The price is only local

Keep adding planks and eventually the saw becomes the problem instead. From
that point on, extra planks pile up unused and are worth nothing.

![The workshop's best profit as a function of how many planks it has: three
straight pieces, each flatter than the last, bending at twenty planks and at
just over forty five.](chapters/08-the-price-breaks/curve.png)

The whole curve is three straight pieces, and the plank price is *the slope of
the piece you happen to be standing on*:

| planks in stock | one more plank is worth | why |
|---|---|---|
| under 20 | $10.00 | so few planks that tables are not worth building at all |
| 20 to 45 ⅐ | **$6.25** | where this workshop actually is |
| over 45 ⅐ | $0.00 | the saw is the binding rule now; planks pile up |

Both bends have a reason, and the odd-looking one has the better reason.

**The first bend, at 20 planks.** Compare the two products by what they get out
of a plank. A chair uses 2 planks and earns $20, which is $10 a plank. A table
uses 4 planks and earns $30, which is $7.50. So while planks are the only thing
running out, the workshop should build chairs and nothing else, and every extra
plank is half a chair, worth $10. That lasts until the chairs run into a
different shelf. Ten chairs take 30 hours of work, and 30 hours is all there
is; ten chairs also take exactly 20 planks. Twenty planks is the point where
the hours run out and the cheap ride ends.

**The second bend, at 45 ⅐ planks.** Past 20 planks, extra planks have to buy
their way in through the trade from chapter 7: eight planks in, three tables up,
two chairs down. That trade leaves the hours alone. It does not leave the saw
alone. Three more tables want 9 hours of saw time, two fewer chairs give back
2, so every swap of eight planks eats 7 hours of saw time.

The workshop has 1 hour of saw time spare, the one from chapter 6. One spare
hour against 7 per swap buys one seventh of a swap, and one seventh of eight
planks is 1 ⅐ planks. That is the whole of the ⅐. It is one spare saw-hour
divided by the seven the trade consumes. After that the saw is empty, no
further tables can be built, and arriving planks have nowhere to go.

The workshop has 44 planks. It is 1 ⅐ planks away from its price collapsing to
nothing.

That is a narrow shelf to be standing on, and it is the most common way this
idea gets misused. A shadow price quoted without the range over which it holds
is close to useless.

The pieces get flatter, never steeper. Easy uses go first, so more of a
resource is never worth more per unit than the last lot was, and the curve can
only bend one way.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/08.html)**
Slide the stock of any of the three resources and watch its own price step down.

> **In one sentence.** A shadow price is a local slope with an expiry date, so
> it always has to be quoted with the range over which it holds.

---

## 9 · Profit that runs away

Two things can go wrong, and the dual has something to say about both. Here is
the first.

![A region with no upper limit and profit lines marching off it
forever.](chapters/09-profit-runs-away/edges.png)

If the rules leave a direction the workshop can go forever, there is no best
plan. Nothing is stopping it, so the profit is unbounded and there is no number
to report.

Now ask what the price side makes of that. An honest price list has to be a
ceiling over every plan at once, which is chapter 4. But a ceiling would have to
be a number bigger than every plan, and no such number exists. So there is no
honest price list either — not a bad one, not a loose one, none at all.

The two failures come as a pair, and it is worth stating the pairing plainly
because it is the shape the whole theory keeps taking: *the plan side runs away
precisely when the price side has nothing to offer.*

Which is also how a solver tells you. Hand it a model with a direction of escape
and it does not search forever and give up. It finds the direction, reports
unbounded, and the thing it hands back as evidence is a fact about the prices.

> **In one sentence.** Profit running away on one side is exactly the same event
> as no honest price list existing on the other.

---

## 10 · A plan that cannot exist

The second failure is the more interesting one, because of *how* it gets
settled.

![A scale of tables showing that the planks reach eleven and the order starts at
twelve, with nothing in between.](chapters/10-no-such-plan/no-such-plan.png)

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

## 11 · Where this leads

Everything above is one small problem solved by hand. What makes duality worth
this much attention is what gets built on it.

- **The simplex method** decides which product to bring into a plan by asking
  whether its dual row is violated. The "reduced cost" in any solver's log is
  the amount by which a product's ingredients cost less than it earns.
- **Column generation** turns that around. When there are too many possible
  products to write down, solve with a few, read the prices off the dual, and
  use those prices to *ask* whether some product you have not written down yet
  would be worth adding. The prices are the entire interface between the two
  halves.
- **Dantzig–Wolfe decomposition** is that idea applied to a problem with
  repeated structure, and **branch and price** is what you get when the pieces
  have to come out whole.
- **Benders decomposition** cuts the other way: fix the hard decisions, solve
  what is left, and take the *dual* of that leftover problem as a new rule to
  send back. Every Benders cut is a price list from chapter 3, doing the job it
  did there: proving a proposal cannot be as good as it claims.

The next guide, [along the edge, or through the middle](../corners-vs-centre/),
takes the first of those apart: how the walk uses the dual row to choose, and
what a rival method that refuses corners does instead. [Solving a model you
never wrote down](../branch-and-price/) is the second of them under load.

---

## What the plain words are really called

Every invented phrase in this guide has a standard name. They are here so that
anything you read next is legible.

| this guide says | everyone else says |
|---|---|
| a plan | a feasible solution |
| the best plan | an optimal solution |
| the plans problem | the **primal** |
| a price list that covers every product | a dual feasible solution |
| the prices problem | the **dual** |
| a ceiling | an upper bound |
| every honest price list is a ceiling | **weak duality** |
| the two always meet | **strong duality** |
| spare resources are worth nothing | **complementary slackness** |
| what one more is worth | a **shadow price** / dual variable |
| how long a price holds | right-hand-side ranging |
| the short proof that a plan cannot exist | a **Farkas certificate** |
| profit that runs away | unbounded |
| a price that is not unique | degeneracy |

## Running the code

```bash
make bootstrap    # once, from the repository root
cd lp-duality && make verify
```

The solver uses exact fractions throughout and Bland's pivoting rule, which is
slower than the usual choice and cannot cycle. It is about 250 lines and is
meant to be read. The tests check three separate things: that the mathematics
is right, that the numbers written on this page still match what the code
produces, and that the interactive pages compute the same values the Python
does.
