# Illuminate

Optimisation, drawn.

**[bayzhan8.github.io/Illuminate](https://bayzhan8.github.io/Illuminate/)**

Most of this subject is taught as algebra. Most of it is actually geometry, or
bookkeeping, or a small argument you could sketch on a napkin. These guides
build the sketch first and name it afterwards.

## Guides

**[lp-duality](lp-duality/)** · [read](https://bayzhan8.github.io/Illuminate/lp-duality/) · [play](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/)
Every planning problem has a second problem hiding inside it, about prices, and
solving either one solves both. Where shadow prices come from, and why they
expire.

**[branch-and-price](branch-and-price/)** · [read](https://bayzhan8.github.io/Illuminate/branch-and-price/) · [play](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/)
A cutting-stock model with four trillion variables that fits on a napkin.
Column generation asks the prices which variable is missing rather than
searching for it; branch-and-price puts that loop inside a search tree.

Queued: simplex against interior point · branch and bound and branch and cut ·
Benders decomposition · what solvers actually do (and why presolve is where the
gap opens) · LP on the GPU · queues and Little's law.

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

Read `.claude/skills/new-topic/SKILL.md` first. Short version: find the worked
example by computation before writing a word of prose, then write `lesson.md`,
then let `build.py` generate the rest. Register the folder in `TOPICS` here, in
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
