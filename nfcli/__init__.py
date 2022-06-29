__version__ = "0.2.0"

STACK_COLUMNS = 3
COLUMN_WIDTH = 40


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
