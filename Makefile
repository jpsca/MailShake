.PHONY: clean-pyc clean-build

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "test - run tests with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - show a coverage report"
	@echo "publish - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

test:
	py.test -x tests

testcov:
	py.test --cov-config .coveragerc --cov mailshake tests/

test-all:
	tox

coverage:
	py.test --cov-config .coveragerc --cov-report html --cov mailshake tests/
	open htmlcov/index.html

flake:
	flake8 mailshake tests

publish: clean
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist
