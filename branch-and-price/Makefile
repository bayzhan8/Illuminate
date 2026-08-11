# Run these from inside this folder: `cd branch-and-price && make test`.
PY ?= $(CURDIR)/../.venv/bin/python

FIGURE_SCRIPTS := $(wildcard figures/fig*.py)

.PHONY: help venv test figures build chapters page sandbox check

help:
	@echo "make test      re-check every number the lesson quotes"
	@echo "make figures   re-render every image"
	@echo "make build     regenerate the chapters, the page and the sandboxes"
	@echo "make check     figures, build and test, in that order"

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

fig%:
	cd figures && $(PY) fig$*.py
