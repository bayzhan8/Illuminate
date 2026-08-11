TOPICS  := lp-duality branch-and-price queues lp-on-gpu corners-vs-centre
VENV    := $(CURDIR)/.venv
PIP     := $(VENV)/bin/pip

.PHONY: bootstrap verify render publish list $(TOPICS)

## bootstrap  install the shared package and every topic into .venv
bootstrap:
	python3 -m venv $(VENV)
	$(PIP) install -q -e ./illuminate
	$(PIP) install -q pytest
	$(PIP) install -q --no-deps $(TOPICS:%=-e ./%)

## verify     run every topic's tests
verify: $(TOPICS:%=verify-%)
verify-%:
	@echo "-- $*"
	@$(MAKE) --no-print-directory -C $* verify

## render     regenerate every figure
render: $(TOPICS:%=render-%)
render-%:
	@echo "-- $*"
	@$(MAKE) --no-print-directory -C $* render

## publish    regenerate every chapter file, page and sandbox
publish: $(TOPICS:%=publish-%)
publish-%:
	@echo "-- $*"
	@$(MAKE) --no-print-directory -C $* publish

## list       show the topics
list:
	@printf '%s\n' $(TOPICS)

help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/^## //'
