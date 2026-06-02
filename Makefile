SHELL := /bin/bash

.PHONY: lint test molecule

lint:
	python3 -m pip install -r requirements.txt
	ansible-lint

test:
	python3 -m pip install -r requirements.txt
	molecule test

molecule:
	python3 -m pip install -r requirements.txt
	molecule converge
