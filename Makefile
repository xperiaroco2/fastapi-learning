dev:
	poetry run fastapi dev

lint-fix:
	poetry run ruff check --fix . && poetry run ruff format .

types-check:
	poetry run pyright .

run-migrations:
	poetry run alembic upgrade head

create-migration:
	poetry run alembic revision --autogenerate -m "auto"
