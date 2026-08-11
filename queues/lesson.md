# The wait is not about the speed

**Queues and Little's law, built from one clerk and a six-minute job.**

A clerk who serves a customer in six minutes will, at some point, hand someone
a wait of an hour. Nothing about the clerk changed. Nothing about the job
changed. This guide is about what did.

Two ideas carry the whole thing. The first is an accounting identity so plain
it looks like it cannot be worth stating, and so general it applies to
warehouses, hospitals and software teams that contain no queue at all. The
second is that the thing which actually generates waiting is not how busy you
are. It is how *irregular* you are, and those are different dials.

The numbers below come from the code in this folder, in exact rationals,
asserted by its tests.

---

## 0 · What this is

![The average wait climbing as the clerk gets busier: flat and unremarkable
most of the way, then bending upward and running off the top of the frame as
the busy fraction approaches one.](chapters/00-what-this-is/hero.gif)

One clerk. Six minutes a customer, always. The only thing changing is how
often people arrive.

At half busy, the wait is six minutes. At 90% busy, it is 54 minutes. At 99%
busy, it is very nearly ten hours.

The clerk has not slowed down at any point. What ran out was idleness, and
idleness turns out to be the thing that was absorbing all the irregularity.

---

## 1 · The desk

One clerk, serving on average ten customers an hour, so **six minutes** a
customer. People arrive at random.

Three quantities, and it matters which is which:

| | what it means | who would notice |
|---|---|---|
| **L** | how many people are here, on average | someone glancing at the room |
| **W** | how long a person is here, on average | the person |
| **λ** | how many people arrive per hour | the door |

These are averages of different things. `L` averages over *time*: take a
photograph at random moments and count heads. `W` averages over *people*: ask
each one how long they were there. Nobody computing `L` ever asks anyone a
question, and nobody computing `W` ever looks at a clock on the wall.

One more quantity worth naming now, because it turns out to be the same idea:
**utilisation**, the fraction of the time the clerk is busy. At ten customers
an hour arriving and six minutes each, the clerk is busy 90% of the time.

---

## 2 · Draw a box

Here is the whole theorem, and it contains no probability.

Draw two staircases. One steps up whenever somebody arrives. The other steps
up whenever somebody leaves. The gap between them, at any moment, is the number
of people in the room.

![Two staircases, arrivals above and departures below, with the region between
them shaded. Dashed rectangles show that the region is also exactly tiled by
one horizontal bar per customer.](chapters/02-draw-a-box/region.png)

Now measure the shaded region between them, twice.

**Slice it vertically.** Each thin strip is *how many people were here* during
a moment, so adding the strips up gives person-hours as the manager would
count them: heads, repeatedly, over time.

**Slice it horizontally.** Each bar is one customer, running from their arrival
to their departure, so its length is *how long that person stayed*. Adding the
bars up gives person-hours as the customers would count them: one number each,
no clock.

![The same region filled first by vertical strips and then rebuilt from
horizontal bars, with a running total that lands on the same number both
times.](chapters/02-draw-a-box/two-counts.gif)

Same region. Both totals are **11.60 person-hours** for the eight customers
drawn. They are not close. They are the same number, because it is the same
shape measured two ways.

Divide that shared area by the elapsed time and you get the average number
present. Divide it by the number of customers and you get the average time each
one spent. So the two averages differ by exactly the factor of customers per
unit time, which is the arrival rate:

> **L = λW**

That is **Little's law**. It is an identity about a shaded region, and the
argument above is the entire proof.

It also applies to any box you care to draw. Draw the box around the *waiting
line only*, excluding the clerk, and it says the number of people queueing
equals the arrival rate times the time spent queueing. Draw the box around the
*clerk alone*, a box holding zero people or one, and its average occupancy is
the fraction of time the clerk is busy. So:

> **utilisation = arrival rate × service time**

Utilisation is not a separate concept. It is Little's law applied to the
smallest interesting box in the building.

---

## 3 · What the law does not need

The proof used a picture of eight customers. It did not use a distribution, so
the list of things Little's law does not require is unusually long, and worth
having explicitly:

- **No distributional assumptions.** Not Poisson arrivals, not exponential
  service, not anything. The staircases were drawn by hand.
- **No independence.** Arrivals may be correlated with each other and with how
  long service takes.
- **No queue discipline.** First come first served, last come first served,
  priority, random: the horizontal bars can be reordered freely and the region
  is unchanged. *(The figure above serves in order only so that the bars tile
  the region visibly; the identity does not care.)*
- **No steady state.** No stationarity, no equilibrium, no Markov property.
  Only the long-run averages need to settle.
- **No single server, and no server at all.** The box may contain a hundred
  clerks, or a warehouse, or an entire hospital.

What it *does* need is small and mostly about bookkeeping. λ has to count
entries to *the box you drew*. If people give up and leave the line, they are
not arrivals to the part of the system you are measuring. `W` has to be
measured across the same boundary as `L`; mixing "time spent queueing" with
"number of people in the building" is the most common way to get a wrong answer
from a correct theorem. And everyone who enters has to eventually leave.

---

## 4 · The wait explodes long before the clerk is full

Little's law relates the averages. It does not say how big they are. For that
you need to know something about the randomness, and with random arrivals and
random service times the answer is:

> **wait = service time × 1/(fraction of time idle)**

![The average wait against utilisation: barely moving up to about 70%, then
bending sharply and going vertical as the idle fraction approaches
zero.](chapters/04-the-wait-explodes/explode.png)

| arrivals per hour | busy | people present | wait before service |
|---|---|---|---|
| 5 | 50% | 1 | **6 min** |
| 8 | 80% | 4 | 24 min |
| 9 | 90% | 9 | **54 min** |
| 9.5 | 95% | 19 | 114 min |
| 9.9 | 99% | 99 | **594 min** |

Read the arithmetic between the rows, because it is the whole point:

- **5 to 9 customers an hour.** You added 80% more work. The wait went up
  **nine times**.
- **9 to 9.5.** You added 5.6% more work. The wait **doubled**.
- **9.5 to 9.9.** You added 4.2% more work. The wait went up **five times**.

The multiplier is one over the *idle* fraction, so what is being consumed as
you approach saturation is not capacity but slack. At 99% busy, the last one
percent of the clerk's time is carrying all of the queue.

This is also why a dashboard that reports utilisation and calls 97% green is
reporting the one number that cannot go bad. Utilisation is bounded above by
one. The wait is bounded by nothing.

---

## 5 · It is not the utilisation, it is the variability

Here is the part that changes what you would actually do.

Take the desk at 90% busy, where people wait 54 minutes. Change nothing about
the speed: the clerk still averages six minutes a customer, still serves ten an
hour, still busy exactly 90% of the time. Only make the six minutes *reliable*
so that every customer takes exactly six minutes, no more and no less.

The wait falls to **27 minutes**. Exactly half.

![Left, the wait at 90% busy for five different levels of service variability,
from 27 minutes when every job is identical to 702 minutes when a few are
enormously longer. Right, two curves against utilisation, the constant-service
one exactly half the variable one at every
point.](chapters/05-variance-not-utilisation/variance.png)

Not roughly half. Half at every utilisation, exactly. And the ladder continues
in the other direction:

| service times are | wait at 90% busy |
|---|---|
| always exactly 6 minutes | **27 min** |
| mildly variable | 40.5 min |
| exponential (the textbook case) | **54 min** |
| some customers much longer | 135 min |
| a few enormously longer | **702 min** |

Same clerk. Same average service time. Same 90% utilisation. A **twenty-six
fold** spread in how long people wait.

The reason is worth knowing, because it is not obvious. When you arrive and
someone is already being served, you wait out the *remainder* of their job.
A random moment is more likely to land inside a long job than a short one,
simply because long jobs occupy more of the timeline. So the job you are stuck
behind is not an average job. It is biased toward the long ones, and the
strength of that bias is exactly the variability of the service times.

Which gives three separate dials, and it is a genuine design choice which to
turn:

> **wait = (utilisation dial) × (variability dial) × (how long the job takes)**

Cutting variability in half does the same thing as a large capacity increase,
and is frequently cheaper. "Reduce variation" sounds like a slogan. It is
arithmetic.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/queues/sandbox/05.html)**
Move utilisation and variability independently and watch which one costs more.

---

## 6 · Two clerks, arranged two ways

Two clerks, the same total work. Either two separate lines, one per clerk, or a
single line feeding whichever clerk frees up first. Identical staff, identical
capacity, identical utilisation.

![Left, how many times shorter the single-line wait is, as a function of how
busy the clerks are: over three times better when quiet, falling toward twice
as good when busy. Right, a case where dedicating a desk to each job type beats
pooling by a factor of 1.5.](chapters/06-two-clerks/pooling.png)

At 90% busy: **54 minutes** in separate lines, **25.6 minutes** in one line.
Twice as good, for free.

At 45% busy: **4.9 minutes** against **1.5 minutes**. Over three times better.

Note which way round that goes, because most people guess the opposite.
**Pooling helps most when you are quiet**, and its advantage shrinks toward a
factor of two as you get busy. The mechanism is not extra capacity; there
isn't any. It is the elimination of the situation where one clerk sits idle
while somebody waits in the other line. When you are nearly saturated, that
situation is rare anyway, so there is less of it to eliminate.

### When pooling is the wrong answer

Suppose the work is not all alike. Quick jobs take an hour and arrive often;
slow jobs take ten hours and arrive rarely. Give each type its own desk, and
each desk runs at 80% busy. Or pool them into one line served by a desk of
double speed, at identical total capacity and identical utilisation.

| | average wait |
|---|---|
| a desk for quick jobs, a desk for slow ones | **3.64 hours** |
| one line, one desk of double speed | **5.50 hours** |

Pooling is **1.5 times worse**. Nothing was taken away; the arrangement
alone did it. Putting everything in one line means a one-hour job can arrive behind a
ten-hour job and wait for it, and chapter 5 already told us what happens when
you increase the variability of what people are stuck behind.

Pooling raises the number of servers, which helps, and raises the variability
of the queue everyone is standing in, which hurts. Usually the first wins. When
the jobs are wildly different sizes, the second does, which is why hospitals
have a separate minor injuries stream and supermarkets have a basket-only till.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/queues/sandbox/06.html)**
Add clerks and watch the single line pull ahead, then make them busier and
watch the gap close again.

---

## 7 · Measuring it is harder than computing it

If you did not believe any of the above, the obvious move is to measure your
own queue. This chapter is about why that is much harder than it looks.

Run a simulated desk at 90% busy and track both averages as they accumulate:
counting heads over time and dividing by the arrival rate, against asking each
customer and averaging.

![Left, two estimates of the average time in the system as a run proceeds, one
riding exactly on top of the other, both wandering between 44 and 60 minutes
over three hundred thousand customers. Right, a nominal 95% confidence interval
covering the true answer 9% of the time when it assumes independence, and 96%
when it does not.](chapters/07-measuring-is-harder/measuring.png)

Two things in that picture, and they point in opposite directions.

**Little's law is satisfied from almost the first customer.** The two curves
sit on top of each other the whole way. That is the identity of chapter 2
doing its work: over a window that starts and ends with an empty room, the
agreement is exact to fourteen decimal places, with no assumptions and no limit
taken.

**And both of them are wrong for a very long time.** After three hundred
thousand customers the estimate is still wandering around in the fifties for a
true answer of sixty. Your simulation satisfying `L = λW` tells you nothing
whatsoever about whether it has converged. It was never going to fail that
check.

Then the part that should worry anyone who has ever reported a simulation
result. Take the ordinary 95% confidence interval, the one every statistics course
teaches, the standard deviation over the square root of the sample size, and
apply it to a million measured waits. Repeat the whole experiment three
hundred times.

It contains the true answer **9% of the time**. It is about twenty times
too narrow.

The reason is that consecutive waits in a queue are not independent
observations, and it is not close. One long wait makes the next one long, and
at 90% busy roughly four hundred consecutive customers behave as a single
observation. A million measurements are worth about two and a half thousand.
The square root of four hundred is twenty, which is exactly the factor by which
the interval is wrong.

Cutting the run into ten large blocks and treating the block averages as the
observations restores it: **96% coverage**, with an honest interval more than twenty
times wider than the confident, wrong one.

The moral is not that simulation is useless. It is that near saturation, the
formula is not the approximation. The measurement is.

---

## 8 · The same law somewhere else entirely

Little's law says nothing about queues. It says something about boxes with
things going in and out. Rename the three letters:

| | L | λ | W |
|---|---|---|---|
| a queue | customers present | arrivals per hour | time in the system |
| **inventory** | stock on hand | throughput | days of supply |
| **a factory** | work in progress | production rate | cycle time |
| **a kanban board** | items in progress | delivery rate | lead time |
| **a hospital ward** | occupied beds | admissions per day | length of stay |
| **a company** | employees | hires per year | average tenure |

Each row is the same theorem. Two are worth spelling out.

**A WIP limit is a lead-time limit.** A team finishing 12 items a week with 6
in progress has a lead time of 6/12 = half a week. Raise the limit to 18 "so
nobody is blocked" and throughput does not move, being set by the bottleneck
rather than by how much you shove in, so the lead time becomes 18/12, a week
and a half. It tripled, and nothing else about the team changed. This is the entire
theoretical content of a kanban limit, and of CONWIP before it.

**Safety stock is measured in time, whether you like it or not.** A distributor
moving $100,000 of goods a day and holding $9M of inventory has, by Little's
law, 90 days of supply. Add $3M of stock to improve service and you have not
bought service; you have bought 30 more days of age on every unit. Obsolescence
and markdown scale with `W`, and you just increased it by a third.

Neither of those needed a demand distribution, a lead-time model, or an
independence assumption. That is why this particular result survives contact
with reality when most inventory theory does not.

## What the plain words are really called

| this guide says | everyone else says |
|---|---|
| how many are here, on average | **L**, the time-average number in system |
| how long a person is here | **W**, the customer-average sojourn time |
| L = λW | **Little's law** |
| fraction of time the clerk is busy | utilisation, **ρ** |
| one over the idle fraction | the congestion multiplier, 1/(1−ρ) |
| random arrivals, random service, one clerk | **M/M/1** |
| every job takes exactly the same time | **M/D/1** |
| the variability dial | the squared coefficient of variation, **c²** |
| the wait formula for any service distribution | the **Pollaczek–Khinchine** formula |
| the three-dial version | **Kingman's** approximation |
| one line, several clerks | **M/M/c**; the wait probability is **Erlang C** |
| cutting a run into blocks to get an honest interval | the **batch means** method |

## Further reading

Ross's *Introduction to Probability Models* for the derivations, Harchol-Balter's
*Performance Modeling and Design of Computer Systems* for the many-server and
job-size-variability material, and Little's own 50th-anniversary retrospective
for how far the identity reaches. The sample-path proof in chapter 2 follows
Stidham's 1974 version, which is the one that needs no probability.

## Running the code

```bash
make bootstrap    # once, from the repository root
cd queues && make verify
```

The formulas are exact rationals, so "exactly half" in chapter 5 means exactly
half. The simulation shares no code with the formulas, which is what lets the
tests use each to check the other.
