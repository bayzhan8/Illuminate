---
name: new-topic
description: Author a new Illuminate topic (a chapter/page explaining an OR or optimisation idea) end to end - curriculum, exact-arithmetic code, figures, interactive sandboxes, tests, and publishing. Use when adding a topic to this repo, drafting a lesson.md, writing figure scripts, or when asked to explain an optimisation method as a visual guide.
---

# Building a topic

A topic is a guide to one idea: a `lesson.md`, the code that computes every
number in it, figures generated from that code, pages the reader can push
around, and tests that stop the three from drifting apart.

Read this before writing anything. The order below is the order to work in, and
most of the failure modes come from doing it out of order.

## The rule that everything else serves

**Nothing on the page is typed in by hand.** Every number in the prose is
computed by the code beside it, in exact arithmetic, and a test asserts the
prose still matches. Every figure is rendered by a script. Every chapter file
and HTML page is generated from `lesson.md`.

This is not tidiness. It is the only thing that makes the guide trustworthy
after the third edit, and it is what lets a reader take the numbers seriously.

## Work in this order

### 1. Find the example before writing a word

The example is the topic. Pick it by computation, not by taste, and do it
first. Writing prose around an example that turns out not to demonstrate the
point is the most expensive mistake available here.

Search for an instance that satisfies every property the story needs, and
verify it in a throwaway script before committing to it. Things worth
requiring:

- **small enough to draw.** Two variables if there is a region to show, or few
  enough rows to print in full
- **not symmetric.** Asymmetry is what gives a phenomenon something to say.
  The duality topic needs one constraint with slack at the optimum, or
  complementary slackness is a sentence with no picture
- **the numbers land.** The answer should be exact and quotable, with
  intermediate quantities a reader can hold in their head
- **the phenomenon actually occurs.** If the chapter claims a bound is too
  weak, find an instance where rounding it really does give the wrong answer.
  Never assert a gap you have not computed

Worked precedent: the branch-and-price topic needed an instance where the
naive relaxation cannot rule out an answer the pattern relaxation can. A search
over a few thousand candidates found `W=25, widths (4,9,10), demands (3,6,7)`,
where ⌈naive⌉ = 6 and ⌈Dantzig-Wolfe⌉ = 7 = the answer. Without that search
the chapter would have been an assertion.

Keep a second, larger instance for the chapter that shows scale, and a third
you never solve at all if you need to quote a number like "four trillion".

### 2. Write the curriculum notes, not the prose

Read `notes/craft.md` at the repository root first. It holds the prose rules
every guide is written to — one idea per chapter and how to test for that,
the hope-then-the-thing-that-kills-it shape, giving the reader arithmetic
they can check by hand, announcing the notation budget, the tics to avoid,
and the mechanical order for re-cutting chapters later.

Then `notes/design.md`, before `lesson.md`. Decide and write down:

- **who it is for.** Assume no background and full intelligence. The test of a
  paragraph is whether a busy person who last did algebra at school gets
  through it without stopping, and whether a specialist would still call it
  correct
- **the chapter order, and why it is that order.** The usual mistake is
  defining the object and then motivating it. Reverse that: spend a whole
  chapter establishing that the reader *needs* something before naming it. In
  lp-duality, chapter 2 does nothing but demonstrate that search can never
  prove optimality; the dual arrives in chapter 3 as the answer to a question
  the reader now has
- **where the difficulty is allowed to spike**, and what you will do about it
- **what you will refuse to claim**

### 3. Write the code, with a second opinion built in

Exact arithmetic throughout: `fractions.Fraction`, never floats. The guides
turn on quantities being *equal*, and in floating point "the gap is zero"
silently becomes "the gap is under a tolerance", which is a different and much
weaker sentence.

**Every important claim needs two independent routes to the same answer.**
Not a test that re-runs the same function; a genuinely different method:

- simplex checked against brute-force vertex enumeration
- the dual read from the tableau checked against solving the dual as a fresh LP
- column generation checked against solving the master over every column
- branch-and-price checked against brute-force integer optimisation

These are hopeless at any real size, which is exactly why they belong in tests
that run only on toy instances. This is the highest-value habit in the
repository: it caught two bugs in branch-and-price that produced plausible
wrong answers on 476 of 1230 instances while every tree looked sensible.

Prefer a slow, obviously-correct algorithm over a fast subtle one. Bland's rule
is used for pivoting because it cannot cycle, not because it is quick.

**When a computation cannot be trusted, it must refuse rather than guess.** The
value-function reconstruction raises when the sampling grid is too coarse to
distinguish a real segment from a straddled bend, because returning a
smooth-looking wrong curve is worse than returning nothing.

### 4. Figures: only animate when the motion is the argument

Import the house style from `illuminate.draw`. Never set a colour by hand.

- **blue is a plan / primal, rust is a price / dual**, on every page of every
  topic. That pair was validated with a colour-vision simulator and holds up
  over 20 perceptual units apart under all three common CVD types in both
  light and dark. Green is a *status* mark only. Never a third data series,
  and never without a word or tick beside it
- **animate only where the motion carries the argument.** A converging gap, a
  sweeping objective line, a capacity sliding until its price dies. If a still
  would say the same thing, make a still. Roughly half of each topic's figures
  should be static
- **every animation pauses on its conclusion.** `animate(..., hold=3.0)`; the
  encoder collapses the repeats into one long frame at no cost in bytes
- **a diagram of labelled boxes is not a diagram.** If the graphical content is
  zero, render it as a table: searchable, selectable, legible to a screen
  reader, and no re-render needed when a word changes
- **direct-label the marks.** Colour is never the only cue
- figures render on cream and are matted in a bordered plate that stays cream
  in dark mode. They do not invert

Check every figure by rendering it and *looking at it*. Label collisions,
overflowing callouts and text sitting on lines are invisible in the source and
obvious in the image. Extract the last frame of a GIF and look at that too.

### 5. Write lesson.md

Structure: an H1, a short opening that states the payoff in plain terms, then
chapters delimited by `---` with headings of the exact form `## N · Title`.
Everything after the last chapter is the tail: glossary, further reading, how
to run the code.

Rules that have earned their place:

- **keep algebra out of the running text.** State relations as a drawing or
  as a sentence. The model itself may appear once as a table of quantities,
  which reads as a shopping list rather than as notation
- **every invented phrase gets its real name**, in a glossary table at the end,
  so a reader can put the guide down and pick up a textbook
- **one word, one meaning.** If "price" means a dual variable, it never also
  means a market price in the same passage
- **state the strength of the evidence.** A figure showing 320 instances of a
  theorem is not a proof, and the text has to say so. Budget a full chapter for
  what the result does not claim
- **write up the bugs.** When a subtle failure cost real answers, put it in the
  lesson. It is the most valuable content on the page and it is the part no
  textbook includes
- state the tolerance, the range, the assumption. A shadow price without its
  validity range is the most common way these ideas get misused

### 6. Sandboxes

One per chapter that has a number worth moving. Declare them in `build.py` as
`Sandbox(...)`; the shell, the theming and the drawing helper come from
`illuminate.site`.

The JavaScript re-implements part of the Python, because the pages run with no
server. **That duplication must be tested against the Python** — two copies of
a formula drift the moment one is edited alone. Run the page's own source
through `node` in a test and compare at a spread of inputs.

Where the mathematics is genuinely non-unique (degenerate corners, multiple
optimal dual solutions), test the property rather than the vector: that the
page's prices are feasible and give the same objective, not that they match
element by element.

### 7. Tests, in three separate jobs

Keep them in separate files, because they fail for different reasons:

- `test_<topic>.py` — the mathematics, against independent implementations
- `test_lesson.py` — the prose against the code. Every figure referenced
  exists; every figure on disk is referenced; alt text is a real description;
  every number quoted in a sentence still matches what the code produces; the
  generated chapter files match what `build.py` would write today
- `test_sandbox.py` — the JavaScript against the Python

The middle one catches the failures that are invisible by inspection, because
the page still reads perfectly while being wrong.

### 8. Wire it up

```bash
cd <topic> && make check          # render, publish, verify
```

Then add the topic to `TOPICS` in the root `Makefile`, to the table in the root
`README.md`, and to the landing page `index.html`. Run `make verify` from the
root, commit, push. GitHub Pages serves from the repository root, so images
have one home and the paths in `lesson.md` are the paths the site uses.

## Register

Write like someone who knows the subject explaining it to a colleague across a
table. Concretely:

- **vary sentence length a lot.** Uniform rhythm is the loudest tell of
  machine-written prose. Follow a long qualified sentence with a three-word one
- **no formulaic connectives.** Not "Moreover", "Furthermore", "It's worth
  noting that", "Let's dive in", "In conclusion"
- **avoid the "not just X, it's Y" construction** and the rule-of-three list.
  Both are addictive and both read as generated
- **cut sentences that restate the previous sentence.** One idea, said once
- **be specific rather than enthusiastic.** "It bends at 316/7" beats "the
  results are quite striking"
- **let the reader draw the conclusion** where the picture already made it
- **admit things.** "This rule is weak, here is what practice uses instead"
  is worth more than a confident summary
- **watch em-dash density.** Target under 3 per thousand words. The published
  lessons run at 0; the first drafts ran at 8. Convert most to full stops, a
  few to colons or parentheses

## What not to do

- do not hand-edit anything under `chapters/`, `index.html`, or `sandbox/` —
  they are generated, and a test will fail
- do not ship a figure whose content is entirely typography
- do not quote a number you have not computed
- do not claim a phenomenon you have not found an instance of
- do not introduce a third and fourth data colour; use shading, position or
  labels instead
- do not copy another topic's `build.py` wholesale — it is configuration, and
  the machinery belongs in `illuminate/`
