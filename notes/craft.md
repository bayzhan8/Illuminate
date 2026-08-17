# Craft notes

How these guides are written. This is the cross-topic companion to each
`<topic>/notes/design.md`, which records decisions about one topic only.

The technique here was arrived at by reading the Jacobian-conjecture guide at
`muchmirul.github.io/jacobian-conjecture` closely — the article, its chapter
files, and its two design notes, which are where its method is actually written
down — and taking from it only what transfers. Nothing about its wording,
chapter shape, visual identity or subject is reused; see the divergence rules at
the end.

---

## The finding that started this note

Measured against that guide, chapter by chapter, as the guides stood in
August 2026:

| | words per chapter | ideas per chapter |
|---|---|---|
| the reference | ~490 | 1 |
| these guides, before | ~370–450 | 3–5 |

The length was right. The load was not. The reference spends a whole chapter,
270 words, on *a function is a machine*, and another whole chapter on *some
machines can be undone*. `lp-duality` chapter 3 introduces pricing, the covering
condition, the ceiling argument and a failure mode in 226 words.

So the accessibility gap was never that the prose is dense. Sentence for
sentence it is plainer than the reference. The gap was that **a reader who does
not already know the subject was asked to take three or four steps per chapter
and given a handhold for one of them.**

Everything below follows from that. The rules are the standing ones; the
"applied" notes record the August 2026 pass that first enforced them.

---

## 1 · One idea per chapter, and the idea is small

A chapter earns its number by introducing exactly one thing the reader could
not have said before reading it. Not one *topic*, one *idea*.

The test is mechanical. Write the chapter's "In one sentence" box first. If it
needs an "and", the chapter is two chapters.

Being generous with chapter numbers is free. Chapters are cheap; a reader who
loses the thread is not.

**Applied.** All six guides were re-cut against that test:

| | was | now | what was carved out |
|---|---|---|---|
| `corners-vs-centre` | 11 | 15 | the old ch5 held five ideas; it is now the rule/method distinction, Bland's Fibonacci growth, every-rule-has-a-cube, and smoothed analysis. The barrier chapter split into the penalty and the curve it traces |
| `solvers` | 11 | 15 | the cascade split from the decision it settles; the benchmarks from measuring your own; the layer chapter into layers, convex, and toolkits |
| `lp-on-gpu` | 11 | 14 | arithmetic intensity split from the roofline; the notation chapter into reading the table, the two-player score, and the method |
| `queues` | 9 | 14 | the multiplier split from the explosion; the variability ladder, the inspection paradox and the three dials became three chapters; pooling from when pooling loses; converged-looking from the coverage failure |
| `branch-and-price` | 10 | 12 | the 848-word chapter 5, the largest in the repo, became start-small, what-the-prices-say, and the dual-side reading |
| `lp-duality` | 11 | 12 | unboundedness split from infeasibility |

82 chapters, from 63. Mean length fell from ~400 words to 352; the longest is
now 636 words, where it was 848.

Two chapters remain over 600 words and both are deliberate: `lp-on-gpu` 4 is one
idea (a table read two ways) that is spending the guide's whole notation budget
at once, and `solvers` 2 is a catalogue of six reductions, which is a single
chapter's work even though it is six paragraphs. Length was never the test.

## 1a · The chapter-0 rule, and the failure that produced it

The August 2026 re-cut fixed the *chapters* and left the *openings* alone, and
that turned out to be where the corpus was still losing readers. A reader was
handed `branch-and-price` chapter 0 and reported, accurately, that they got
nothing from it. It read:

> Model it the obvious way, relax it, and it proves you need at least 5.44
> boards. So six might be enough. The model cannot say otherwise.

Five sentences, and the argument in them runs on four things the reader has not
been given: what it means to *model* something, what it means to *relax* a
model, why a lower limit of 5.44 leaves six open, and why any of it matters. The
sentences are short and the vocabulary is plain, so the page looks accessible
and is not. This is the same disease as the three-ideas-per-chapter problem in
§1, relocated: the compression moved out of the chapter and into the sentence.

Two rules follow, and they are absolute.

**A chapter 0 teaches; it does not tease.** It must leave the reader holding one
thing they did not have, established well enough that they could repeat it to
somebody else. A list of results with the derivations withheld is a trailer, and
a trailer is worth nothing to a reader who came to learn. The test: strike every
number from the chapter and ask whether anything is left. If not, rewrite it.

**Nothing may carry an argument before it has been built.** Not a term, not a
notion, not a step. This is §2 applied at word scale rather than chapter scale.
The words that kept breaking it, in order of damage: *relax* and *relaxation*,
*model* used as a verb, *bound*, *variable*, *column*, *objective*, *feasible
region*, *basis*. If one of them is load-bearing in a sentence, either it was
built in an earlier chapter — name that chapter — or it gets built right there,
in a sentence, before it is leant on.

**Applied**, August 2026, second pass. Every chapter 0 in the repository was
rewritten, and the openings above them with it.

| | was | now |
|---|---|---|
| `branch-and-price` | 5.44 and 6.5 asserted, running on *model* and *relax* | the order, and two lower-limit arguments the reader checks by hand — 136 ÷ 25, and 13 long pieces two to a board. Chapter 2 then builds *model* and *relax* and shows where the first one came from mechanically |
| `lp-duality` | two panels stopping on the same number | the buyer's problem stated fully enough that its answer being $350 is surprising, plus what the coincidence buys: a receipt |
| `corners-vs-centre` | the two routes, and $350 | the region, corners and walls defined; and the opening now says what a linear program *is*, which the guide had never done |
| `lp-on-gpu` | one curve settles, one does not | why anyone would build a method this fragile, said before the fragility |
| `queues` | 6 / 54 / 594 minutes, and an assertion about idleness | *busy* derived from the arrival rate, the three rows as a table, and the row-to-row arithmetic — 80% more work, nine times the wait |
| `solvers` | rows, columns and nonzeros used cold | all three defined off the picture, then one deletion walked through end to end |

Two further things that pass came out of the same read and are worth keeping as
standing checks. `queues` chapter 0 said "six minutes a customer, always", which
reads as deterministic service while quoting M/M/1 numbers; the wait at 90% is
54 minutes only because service is *random*, and 27 if it really were always six
minutes. **State the distribution wherever a number depends on it.** And
`lp-on-gpu` chapter 9 required eigenvalues of a 2×2 matrix and complex conjugate
pairs to reach two numbers; it now states what one step does — a fixed turn and a
fixed shrink — derives nothing from linear algebra, and puts the eigenvalue route
in a parenthetical for readers who want it. **Where a technique is the standard
route rather than the content, name it in an aside and take the reader by the
short way.**

## 2 · Nothing is used before it is built, and say when you are cashing in

The reference is a tower: function → inverse → polynomial → plane map → linear
map → determinant → Jacobian → local-vs-global → the question. Its chapter 9
opens by listing the five pieces with the chapter each came from, then spends
the conjecture out of that account.

**Declare the debt.** When a chapter leans on an earlier one, name the chapter.
`lp-duality` chapter 8 does this well ("the trade from chapter 7: eight planks
in, three tables up, two chairs down") and it is among the strongest passages in
the repo. Do it every time, not when convenient.

**Nothing is asserted about a figure that the figure does not show.** No test
compares alt text or prose against what a script actually plots, and the gap is
real: `corners-vs-centre` chapter 4 carried alt text describing a 3D cube that
was never drawn, over a chart whose y-axis said "corners visited" while every
series on it was a pivot count. Both had been there since the chapter was
written. **Look at every figure you touch, and at the prose beside it**, because
this is the one class of error the test suite cannot reach.

**Never borrow from a guide that does not exist.** Still outstanding: three
guides lean on branch and bound, which is queued and unwritten.
`branch-and-price` chapter 10 defines it in half a sentence and builds on it,
and `lp-on-gpu` chapter 12 and `corners-vs-centre` chapter 14 both assume it.
That is the one place the no-unearned-assertions rule is still broken
structurally rather than locally, and writing that topic closes it.

## 3 · The hope, then the thing that kills it

The reference's best chapter is its eleventh, and its shape is worth copying
exactly. Three obstacles, each written as:

> *The hope:* the natural plan a reader would themselves propose.
>
> *The example that kills it:* one specific object, named, with its numbers.

This works because it builds the reader's own objection for them before
answering it, so the answer lands on a question they are actually holding.

**Applied,** in the chapters that were being rewritten anyway: `corners-vs-centre`
chapter 7 opens by proposing steepest edge as the winner and then dismantling
the idea that its one pivot means anything; chapter 8 states the puzzle as
sharper rather than easier before resolving it. `queues` chapter 10 opens by
saying chapter 9 made pooling sound unconditional. `solvers` chapter 12 grants
the benchmarks everything and shows they still do not answer your question.

Still flat, and worth converting when those guides are next touched: the
ellipsoid's polynomial-means-fast promise, and the naive relaxation's
round-it-up.

## 4 · Give the reader something to check by hand

The reference ends by handing over three points and one short polynomial and
inviting the reader to evaluate it in their head. Three lines of arithmetic, all
coming out zero, and the reader has personally verified the punchline of an
87-year-old problem.

"Every number is asserted by a test" is a claim about a pipeline the reader will
never run. A number they can check on the back of an envelope in thirty seconds
is a different kind of evidence, and it is the one that converts.

One per guide, and signpost it so it is not mistaken for narration:

- `lp-duality` chapter 10 — a quarter of the plank rule, subtract, land on
  "half the chairs, at most −1"
- `queues` chapter 7 — nine jobs of two minutes and one of forty-two, so
  forty-two of every sixty minutes sit inside the long job
- `branch-and-price` chapter 3 — thirteen long pieces, two to a board, 6.5;
  and chapter 5, three lines that add to 7 boards
- `solvers` chapter 4 — 25/100 = 0.25, rounds to 1, and a binary decision is
  gone
- `lp-on-gpu` chapter 4 — 4×6.25 + 2×2.50 + 3×0 = $30, a table breaking even
  to the penny
- `corners-vs-centre` chapter 4 — read the chart at dimension 3: eight corners,
  seven pivots, and the gap stays exactly one all the way to 1024 and 1023

## 5 · Count the notation out loud

`queues` gets this right: "it is written **λ** … and it is the only Greek letter
in this guide." Naming the size of the notational debt caps the reader's anxiety
about how much worse it is going to get.

A guide announces its total symbol budget the first time it spends any of it,
and the budget is small.

**Applied.** `lp-on-gpu` chapter 4 now opens by saying it spends the entire
budget — four symbols and one mark — and that nothing after it is written in
symbols at all. `corners-vs-centre` chapter 10 does the same for μ, which it had
previously used without ever introducing.

## 6 · Where these guides are already ahead — do not regress this

The reference is better at rungs. It is not better at rigour, and the gap runs
the other way, sometimes widely. Protect:

**Real derivations, not gestures.** The reference introduces the determinant as
`ad − bc` and says "you will never need to compute this by hand here."
`lp-duality` chapter 8 instead derives where the ⅐ in "45 ⅐ planks" comes from:
one spare saw-hour divided by the seven a swap consumes. That is a harder and
better piece of teaching than anything in the reference.

**The same number reached twice by different routes.** `queues` chapters 7 and 8
get leftovers of 3, 6 and 15 minutes from the inspection paradox, then show the
waits 27, 54 and 135 are nine times each. `queues` chapter 12 measures an
autocorrelation length of ~400 from the waits themselves and separately measures
9% interval coverage, and √400 = 20 is the same factor arriving from two
independent directions. The reference has nothing this good.

**Saying which claims are not earned.** "This one is quoted, not proved." "The
band drawn above is that rule of thumb, not a measurement from this repository."
"The account is Dantzig's own recollection and is not independently documented."
The reference does this once; these guides do it constantly, and it is the
single most distinctive thing about them.

**Confessing bugs.** `branch-and-price` chapter 10 reports that this repo's own
solver disagreed with brute force on 476 of 1230 instances and why. Keep this
habit. It buys more credibility than any amount of careful phrasing.

**The naming tables.** Ending each guide with *this guide says* / *everyone else
says* lets the prose stay plain without leaving the reader unable to read
anything else afterwards. The reference does it in scattered parentheticals; the
table is better.

## 7 · Standing tics to watch

- **The two-beat negation.** "Not close to it. On it." / "Not small. Zero." It
  is a good move, and by six guides it had become a signature, which is the
  problem: it is the one thing that would let a reader identify every page as
  one hand, or as machine-written. Thinned to the two places carrying a guide's
  largest claim. Keep it there.
- **First person.** Removed. The corpus is narrator-free, and three appearances
  in 29,000 words read as slips rather than as a voice. The impersonal register
  is doing real work for pages whose authority rests on verifiability.
- **The "Try it yourself" link goes before the "In one sentence" box**, always.
- **Chapter cross-references are numbers**, and they go stale the moment a
  chapter is split. After any re-cut, grep `chapter [0-9]` across `lesson.md`,
  `build.py` sandbox blurbs, the tests, and both READMEs.
- **The topic README is hand-written and its chapter table rots silently.** The
  August 2026 re-cut left 26 dead links across five of them before anyone
  looked. A test now pins the table against `build.CHAPTERS` in every topic, so
  the failure mode is loud rather than invisible.
- **A chapter must not open on a pronoun** pointing at the chapter before it.
  Splitting one leaves the second half starting mid-thought — "CVXPY is a layer
  too", "Google OR-Tools is where this gets misread" — and each needs a sentence
  of its own before it earns its number.

## 8 · What a re-cut actually touches

Splitting a chapter is cheap prose and fiddly plumbing. The order that works:

1. `git mv` the `chapters/NN-slug` folders, **highest number first**, so a
   destination is always vacant before it is used.
2. Rewrite `chapter_dir("…")` in `figures/*.py` and the image paths in
   `lesson.md` in the same pass.
3. Update `CHAPTERS` in `build.py`, and the `Sandbox(n, …)` numbers, which are
   chapter numbers and become the sandbox filenames.
4. Update the hardcoded chapter count in `tests/test_lesson.py`, the
   `sandbox/NN.html` links in `lesson.md`, and any sandbox path in the tests.
   Rebuild the chapter table in `<topic>/README.md`; a test will fail until you
   do, and the prose around it ("Eleven chapters on …") is not covered by it.
5. `rm` the orphaned `sandbox/NN.html` files; `build.py` will not clean them.
6. Renumber the `## N · Title` headings, working **downward**, so a new number
   never collides with an old one still waiting to be read.
7. `make publish && make verify`.

A new chapter may be prose-only; nothing enforces a figure per chapter. But a
picture-first repo should not accumulate them. Where a split leaves a two-panel
figure straddling two chapters, split the figure — `queues` fig06 was cut into
`fig06_two_clerks` and `fig09_when_pooling_loses`, fig07 into `fig07_measuring`
and `fig13_coverage`, and `lp-duality` fig09 into `fig09_profit_runs_away` and
`fig10_no_such_plan`. All six read better alone than they did sharing a frame —
but check the result: a panel that was narrow inside a pair usually needs its
margins and limits re-tuned once it is square.

**Outstanding figure debt.** Twenty-nine of the 82 chapters carry no picture.
Some of those are fine — closing chapters and naming chapters never had one —
but these were created by the re-cut and want one: `corners-vs-centre` 6, 7, 8
and 10; `lp-on-gpu` 1, 5 and 6; `solvers` 4, 9, 10 and 12; `queues` 4 and 7;
`branch-and-price` 5, 6 and 7. `solvers` is the guide most short of pictures
overall, with only three across fifteen chapters.

---

## What is deliberately not taken

The constraint that these guides must not read as a copy of the guide that
prompted this note is stronger than any technique in it. Do not adopt: its title
pattern, its "The one thing to remember" box wording (ours is "In one
sentence"), its chapter names, its folder layout, its habit of addressing the
reader as *you* throughout, its register, or its subject matter. The list of
divergences already settled — architecture, visual identity, `sandbox/` over
`play/`, `figures/` over `src/viz/`, `notes/design.md` over
`notes/curriculum.md` — stands.

Technique is fair game. Voice is not.
