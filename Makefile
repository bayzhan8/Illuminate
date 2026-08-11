# Repository root. Every topic is a self-contained folder with its own Makefile.
# Add a new topic by creating its folder and adding its name here.
TOPICS := lp-duality branch-and-price

VENV := $(CURDIR)/.venv

.PHONY: help venv test figures docs topics

help:
	@echo "make venv      create the shared .venv and install every topic"
	@echo "make test      run the tests of every topic"
	@echo "make figures   re-render the figures of every topic"
	@echo "make docs      regenerate every topic's chapters, page and sandboxes"
	@echo "make topics    list the topics in this repo"
	@echo
	@echo "To work on one topic:  cd lp-duality && make test"

topics:
	@for t in $(TOPICS); do echo "$$t"; done

venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -e ./illuminate
	@set -e; for t in $(TOPICS); do $(VENV)/bin/pip install -q --no-deps -e "./$$t[dev]"; done
	$(VENV)/bin/pip install -q pytest

test:
	@set -e; for t in $(TOPICS); do echo "== $$t"; $(MAKE) -C $$t test; done

figures:
	@set -e; for t in $(TOPICS); do echo "== $$t"; $(MAKE) -C $$t figures; done

docs:
	@set -e; for t in $(TOPICS); do echo "== $$t"; $(MAKE) -C $$t build; done
