r:
	PYTHONPATH=./src uvicorn main:app --host localhost --port 8000  --reload


run_services:
	docker compose -f docker-compose_services.yml up --build

lint-fix:
	@echo "Fixing issues with linters (black, isort, flake8)..."
	@isort .
	@flake8 . --ignore=E501
	@black . --target-version py310 --line-length 100 --extend-exclude "/(k_env|env|venv)/"
	@echo "Linting is complete"