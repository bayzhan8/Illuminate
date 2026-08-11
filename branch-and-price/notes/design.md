# Decision log — branch-and-price

---

**Three instances, three jobs.**

`BOARDS` (25ft, widths 4/9/10, demands 3/6/7) is small enough to print every
pattern. `SCALE` (55ft, four widths) is small enough to solve exactly and large
enough that the loop visibly ignores most of it: six patterns touched out of
thirty. `MILL` is never solved. It exists so the pattern count can be printed.

Found by search over a few thousand candidates, against a checklist: the
relaxation must be fractional, the naive bound must round to something the
pattern bound rules out, and the loop must run 3–5 rounds so the animation has
frames worth reading.

`BOARDS` fails one of those criteria on purpose. It has six maximal patterns
and column generation ends up holding all six, so it does *not* demonstrate
skipping columns. That is why `SCALE` exists and why chapter 7 changes
instance halfway through.

---

**No integrality gap to demonstrate, so the guide does not claim one.**

The original plan for chapter 8 was an instance where rounding the relaxation
up gives the wrong answer. A search over every width/demand combination in a
sensible range found none. That is the round-up property of cutting stock, and
counterexamples are known to be rare and awkward.

Rather than assert a gap that was not found, the chapter says outright that
rounding up is nearly always right here, and gets its force from a different
comparison instead: ⌈naive⌉ = 6, ⌈Dantzig-Wolfe⌉ = 7, answer 7.

---

**Reuses `lpduality` rather than vendoring a solver.**

An import across topic folders is slightly awkward and it is the honest
structure. This topic is the duality topic under load; a second copy of the
simplex would obscure that and would drift.

---

**Two bugs, both of which returned confident wrong answers.**

Recorded because they are in the lesson and because they cost real time.

*Branching rows carry duals.* A row saying `x_s ≤ 0` gets a dual of its own,
which inflates that pattern's reduced cost. The knapsack then keeps nominating
a pattern the master already holds and has pinned. Stopping there leaves the
node's relaxation unsolved, its bound too high, and in a minimisation a bound
that is too high prunes the optimum.

*An under-supplied restricted master is not an infeasible node.* At a node
with `x_s ≤ 1` on the only pattern producing a needed width, the restricted
master is infeasible while the node is fine. The columns that would satisfy the
demand simply have not been generated. Emergency columns at a punitive price
keep the master solvable and fall out of the basis on their own.

Before either fix: 476 disagreements out of 1230 instances. Every search tree
looked reasonable. Nothing in the output suggested a problem. The only thing
that caught it was `integer_optimum_by_enumeration`, which exists purely to
disagree.

---

**The branching rule is weak and the guide says so.**

Branching on a single pattern's count is legible in a chapter and inferior in
practice; Ryan-Foster pushes the restriction into the pricing problem instead.
Kept for legibility, paid for in tree size, and named in the lesson so nobody
implements this one from here and wonders why it scales badly.

---

**`best_new_pattern` is a stand-in, and is labelled as one.**

When the knapsack nominates a held pattern, the search falls back to scanning
for the best pattern not yet in the master. That scan is the exact thing column
generation exists to avoid. It is correct, it is only reached in one situation,
and a real implementation replaces it with a branching rule that keeps pricing
well-defined. The docstring says this.

The scan also connects to chapter 9's closing section: where columns are
pre-generated rather than defined by a polyhedron, pricing genuinely *is* a
scan, and the bound obtained is a bound for the discretisation rather than for
the problem.

---

**Figures: two animated, five static.**

The hero (two bounds crossing an integer boundary) and the loop move. The
patterns, the pattern explosion, the touched/untouched grid and the tree do
not. The loop runs at about one frame per second because each frame carries
four numbers that have to be read rather than watched.

Patterns are drawn as boards with cuts marked, shaded light-to-dark by piece
width. Not coloured by width: blue and rust already mean plan and price
everywhere in this repository, and a third and fourth categorical hue would
break that and fail the contrast check besides.

---

**Sandbox 07 ships its numbers rather than recomputing them.**

The page shows the run the chapter shows. `build.py` bakes the rounds in as
JSON at build time and a test compares that JSON against a live solve, so the
convenience cannot silently diverge from the mathematics.
