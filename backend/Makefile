r:
	PYTHONPATH=./src uvicorn main:app --host localhost --port 8000  --reload


run_services:
	docker compose -f docker-compose_services.yml up --build

lint-fix:
	@echo "Fixing issues with linters (ruff)..."
	@ruff format .
	@ruff check . --fix
	@echo "Linting is complete"