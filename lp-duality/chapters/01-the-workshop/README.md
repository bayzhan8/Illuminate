<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

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
straight lines.](region.png)

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
resting finally on a single corner.](sweep.gif)

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

Chapter 1 of 10

Previous: [What this is](../00-what-this-is/README.md)  
Next: [A good plan cannot prove itself best](../02-no-way-to-check/README.md)  
Contents: [lp-duality](../../README.md)
