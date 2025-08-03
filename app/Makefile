include .env

.PHONY: default aider aider_dryrun install_new install_test llm pre-commit run shell shell_clean test test_verbose test_coverage run_dbs run_hsbc run_uob_bg run_uob_dl run_uob_family
SHELL := /bin/bash

default: test

aider:
	@cd .. && aider app/*.py app/common/*.py app/tests/*.py

aider_dryrun:
	@cd .. && aider --dry-run app/*.py app/common/*.py app/tests/*.py

install_new:
	pipenv install pandas==2.2.2 pyyaml==6.0.1 openpyxl==3.1.3 typer==0.12.3 jsonschema==4.23.0
	pipenv install --dev pytest==8.2.2

llm:
	@test $(INPUT) || ( echo [Usage] make llm INPUT='<input>'; exit 1 )
	@cat ledger.py common/*.py tests/*.py | llm $(INPUT)

pre-commit:
	@pre-commit run --all-files

run:
	pipenv run python ledger.py

shell:
	pipenv shell

shell_clean:
	pipenv --rm

test:
	PYTHONPATH=.:../ pipenv run pytest

test_verbose:
	PYTHONPATH=.:../ pipenv run pytest -v -s

test_coverage:
	PYTHONPATH=.:../ pipenv run pytest --cov=common --cov-report=term-missing

# Bank-specific ledger processing targets
run_dbs:
	pipenv run python ledger.py ../input/dbs.csv ../rules/rules_dbs.yaml

run_hsbc:
	pipenv run python ledger.py ../input/hsbc.csv ../rules/rules_hsbc.yaml

run_uob_bg:
	pipenv run python ledger.py ../input/uob_bg.xls ../rules/rules_uob_bg.yaml

run_uob_dl:
	pipenv run python ledger.py ../input/uob_dl.xls ../rules/rules_uob_dl.yaml

run_uob_family:
	pipenv run python ledger.py ../input/uob_family.xls ../rules/rules_uob_family.yaml