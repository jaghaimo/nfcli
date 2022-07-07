import os

from dotenv import load_dotenv
from rich.theme import Theme

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USERNAME = os.getenv("STEAM_USERNAME")

STACK_COLUMNS = 3
COLUMN_WIDTH = 50

nfc_theme = Theme({"orange": "#e14b00", "grey": "#474946"})


def load_path(path: str) -> str:
    with open(path, "r") as f:
        return f.read()
