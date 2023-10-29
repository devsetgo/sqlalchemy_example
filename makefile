# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

SERVICE_PATH = src
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

VENV_PATH = _venv
REQUIREMENTS_PATH = requirements.txt
DEV_REQUIREMENTS_PATH = requirements/dev.txt

.PHONY: install run_prod run_dev create_tables help black isort autoflake

autoflake:
	autoflake --in-place --remove-all-unused-imports -r $(SERVICE_PATH)

black:
	black $(SERVICE_PATH)
	black $(TESTS_PATH)

cleanup: isort black autoflake


help:
	@echo "Available targets:"
	@echo "  install       - Install required dependencies"
	@echo "  prod      	   - Run the FastAPI application in production mode"
	@echo "  dev           - Run the FastAPI application in development mode with hot-reloading"
	@echo "  create_tables - Create the necessary tables in the database"
	@echo "  black         - Format code using black"
	@echo "  isort         - Sort imports using isort"
	@echo "  autoflake     - Remove unused imports and variables"

isort:
	isort $(SERVICE_PATH)
	isort $(TESTS_PATH)

install:
	$(PIP) install -r $(REQUIREMENTS_PATH)


prd:
	uvicorn $(SERVICE_PATH).main:app --port 5000 --workers 8

dev:
	uvicorn $(SERVICE_PATH).main:app --host 0.0.0.0 --port 5000 --reload 

test:
	$(PYTEST)



