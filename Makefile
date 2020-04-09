current_dir = $(shell pwd)

PROJECT = covid_graphs
VERSION ?= latest

.POSIX:
check:
	!(grep -R /tmp ./tests)
	flake8 --count ${PROJECT}
	pylint ${PROJECT}
	black --check ${PROJECT}

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -s
