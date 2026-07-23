.PHONY: install run debug clean fclean re lint lint-strict

install:
	uv sync

run:
	uv run main.py $(MAP)

debug:
	uv run python -m pdb main.py

clean:
	rm -rf __pycache__ .mypy_cache .python-version

fclean: clean
	rm -rf .venv

re: fclean install

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict