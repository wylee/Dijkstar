venv ?= .venv

$(venv):
	python3 -m venv $(venv)
	$(venv)/bin/pip install --upgrade pip setuptools

init: $(venv)
	$(venv)/bin/pip install -e .[dev]

test:
	$(venv)/bin/coverage run --source dijkstar -m unittest discover .
	$(venv)/bin/coverage report --show-missing
	flake8 .

.PHONY = init test
