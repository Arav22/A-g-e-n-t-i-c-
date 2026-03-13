#makefile
PYTHON ?= python
PROMPT ?= Count words in: hello world from agentic ai

.PHONY: install lint test run

install:
	$(PYTHON) -m pip install -e .[dev]

lint:
	ruff check src tests
	mypy src

test:
	pytest

run:
	$(PYTHON) -m agentic_ai --prompt "$(PROMPT)"
