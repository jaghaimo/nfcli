deactivate || true
poetry install --dev
pip install pre-commit
pre-commit autoupdate
pre-commit install
