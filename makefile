# .PHONY is a special target in Make, which allows you to define commands that are not file-based targets.
# It ensures these "phony" targets get executed even if there's a file/folder with the same name.
.PHONY: install run_prod run_dev create_tables help

# This target when called displays the available make targets and their descriptions.
help:
	@echo "Available targets:"
	@echo "  install       - Install required dependencies"
	@echo "  run_prod      - Run the FastAPI application in production mode"
	@echo "  run_dev       - Run the FastAPI application in development mode with hot-reloading"
	@echo "  create_tables - Create the necessary tables in the database"

# The 'install' target installs the dependencies listed in the requirements.txt file using pip.
install:
	pip install -r requirements.txt

# The 'run_prd' target runs the FastAPI application in production mode using uvicorn.
# It binds the app to all network interfaces (0.0.0.0) on port 5000 and uses 2 workers for handling requests.
run_prd:
	uvicorn src.main:app --port 5000 --workers 8

# The 'run_dev' target runs the FastAPI application in development mode with hot-reloading enabled using uvicorn.
# It also binds the app to all network interfaces (0.0.0.0) on port 5000.
run_dev:
	uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload 
