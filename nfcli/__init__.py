__version__ = "0.1.0"


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
