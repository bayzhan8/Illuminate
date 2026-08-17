# Illuminate

Optimisation, drawn.

**[bayzhan8.github.io/Illuminate](https://bayzhan8.github.io/Illuminate/)**

Most of this subject is taught as algebra. Most of it is actually geometry, or
bookkeeping, or a small argument you could sketch on a napkin. These guides
build the sketch first and name it afterwards.

## Guides

Numbered in the order they build on each other. The first five are one
chain and are best read in sequence; queues stands on its own and can be
read at any point.

**[lp-duality](lp-duality/)** · [read](https://bayzhan8.github.io/Illuminate/lp-duality/) · [play](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/)
Every planning problem has a second problem hiding inside it, about prices, and
solving either one solves both. Where shadow prices come from, and why they
expire.

**[corners-vs-centre](corners-vs-centre/)** · [read](https://bayzhan8.github.io/Illuminate/corners-vs-centre/) · [play](https://bayzhan8.github.io/Illuminate/corners-vs-centre/sandbox/)
A shape built in 1972 to embarrass the simplex method, which it does: ten
dimensions, 1024 corners, and the method stops at every one. Nobody has met one
in practice in seventy years. Why the bad case is real, why it never happens,
and why the method built to dodge it never lands on a corner at all.

**[lp-on-gpu](lp-on-gpu/)** · [read](https://bayzhan8.github.io/Illuminate/lp-on-gpu/) · [play](https://bayzhan8.github.io/Illuminate/lp-on-gpu/sandbox/)
Two runs on the same problem, same step sizes, differing by one term in one
line: one lands on the answer, the other swings between $0 and $753 forever.
Why linear programming had to change algorithms when machines started getting
wider instead of faster.

**[branch-and-price](branch-and-price/)** · [read](https://bayzhan8.github.io/Illuminate/branch-and-price/) · [play](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/)
An order of boards takes seven, and proving six is impossible is far harder
than finding a way to do it in seven. Column generation asks the prices which
unknown is missing rather than searching four trillion of them for it;
branch-and-price puts that loop inside a search tree.

**[solvers](solvers/)** · [read](https://bayzhan8.github.io/Illuminate/solvers/) · [play](https://bayzhan8.github.io/Illuminate/solvers/sandbox/)
Hand a solver a twenty-row model and it deletes thirteen of the rows before any
algorithm runs, and settles one of the decisions by arithmetic. What presolve
is, why it is where the gap opens, and which solvers you can actually deploy
without a licence server ruining your week.

**[queues](queues/)** · [read](https://bayzhan8.github.io/Illuminate/queues/) · [play](https://bayzhan8.github.io/Illuminate/queues/sandbox/)
A clerk who gets through the average customer in six minutes will hand someone
a wait of an hour without ever slowing down. Little's law as one region
measured twice, why variability rather than utilisation does the damage, and a
95% confidence interval that covers 9%.

Queued: branch and bound and branch and cut · Benders decomposition.
Branch and bound is the next one to write: three of the guides above already
lean on it, which is the only place in the repository where a guide asks the
reader to take something on trust.

## Repository map

| path | what it holds |
|---|---|
| `<topic>/lesson.md` | the prose. The only place it exists |
| `<topic>/build.py` | the topic's configuration: chapter names, sandbox definitions |
| `<topic>/chapters/` | generated per-chapter READMEs, and the images belonging to each |
| `<topic>/figures/` | one script per chapter, writing into `chapters/` |
| `<topic>/sandbox/` | generated client-side pages |
| `<topic>/src/` | the code behind every number |
| `<topic>/tests/` | maths · prose-against-code · JavaScript-against-Python |
| `<topic>/notes/` | the decision log |
| `notes/craft.md` | the prose rules every guide is written to |
| `illuminate/` | shared package: figure style, typeface, and the `lesson.md` → site machinery |
| `index.html`, `assets/` | the published site |

Pages serves from the repository root rather than a `docs/` folder. [^1]

[^1]: Which means an image has one location, and the paths written in
`lesson.md` are the paths the published page requests. Serving from `docs/`
would require either duplicating every figure or rewriting every link.

## Build

```bash
make bootstrap    # .venv, shared package, all topics
make verify       # every topic's tests
make render       # every figure
make publish      # every chapter file, page and sandbox
```

Inside one topic: `make check` runs render, publish and verify in that order.

Python 3.10+. `node` is optional; without it the tests that execute the
sandbox JavaScript are skipped and everything else runs.

## Adding a guide

Read `.claude/skills/new-topic/SKILL.md` and `notes/craft.md` first. Short
version: find the worked example by computation before writing a word of prose,
then write `lesson.md` one small idea per chapter, then let `build.py` generate
the rest. Register the folder in `TOPICS` here, in
the list above, and in `index.html`.

## The standard

Every number in every guide is produced by the code beside it, in exact
rational arithmetic, and asserted by a test. Where a result can be reached by a
second route that shares no code with the first, it is: the simplex answers are
checked against brute-force vertex enumeration, column generation against
solving the full model, branch-and-price against exhaustive integer search.

That habit is not decoration. It caught two bugs in branch-and-price that
returned confident wrong answers on 476 of 1230 instances, and both are now
written up in the guide itself.

## Licence

MIT for code and prose. The bundled IBM Plex Mono in
`illuminate/src/illuminate/fonts/` is SIL OFL 1.1, licence included alongside.
