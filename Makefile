.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
        from urllib import pathname2url
except:
        from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
        match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
        if match:
                target, help = match.groups()
                print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

bandit:
	bandit -r saltapi

black: ## format code with black
	black saltapi tests

clean: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

coverage: ## check code coverage quickly with the default Python
	pytest --cov-report html:htmlcov --cov=saltapi tests/
	$(BROWSER) htmlcov/index.html

flake8: ## check style with flake8
	flake8 saltapi tests

isort: ## sort import statements with isort
	isort saltapi tests

mkdocs: ## start development documentation server
	mkdocs serve

mypy: ## check types with mypy
	mypy --config-file mypy.ini .

pytest: ## run tests quickly with the default Python
	poetry run pytest

start: ## start the development server
	poetry run uvicorn --reload --port 8001 saltapi.main:app

test: ## run various tests (but no end-to-end tests)
	poetry run mypy --config-file mypy.ini .
	poetry run bandit -r saltapi
	poetry run flake8
	poetry run isort --check .
	poetry run black --check .
	poetry run pytest

tox: ## run tests on every Python version with tox
	tox
