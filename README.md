# Illuminate

*Operations research, from nothing, with pictures that move.*

**[bayzhan8.github.io/Illuminate](https://bayzhan8.github.io/Illuminate/)**

Optimisation is full of ideas that are genuinely simple once you can see them,
and that are usually introduced as a page of algebra with a *hence* in the
middle. This is an attempt at the other order: build the picture first, move it
around until it is obvious, and only then say what everyone else calls it.

Every number on every page is computed by the code in this repository, in exact
arithmetic, and re-checked by its tests. If a number in the prose ever stops
matching what the code produces, `make test` fails.

## Topics

| Topic | What it is about | |
|---|---|---|
| [lp-duality](lp-duality/) | Every planning problem has a second problem hiding inside it, about prices, and solving either one solves both. It is where shadow prices come from, and it is the engine inside most of the methods below. | [read](https://bayzhan8.github.io/Illuminate/lp-duality/) · [play](https://bayzhan8.github.io/Illuminate/lp-duality/sandbox/) |
| [branch-and-price](branch-and-price/) | A model with four trillion variables that fits on a napkin. Column generation asks the prices which variable is missing instead of searching for it; branch-and-price puts that loop inside a search tree. | [read](https://bayzhan8.github.io/Illuminate/branch-and-price/) · [play](https://bayzhan8.github.io/Illuminate/branch-and-price/sandbox/) |

### Planned

Each of these leans on duality, which is why that one came first.

- **Simplex against interior point** — walking the corners against cutting through the middle
- **Branch and bound** and **branch and cut** — the tree, and what pruning actually prunes
- **Benders decomposition** — generating rows instead of columns
- **LP on the GPU** — why simplex resists parallel hardware, and what first-order methods changed
- **Queues and Little's law** — why the wait explodes long before the servers are full

## How a topic is laid out

```
<topic>/
  README.md      the topic's front page and chapter list
  lesson.md      the prose, and the only place it exists
  build.py       lesson.md -> chapter files, the web page, the sandboxes
  chapters/      one folder per chapter: a generated README and its images
  figures/       one script per chapter, writing into chapters/
  sandbox/       generated pages you can push around, no server needed
  src/           the code behind every number
  tests/         the maths, the prose-against-the-code, the JS-against-the-Python
  notes/         why it is built the way it is
```

`illuminate/` is a small shared package: the house style for every figure, the
typeface, and the machinery that turns a `lesson.md` into chapter files, a web
page and its sandboxes. A topic supplies configuration, not a copy of the
build.

Two more things live at the root because they have to. `index.html` and `assets/`
are the published site — GitHub Pages serves this repository from its root,
which means a figure has exactly one home and the image paths in `lesson.md`
are the same paths the published page uses. `.venv/` is one shared virtualenv
for every topic.

## Running it

```bash
make venv     # create .venv and install every topic
make test     # re-check every number every topic quotes
make figures  # re-render every image
make docs     # regenerate the chapter files, pages and sandboxes
```

Or work inside one topic:

```bash
cd lp-duality
make test
make check    # figures, then build, then test
```

Python 3.10 or later. `node` is optional — without it, the tests that run the
interactive pages' JavaScript against the Python are skipped and everything
else still runs.

## Adding a topic

1. Create the folder following the layout above, and add it to `TOPICS` in the
   root [Makefile](Makefile).
2. Add it to the table above and to the list in [index.html](index.html).
3. Write `lesson.md` first. The chapters, the page and the sandboxes are all
   generated from it, and the tests will not let them drift.

## Why bother

Two reasons.

The first is that these ideas are more useful outside the field than inside it.
"What is this bottleneck actually costing me, and how far can I trust that
number" is a question almost every organisation has and almost nobody phrases
that way. The mathematics that answers it is a century old and mostly locked
behind notation.

The second is that a picture you can move is a different kind of object from a
picture. Reading that a price collapses when a different constraint takes over
is weaker than dragging the slider until it happens to you. So the animations
are not decoration on the argument; where they exist, they are the argument,
and where they would only have been decoration there is a chart instead.

## Licence

Code and prose: MIT. The vendored copy of IBM Plex Mono in
`illuminate/src/illuminate/fonts/` is under the SIL Open Font Licence 1.1,
included alongside it.
