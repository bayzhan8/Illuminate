# Decision log — lp-duality

What was chosen, what it cost, and what broke before it was chosen. Written
for whoever edits this next, including me.

---

**Example: a workshop, 3 rows × 2 columns, optimum (9, 4) = $350.**

Chosen by search, not taste. The requirements were: two variables so the
feasible set is drawable; an optimum at a vertex with integer coordinates; and
at least one row slack at that vertex. That last one is the whole reason
chapter 6 has a picture instead of a paragraph. With every row tight,
complementary slackness has nothing to point at.

Rejected: the first candidate (wood 40) gave T = 7.5. Fractional table counts
read as a modelling error to a beginner even when they are not.

Consequence: the plank price holds only over [20, 316/7], a range of 25 units
around a stock of 44. That narrowness was luck, and chapter 8 was built around
it afterwards.

---

**Arithmetic: `fractions.Fraction`, never float.**

The guide's central claim is that two numbers are *equal*. In float, one of
them arrives as 349.99999999999994 and the claim silently weakens to "equal
within tolerance", which is a different and much less interesting statement.
`Fraction` costs nothing at this size.

Downstream effect: `always.png` can print "largest disagreement across all 320:
0" and mean it literally.

---

**Pivoting: Bland's rule.**

Slower than Dantzig's rule. Chosen because it provably cannot cycle, and
chapter 9 is *about* degenerate programs. A solver that hangs on the example
in the chapter demonstrating degeneracy would be an embarrassing way to learn
this lesson.

---

**Duals: solved from `Bᵀy = c_B`, not read off the tableau.**

The tableau accumulates sign conventions through phase 1, negated rows and the
min/max flip. Getting one backwards produces a plausible wrong vector rather
than an error. Recovering `y` from an untouched copy of the standard-form
columns sidesteps all of it, and the test then compares that vector against the
dual program solved as an independent LP.

---

**Every claim gets a second, unrelated implementation.**

`vertices()` + `solve_by_enumeration()` exist only so the tests can disagree
with the simplex code. They share nothing with it. This is the highest-value
habit in the repository; the sibling topic's version of it caught two real
bugs.

---

**The value-function reconstruction refuses rather than guesses.**

Bends are found by sampling, and a bend almost never lands on a sample. This
example bends at 316/7. A grid stepping 45 to 45.5 straddles it, and the
straddling pair reports slope 25/14, which belongs to neither adjacent piece.
Taken at face value that becomes a phantom fourth segment a tenth of a unit
wide.

So: a line is believed only when two consecutive intervals agree on it,
single-interval runs are treated as straddles, and every bend is re-solved to
confirm the value there. A grid too coarse to corroborate anything raises.

This was observed before it was fixed. The first version drew four segments and
looked entirely reasonable.

---

**Chapter order: need before definition.**

Chapter 2 does nothing except demonstrate that search can never certify
optimality. It produces no result and introduces no object. It exists so that
the price list in chapter 3 arrives as an answer to a question the reader is
already holding, rather than as a definition to be accepted on credit.

The cost is one chapter of apparent stalling. Worth it.

---

**Prose constraints.**

Relations appear as pictures or sentences; the program itself appears once, as
a table of stock and recipes, because that is a shopping list. Every invented
term is mapped to its standard name in a table at the end, so the reader can
leave and read anything else. "Price" means a dual variable throughout and never a
market price in the same passage. Chapter 7 has to separate those two senses
explicitly, which is a sign the word is working hard.

---

**Six figures move, five do not.**

Motion is spent where the motion carries the argument: two regions converging,
an objective line sweeping to a corner, price bars covering their products, two
ladders closing, a capacity sliding until its price dies. Everything else is a
chart. Nine early drafts were boxes containing words. Those became tables,
which are searchable, selectable, and legible to a screen reader.

Animations hold three seconds on the final frame. The encoder folds identical
trailing frames into one, so the pause costs no bytes.

---

**Figures are matted, not inverted.**

They render on cream with black ink in both schemes, inside a bordered plate
that stays cream in dark mode. Inverting would mean re-validating the
blue/rust pair against a second surface for no reading benefit.

---

**Colour: two hues, chosen by simulator.**

Blue is a plan, rust is a price, everywhere, in every topic. Candidates were
run through a colour-vision validator rather than eyeballed. A third
categorical hue kept failing (blue against violet, rust against green, both
under the separation floor), so green survives only as a status mark, always
beside a word or a tick.

---

**Tests split three ways because they fail for different reasons.**

`test_lp.py` is mathematics. `test_lesson.py` is prose against code, catching
the class of failure invisible by reading, since a stale number leaves a page
that still scans perfectly. `test_sandbox.py` is JavaScript against Python.

Where the mathematics is genuinely non-unique (degenerate corners have several
valid dual vectors) the sandbox test asserts the property, feasible and same
objective, rather than the vector. Demanding an exact match would be demanding
something false.
