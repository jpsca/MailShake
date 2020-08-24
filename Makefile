.PHONY: help
help:
	@echo "clean - remove build/python artifacts"
	@echo "test - run tests"
	@echo "lint - check style with flake8"
	@echo "coverage - generate an HTML report of the coverage"
	@echo "install - install for development"

.PHONY: clean
clean: clean-build clean-pyc

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf pip-wheel-metadata
	rm -rf *.egg-info

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +

.PHONY: test
test:
	python -m pytest -Wd -x mailshake tests

.PHONY: lint
lint:
	python -m flake8 mailshake tests

.PHONY: coverage
coverage:
	python -m pytest --cov-report html --cov mailshake mailshake tests

.PHONY: install
install:
	pip install -e .[dev]
