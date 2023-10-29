# Variables
DEV_REQUIREMENTS_PATH = requirements/dev.txt
LOG_PATH = log
PIP = $(PYTHON) -m pip
PORT = 5000
PYTHON = python3
PYTEST = $(PYTHON) -m pytest
REQUIREMENTS_PATH = requirements.txt
SERVICE_PATH = src
SQLITE_PATH = _sqlite_db
TESTS_PATH = src/tests
VENV_PATH = _venv
WORKERS = 8

.PHONY: autoflake create_tables help install isort run_dev run_prod test 

autoflake:
    autoflake --in-place --remove-all-unused-imports -r $(SERVICE_PATH)

create_tables:
    @echo "Creates necessary tables in the database"

help:
    @echo "Available targets:"
    @echo "  autoflake     - Removes unused imports"
    @echo "  create_tables - Creates necessary tables in the database"
    @echo "  help          - Displays this help message"
    @echo "  install       - Installs dependencies"
    @echo "  isort         - Sorts imports"
    @echo "  run_dev       - Runs FastAPI application in development mode with hot-reloading"
    @echo "  run_prod      - Runs FastAPI application in production mode"
    @echo "  test          - Run tests"

install:
    $(PIP) install -r $(REQUIREMENTS_PATH)

isort:
    isort $(SERVICE_PATH)
    isort $(TESTS_PATH)

run_dev:
    uvicorn $(SERVICE_PATH).main:app --host 0.0.0.0 --port $(PORT) --reload 

run_prod:
    uvicorn $(SERVICE_PATH).main:app --port $(PORT) --workers $(WORKERS)

test:
    $(PYTEST) 
