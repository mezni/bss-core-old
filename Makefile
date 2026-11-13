.PHONY: install run init-db clean

install:
	uv sync

run:
	uv run flask --app src.main run --debug

init-db:
	uv run python -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database initialized.')"

clean:
	rm -rf __pycache__ src/__pycache__ instance/
