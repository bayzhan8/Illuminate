<!-- generated from ../../lesson.md by ../../build.py; do not edit -->

## 7 · Cancel the rotation

If the problem is rotation, remove the rotation.

Averaging is the tool. Average the iterates over a full revolution and the
turning cancels, because points on opposite sides of the circle pull in
opposite directions, while the inward drift does not. Then throw away the state, start
again from the average, and do it once more.

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

> **In one sentence.** Averaging over a revolution cancels the rotation and
> keeps the drift, which costs nothing and is worth orders of magnitude.

---

Chapter 7 of 10

Previous: [It turns fast and shrinks slowly](../06-fast-turn-slow-shrink/README.md)  
Next: [Does it get the right answer?](../08-the-same-answer/README.md)  
Contents: [lp-on-gpu](../../README.md)
