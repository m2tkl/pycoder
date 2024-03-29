MAKEFLAGS += --warn-undefined-variables
.DEFAULT_GOAL := help

# all targets are phony
.PHONY: $(shell egrep -o ^[a-zA-Z_-]+: $(MAKEFILE_LIST) | sed 's/://')

test: ## execute pytest
	rye run pytest -v

testcov: ## execute pytest with coverage
	rye run pytest -v --cov=./src

testout: ## execute pytest and print output
	rye run pytest -v --capture=no

lint: ## execute lint by flake8
	rye run flake8 --exclude 'tests' --show-source ./src

format: ## execute format by autopep8
	rye run autopep8 -ivr . --exclude 'tests'

type: ## execute type check by mypy
	rye run mypy ./pycoder --config-file ./mypy.ini

help: ## Print this help
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

