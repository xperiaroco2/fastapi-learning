dev:
	uv run fastapi dev

lint-fix:
	uv run ruff check --fix . && uv run ruff format .

types-check:
	uv run pyright .

run-migrations:
	uv run alembic upgrade head

create-migration:
	uv run alembic revision --autogenerate -m "auto"

test:
	uv run pytest -v

worker:
	uv run arq app.worker.settings.WorkerSettings