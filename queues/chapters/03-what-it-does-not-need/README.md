<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

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

What it *does* need is small and mostly about bookkeeping.

λ has to count entries to *the box you drew*. If people give up and leave the
line, they are not arrivals to the part of the system you are measuring.

`W` has to be measured across the same boundary as `L`. Mixing "time spent
queueing" with "number of people in the building" is the most common way to get
a wrong answer out of a correct theorem.

And everyone who enters has to eventually leave.

> **In one sentence.** Little's law needs no probability at all, only that you
> draw one box and measure both quantities across the same edge.

---

Chapter 3 of 8

Previous: [Draw a box](../02-draw-a-box/README.md)  
Next: [The wait explodes before the clerk is full](../04-the-wait-explodes/README.md)  
Contents: [queues](../../README.md)
