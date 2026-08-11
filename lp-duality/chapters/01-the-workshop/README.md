<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 1 · The workshop

A workshop builds tables and chairs.

|  | planks | hours of work | saw time | sells for |
|---|---|---|---|---|
| a table | 4 | 2 | 3 | $30 |
| a chair | 2 | 3 | 1 | $20 |
| **in stock** | **44** | **30** | **32** | |

That is the whole problem. Three things there is a limited amount of, two
things to make out of them, and a question: what is the most money that can
come out of this building?

![The set of plans the workshop could actually carry out, drawn as a shaded
region with straight edges and sharp corners, with the three limits drawn as
straight lines.](region.png)

Every point in the shaded region is a plan the workshop could really carry out.
The edges are straight because building twice as much uses twice as much. That
is the only assumption in the guide, and it is what gives the picture flat
sides and corners rather than curves.

To find the best plan, take the set of plans worth some particular amount (a
straight line) and push it outwards.

![A line of equal profit sweeping across the region until it is about to leave,
resting finally on a single corner.](sweep.gif)

The last plan the line still touches is the best one: 9 tables and 4 chairs,
worth $350. It is a corner. That is not luck, and it is why every method in this
repository spends its time on corners.

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/01.html)**
Change what a table and a chair sell for, and watch the best corner jump from
one to the next.

---

Chapter 1 of 10

Previous: [What this is](../00-what-this-is/README.md)  
Next: [A good plan cannot prove itself best](../02-no-way-to-check/README.md)  
Contents: [lp-duality](../../README.md)
