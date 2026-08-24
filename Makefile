.PHONY: install test lint help

install:  ## Instala as dependencias
	pip install -r requirements.txt

test:  ## Roda a suite de testes via tox
	tox

lint:  ## Roda o flake8 (le a config em .flake8)
	flake8 .

help:  ## Lista os alvos disponiveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'
