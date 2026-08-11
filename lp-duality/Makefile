# Run these from inside this folder: `cd lp-duality && make test`.
# The virtualenv is shared by every topic and lives at the repository root.
PY ?= $(CURDIR)/../.venv/bin/python

FIGURE_SCRIPTS := $(wildcard figures/fig*.py)

.PHONY: help venv test figures build page chapters sandbox check

help:
	@echo "make venv      create the shared ../.venv and install this topic"
	@echo "make test      re-check every number the lesson quotes"
	@echo "make figures   re-render every image"
	@echo "make build     regenerate the chapters, the page and the sandboxes"
	@echo "make check     figures, build and test, in that order"
	@echo
	@echo "make fig08_the_price_breaks   re-render one chapter's images"

venv:
	python3 -m venv ../.venv
	../.venv/bin/pip install -e ".[dev]"

test:
	$(PY) -m pytest tests/ -q

figures:
	@set -e; for f in $(FIGURE_SCRIPTS); do \
		echo "== $$f"; (cd figures && $(PY) $$(basename $$f)); done

build:
	$(PY) build.py all

chapters:
	$(PY) build.py chapters

page:
	$(PY) build.py page

sandbox:
	$(PY) build.py sandbox

check: figures build test

# `make fig08_the_price_breaks`
fig%:
	cd figures && $(PY) fig$*.py
