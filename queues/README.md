# Queues and Little's law

*The wait is not about the speed.*

A clerk who serves a customer in six minutes will, at some point, hand someone
a wait of an hour, without having slowed down at any point. Fourteen chapters on
why, built from that one desk.

**[Read it →](https://bayzhan8.github.io/Illuminate/queues/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/queues/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](https://bayzhan8.github.io/Illuminate/queues/#ch0) | the wait, against how busy the clerk is |
| 1 | [The desk](https://bayzhan8.github.io/Illuminate/queues/#ch1) | L, W and the only Greek letter here |
| 2 | [Draw a box](https://bayzhan8.github.io/Illuminate/queues/#ch2) | Little's law, as one region measured twice |
| 3 | [What the law does not need](https://bayzhan8.github.io/Illuminate/queues/#ch3) | which is nearly everything |
| 4 | [Where the multiplier comes from](https://bayzhan8.github.io/Illuminate/queues/#ch4) | each round drags in a smaller round |
| 5 | [The wait explodes before the clerk is full](https://bayzhan8.github.io/Illuminate/queues/#ch5) | 54 minutes at 90%, 594 at 99% |
| 6 | [The other dial](https://bayzhan8.github.io/Illuminate/queues/#ch6) | a 26-fold spread at fixed speed and load |
| 7 | [Why you keep arriving during the long job](https://bayzhan8.github.io/Illuminate/queues/#ch7) | why you keep landing in the long job |
| 8 | [Three dials](https://bayzhan8.github.io/Illuminate/queues/#ch8) | utilisation, variability, job length |
| 9 | [Two clerks, one line](https://bayzhan8.github.io/Illuminate/queues/#ch9) | pooling, and why it helps most when quiet |
| 10 | [When pooling is the wrong answer](https://bayzhan8.github.io/Illuminate/queues/#ch10) | when a shared queue is the wrong answer |
| 11 | [Measuring it is harder than computing it](https://bayzhan8.github.io/Illuminate/queues/#ch11) | the law holds long before you have converged |
| 12 | [The confidence interval is twenty times too narrow](https://bayzhan8.github.io/Illuminate/queues/#ch12) | a 95% interval that covers 9% |
| 13 | [The same law somewhere else](https://bayzhan8.github.io/Illuminate/queues/#ch13) | inventory, WIP, beds, tenure |

## The claim

The formulas are exact rationals, so "exactly half" in chapter 6 means exactly
half rather than half to six decimals. The discrete-event simulation shares no
code with the formulas, which is what lets the tests use each to check the
other: the closed forms are also verified against summing the stationary
distribution term by term, and the exact Erlang C against the numerically
stable recursion.

Chapter 7 is the one worth reading twice. Little's law is satisfied on the
sample path to fourteen decimal places while both estimates are still percent-
level wrong, and the ordinary confidence interval on a million measured waits
contains the true answer 9% of the time.

```bash
cd .. && make bootstrap
cd queues && make check
```

## Source

Ross's *Introduction to Probability Models* for the derivations,
Harchol-Balter's *Performance Modeling and Design of Computer Systems* for the
many-server and job-size material. The chapter 2 proof follows Stidham's 1974
sample-path version, which needs no probability at all.
