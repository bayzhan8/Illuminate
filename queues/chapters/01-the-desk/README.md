<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · The desk

One clerk, serving on average ten customers an hour, so **six minutes** a
customer. People arrive at random.

Three quantities, and it matters which is which:

| | what it means | who would notice |
|---|---|---|
| **L** | how many people are here, on average | someone glancing at the room |
| **W** | how long a person is here, on average | the person |
| **λ** | how many people arrive per hour | the door |

Two of those have ordinary names. The third is written **λ**, the Greek letter
lambda, and it is the only Greek letter in this guide. It is not hiding
anything: λ is the arrival rate, the number of people coming through the door
per hour. Read it as "arrivals per hour" every time it appears.

These are averages of different things, and that is the point.

`L` averages over *time*. Take a photograph at random moments and count heads.

`W` averages over *people*. Ask each one how long they were there.

Nobody computing `L` ever asks anyone a question, and nobody computing `W` ever
looks at a clock on the wall. They are not two views of one measurement; they
are two measurements.

One more quantity, because it turns out to be the same idea: **utilisation**,
the fraction of the time the clerk is busy. At ten customers an hour arriving
and six minutes each, the clerk is busy 90% of the time.

> **In one sentence.** `L` is counted off the clock and `W` off the customers,
> and nothing so far connects them.

---

Chapter 1 of 13

Previous: [What this is](../00-what-this-is/README.md)  
Next: [Draw a box](../02-draw-a-box/README.md)  
Contents: [queues](../../README.md)
