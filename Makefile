.PHONY: install run debug clean fclean re lint lint-strict

PYTHON_MAMBA = /goinfre/$(USER)/micromamba/envs/flyin_env/bin/python

setup_env:
	@echo "Installation de l'environnement pré-compilé (Micromamba)...";\
	if [ ! -f "/goinfre/$$USER/bin/micromamba" ]; then\
		mkdir -p /goinfre/$$USER/bin;\
		curl -kLs https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj -C /goinfre/$$USER/ bin/micromamba;\
	fi;\
	/goinfre/$$USER/bin/micromamba create -y -p /goinfre/$$USER/micromamba/envs/flyin_env -c conda-forge python=3.13 tk;

install:
	uv sync

run:
	uv run --python $(PYTHON_MAMBA) main.py $(MAP)

debug:
	uv run --python $(PYTHON_MAMBA) -m pdb main.py $(MAP)

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