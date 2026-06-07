PYTHON := $(shell command -v python3.12 || command -v python3.11 || command -v python3)

.PHONY: generate validate

generate:
	$(PYTHON) scripts/generate_calendar.py

validate: generate
	$(PYTHON) scripts/validate_calendar.py
