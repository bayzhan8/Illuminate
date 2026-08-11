# Queues and Little's law

*The wait is not about the speed.*

A clerk who serves a customer in six minutes will, at some point, hand someone
a wait of an hour, without having slowed down at any point. Nine chapters on
why, built from that one desk.

**[Read it →](https://bayzhan8.github.io/Illuminate/queues/)**
· **[Play with it →](https://bayzhan8.github.io/Illuminate/queues/sandbox/)**

## Chapters

| | | |
|---|---|---|
| 0 | [What this is](chapters/00-what-this-is/) | the wait, against how busy the clerk is |
| 1 | [The desk](chapters/01-the-desk/) | L, W, λ, and which is an average of what |
| 2 | [Draw a box](chapters/02-draw-a-box/) | Little's law, as one region measured twice |
| 3 | [What the law does not need](chapters/03-what-it-does-not-need/) | which is nearly everything |
| 4 | [The wait explodes](chapters/04-the-wait-explodes/) | long before the clerk is full |
| 5 | [It is not the utilisation](chapters/05-variance-not-utilisation/) | a 26-fold spread at fixed load |
| 6 | [Two clerks](chapters/06-two-clerks/) | pooling, and when it is wrong |
| 7 | [Measuring is harder](chapters/07-measuring-is-harder/) | a 95% interval that covers 9% |
| 8 | [The same law elsewhere](chapters/08-the-same-law-elsewhere/) | inventory, WIP, beds |

## The claim

The formulas are exact rationals, so "exactly half" in chapter 5 means exactly
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
