<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 10 · Cancel the rotation

If the problem is rotation, remove the rotation.

Averaging is the tool. Average the iterates over a full revolution and the
turning cancels, because points on opposite sides of the circle pull in
opposite directions, while the inward drift does not.

That second half deserves a beat. Picture one revolution as a batch of points
spaced around a ring centred on the answer. Every point in the batch has a
partner roughly opposite it, and when you average a pair like that the two
sideways offsets are pointing opposite ways, so they cancel and what survives
is the centre. The shrinking is not like that. It never reverses. Every step
takes 2% off the radius, so every point in the batch is a little closer than
the one a full turn before it, and no later point ever undoes it. Average the
batch and you are left with the ring's centre and the progress inward, which is
the part you wanted. Then throw away the state, start again from the average,
and do it once more.

![Two convergence curves on a logarithmic scale, one decaying slowly and the
other dropping by six orders of magnitude over the same number of
iterations.](restarts.png)

Same iteration. Same two matrix products per step. Same step sizes. Restarting
every 40 iterations leaves it, after 600 iterations, about **a million times**
closer to the answer.

Nothing was added to the inner loop. The averaging is vector work, invisible
next to the matrix products. It is very close to a free improvement of six
orders of magnitude, and it is why practical first-order LP solvers all restart.

*(Real solvers choose the restart moment adaptively rather than on a fixed
schedule, and there are stronger variants than plain averaging. The mechanism
is the one above.)*

**[Try it yourself →](https://bayzhan8.github.io/Illuminate/lp-on-gpu/sandbox/10.html)**
Sweep the restart period and find the best one, then check it against the length
of one revolution from the chapter before.

> **In one sentence.** Averaging over a revolution cancels the rotation and
> keeps the drift, which costs nothing and is worth orders of magnitude.

---

Chapter 10 of 13

Previous: [It turns fast and shrinks slowly](../09-fast-turn-slow-shrink/README.md)  
Next: [Does it get the right answer?](../11-the-same-answer/README.md)  
Contents: [lp-on-gpu](../../README.md)
