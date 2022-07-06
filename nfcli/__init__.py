from rich.theme import Theme

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
