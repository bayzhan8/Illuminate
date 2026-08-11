PY      := $(CURDIR)/../.venv/bin/python
FIGURES := $(notdir $(basename $(wildcard figures/fig*.py)))

.PHONY: verify render publish check $(FIGURES)

## verify   re-check every number lesson.md quotes
verify:
	$(PY) -m pytest tests/ -q

## render   regenerate every figure
render: $(FIGURES)

## publish  regenerate chapters/, index.html and sandbox/
publish:
	$(PY) build.py all

## check    render, publish, verify
check: render publish verify

$(FIGURES):
	@cd figures && $(PY) $@.py

help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/^## //'
