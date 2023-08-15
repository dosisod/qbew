.PHONY: black install isort mypy ruff test typos

all: typos ruff mypy black isort test

install:
	pip install -e .
	pip install -r dev-requirements.txt

ruff:
	ruff qbew test

mypy:
	mypy -p qbew
	mypy -p test

black:
	black qbew test --check --diff

isort:
	isort . --diff --check

typos:
	typos --format brief

test:
	pytest

fmt:
	ruff qbew test --fix
	isort .
	black qbew test

clean:
	rm -rf .mypy_cache .ruff_cache
