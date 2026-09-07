.PHONY: install test test-python test-web build validate

install:
	python -m pip install -e ".[dev]"
	pnpm install

test: test-python test-web

test-python:
	python -m pytest

test-web:
	pnpm --dir apps/viewer test -- --run

build:
	pnpm --dir apps/viewer build

validate:
	abb validate fixtures/traces/incident_triage.json
