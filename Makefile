.PHONY: install setup_env run debug clean fclean re lint lint-strict

PYTHON_MAMBA = /goinfre/$(USER)/micromamba/envs/flyin_env/bin/python
MAMBA_BIN = /goinfre/$(USER)/bin/micromamba

setup_env_42:
	@echo "Vérification et configuration de Micromamba..."; \
	if ! command -v micromamba >/dev/null 2>&1 && [ ! -f "$(MAMBA_BIN)" ]; then \
		echo "Téléchargement de Micromamba..."; \
		mkdir -p /goinfre/$(USER)/bin; \
		curl -kLs https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj -C /goinfre/$(USER)/ bin/micromamba; \
	fi; \
	BIN_TO_USE=$$(command -v micromamba 2>/dev/null || echo "$(MAMBA_BIN)"); \
	if [ ! -d "/goinfre/$(USER)/micromamba/envs/flyin_env" ]; then \
		echo "Création de l'environnement virtuel flyin_env..."; \
		$$BIN_TO_USE create -y -p /goinfre/$(USER)/micromamba/envs/flyin_env -c conda-forge python=3.13 tk; \
	fi

install:
	@which uv > /dev/null 2>&1 || pip install --user uv
	uv sync

run:
	uv run --python $(PYTHON_MAMBA) main.py $(MAP) $(FLAG)

debug:
	uv run --python $(PYTHON_MAMBA) -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache .python-version

fclean: clean
	rm -rf .venv
	rm -rf /goinfre/$(USER)/micromamba/envs/flyin_env
	rm -f /goinfre/$(USER)/bin/micromamba

re: fclean install

lint:
	uv run flake8 . --exclude=.venv
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 . --exclude=.venv
	uv run mypy . --strict

doc:
	uv run pydocstyle