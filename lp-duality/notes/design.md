# How this topic is put together

Notes to myself, and to whoever writes the next topic. The rules here are not
general truths about teaching; they are the decisions this guide made, and the
reasons, so that the next one can make them again on purpose or break them on
purpose.

## Who it is for

Someone who has never met a linear program and has no reason to care about one
yet. Not someone who is slow — someone who is busy. The test of a paragraph is
whether a person who last did algebra at school gets through it without
stopping, and whether someone who teaches this for a living would still call it
correct.

## The order, and why it is that order

Most introductions define the dual and then prove things about it. That order
is efficient and it is the wrong way round, because a reader who has been
handed a definition has no idea why anyone would want it.

So the dual is not defined until it has been made necessary. Chapter 2 spends
its whole length establishing that no amount of searching can ever prove you
are finished. Only then, in chapter 3, does a price list appear — as the answer
to a question the reader now has.

1. **The workshop** (1) makes the problem concrete before anything is claimed.
2. **You cannot check** (2) creates the need. Nothing else happens in it.
3. **Charging for the ingredients** (3) invents the dual, without saying so.
4. **Every honest price list is a ceiling** (4) is weak duality, as two
   separate gaps with two separate reasons rather than one line of algebra.
5. **They always meet** (5) is the theorem, plus 320 pieces of evidence and a
   plain statement that evidence is not proof.
6. **Who is binding** (6) and **what one more is worth** (7) are the payoff:
   the two things practitioners actually use the dual for.
7. **The price is only local** (8) takes the payoff back to a safe size.
8. **When it goes wrong** (9) fences the theorem's conditions, and gets Farkas
   in through the side door where it belongs.
9. **Where this leads** (10) exists because this topic is the foundation of the
   next four in this repository, and a reader who finishes should know that.

## Rules kept

- **No equations in the prose.** Every relation is a picture or a sentence. The
  program itself appears once, as a table of recipes and stock, because that is
  a shopping list rather than notation.
- **Nothing invented stays invented.** "Plan", "price list", "ceiling" and the
  rest all appear in the glossary against their standard names, so a reader can
  put this down and pick up a textbook without a translation problem.
- **Motion only where the motion is the argument.** Six figures move: the two
  regions converging, the profit line sweeping, the price bars covering their
  products, the two ladders closing, and the plank line sliding until its price
  dies. Five are static charts. A moving figure that could have been a still is
  a figure that makes the reader wait for nothing.
- **A picture made only of words is not a picture.** The three-way comparison
  in chapter 4 is a real chart with real lengths. The glossary and the "where
  this leads" list are tables and bullets, because that is what they are, and
  rendering them as images would only make them unsearchable.
- **Every animation pauses on its conclusion.** The last frame is the one
  carrying the answer, and it is held for three seconds before the loop
  restarts.
- **Do not oversell.** Chapter 5 says outright that 320 examples are not a
  proof. Chapter 8 exists mainly to stop a reader walking away thinking a
  shadow price is a constant. Chapter 9 names degeneracy so that a reader who
  meets a non-unique price in the wild recognises it instead of assuming the
  solver is broken.

## Choices in the code

- **Exact fractions everywhere.** The entire guide turns on two numbers being
  equal. In floating point one of them arrives as 349.99999999999994 and the
  central claim silently becomes a claim about a tolerance. `Fraction` costs
  nothing at this size and makes "the gap is zero" a literal statement.
- **Bland's rule**, which is the slow pivoting rule, because it is the one that
  provably cannot cycle. A solver that hangs on a degenerate example is a bad
  thing to hand a beginner, and chapter 9 is about degenerate examples.
- **Prices are recovered by solving `Bᵀy = c_B` against untouched columns**,
  not read out of the final tableau. The tableau accumulates sign conventions
  and getting one backwards produces a plausible wrong answer. The test then
  checks that number against the dual program solved from scratch, so two
  independent routes have to agree.
- **A brute-force corner search exists purely to disagree with the simplex
  code.** It shares nothing with it. On two-variable problems the tests run
  both.
- **The value curve refuses rather than guesses.** Its bends are found by
  sampling, and a bend almost never lands on a sample: this example bends at
  316/7, the grid steps from 45 to 45.5, and the straddling pair reads as a
  slope belonging to neither piece. Single-interval runs are therefore treated
  as straddles, every bend is re-solved to confirm it, and a grid too coarse to
  corroborate anything raises instead of returning a smooth-looking wrong
  curve.

## Choices in the drawing

- **Two colours, and they mean the same thing on every page.** Blue is a plan,
  rust is a price. They were picked by running candidates through a
  colour-vision simulator rather than by eye; the pair stays more than twenty
  perceptual units apart under protanopia, deuteranopia and tritanopia, in both
  light and dark. Green is a status mark only, never a third series, and never
  without a word or a tick next to it.
- **The figures do not follow the page into dark mode.** They are rendered on
  cream with black ink and matted in a plate that stays cream in both schemes.
  Inverting them would mean re-validating the colour pair against a second
  surface for no gain; a mat costs nothing and reads as deliberate.
- **The typeface ships with the repository.** IBM Plex Mono is under the SIL
  Open Font Licence and lives in `assets/fonts/`, so a clone renders the same
  figures as this machine did instead of substituting whatever monospace it
  finds.
- **Tracking is done with hair spaces.** Matplotlib has no letter-spacing, and
  the site sets these small headings at 0.12em. A plain space is a quarter em
  and doubles the width of a heading; a hair space is about a tenth and lands
  close.
- **GIFs are re-encoded onto one shared palette.** Matplotlib writes
  anti-aliased frames in full colour and the encoder then stores thousands of
  near-identical creams. One palette sampled across the whole animation, with
  dithering off and no disposal method set, cuts these to roughly a quarter of
  their size with nothing visible lost. Setting a disposal method undoes all of
  it — that makes every frame a full repaint.

## What the tests are actually for

Three separate jobs, deliberately kept apart:

- `test_lp.py` — the mathematics. Checked against a second implementation
  wherever one is possible.
- `test_lesson.py` — the prose against the code. Every figure in the text
  exists and every figure on disk is used; every number typed into a sentence
  still matches what the program produces; the generated chapter files match
  what `build.py` would write today. These are the failures that are invisible
  by inspection, because the page still reads perfectly while being wrong.
- `test_sandbox.py` — the JavaScript against the Python. The interactive pages
  re-implement the corner search, so both are run over the same inputs. Where a
  corner is degenerate the check is that the page's prices are honest and
  charge the same bill, not that they are the identical vector — because there
  the prices genuinely are not unique, and demanding a match would be
  demanding the wrong thing.
