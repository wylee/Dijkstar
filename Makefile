venv ?= .venv

$(venv):
	python3 -m venv $(venv)
	$(venv)/bin/pip install --upgrade --upgrade-strategy eager pip

init: $(venv)
	$(venv)/bin/pip install --editable .[dev,server]
	$(venv)/bin/run test

.PHONY = init
