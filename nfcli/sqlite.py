"""Communicates with an sqlite database."""

import logging
import sqlite3
from collections import Counter
from pathlib import Path
from sqlite3 import Connection, Cursor, Error
from typing import Any

from discord.message import Attachment

from nfcli.stats import Guilds, User

SQL_PATH = Path(Path.home(), ".nfcli.sqlite")


def fetch_row(cursor: Cursor, default: list[Any]) -> list[Any]:
    if not cursor:
        return default
    row = cursor.fetchone()
    if not row:
        return default
    return row


def create_connection() -> Connection:
    connection = None
    try:
        connection = sqlite3.connect(SQL_PATH.absolute())
        logging.debug("Connection to SQLite DB successful")
        init_database(connection)
    except Error as e:
        logging.error(f"The error '{e}' occurred when connecting to SQLite DB")
        raise e
    return connection


def execute_query(connection: Connection, query: str) -> Cursor:
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        logging.debug(f"Query '{query}' executed successfully")
        return cursor
    except Error as e:
        logging.error(f"The error '{e}' occurred when executing '{query}' query")
        raise e


def init_database(connection: Connection):
    create_table_lobbies = """
    DROP TABLE IF EXISTS lobbies;
    """
    execute_query(connection, create_table_lobbies)
    create_table_usage = """
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        guild BIGINT NOT NULL,
        user BIGINT NOT NULL,
        fleets TINYINT NOT NULL,
        ships TINYINT NOT NULL,
        missiles TINYINT NOT NULL
    );
    """
    execute_query(connection, create_table_usage)


def insert_usage_data(connection: Connection, guild: int, user: int, files: set[Attachment]):
    extensions = [file.filename.split(".")[-1] for file in files]
    counter = Counter(extensions)
    insert_lobby_data = "INSERT INTO usage (guild, user, fleets, ships, missiles) VALUES (?, ?, ?, ?, ?)"
    cursor = connection.cursor()
    cursor.execute(insert_lobby_data, (guild, user, counter["fleet"], counter["ship"], counter["missile"]))
    connection.commit()


def fetch_usage_servers(connection: Connection, days: int = 30) -> Guilds:
    user = fetch_usage_users(connection, days)
    fetch_usage_servers = (
        "SELECT COUNT(DISTINCT guild), SUM(fleets), SUM(ships), SUM(missiles) FROM usage"
        f" WHERE timestamp > DATETIME('now', '-{days} day')"
    )
    cursor = execute_query(connection, fetch_usage_servers)
    row = fetch_row(cursor, [0, 0, 0, 0])
    return Guilds(*row, days, user)


def fetch_usage_users(connection: Connection, days: int = 30) -> User:
    fetch_usage_users = (
        "SELECT guild, user, SUM(fleets) AS sf, SUM(ships) AS ss, SUM(missiles) AS sm FROM usage"
        f" WHERE timestamp > DATETIME('now', '-{days} day') GROUP BY user ORDER BY sf+ss+sm DESC LIMIT 10"
    )
    cursor = execute_query(connection, fetch_usage_users)
    row = fetch_row(cursor, [0, 0, 0, 0, 0])
    return User(*row, days)
