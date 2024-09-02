include .env

.PHONY: default aider aider_dryrun install_new install_test llm run shell shell_clean test test_verbose
SHELL := /bin/bash

default: test

aider:
	@cd .. && aider app/*.py app/common/*.py app/tests/*.py

aider_dryrun:
	@cd .. && aider --dry-run app/*.py app/common/*.py app/tests/*.py

install_new:
	pipenv install pandas==2.2.2 pyyaml==6.0.1 openpyxl==3.1.3 typer==0.12.3
	pipenv install --dev pytest==8.2.2

llm:
	@test $(INPUT) || ( echo [Usage] make llm INPUT='<input>'; exit 1 )
	@cat ledger.py common/*.py tests/*.py | llm $(INPUT)

run:
	python ledger.py

shell:
	pipenv shell

shell_clean:
	pipenv --rm

test:
	PYTHONPATH=.:../ pytest

test_verbose:
	PYTHONPATH=.:../ pytest -v -s