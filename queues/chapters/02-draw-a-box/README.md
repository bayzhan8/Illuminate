<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 2 · Draw a box

Here is the whole theorem, and it contains no probability.

Draw two staircases. One steps up whenever somebody arrives. The other steps
up whenever somebody leaves. The gap between them, at any moment, is the number
of people in the room.

![Two staircases, arrivals above and departures below, with the region between
them shaded. Dashed rectangles show that the region is also exactly tiled by
one horizontal bar per customer.](region.png)

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
times.](two-counts.gif)

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

Chapter 2 of 8

Previous: [The desk](../01-the-desk/README.md)  
Next: [What the law does not need](../03-what-it-does-not-need/README.md)  
Contents: [queues](../../README.md)
