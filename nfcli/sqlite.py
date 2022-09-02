import logging
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, Error
from time import time
from typing import Counter, List

from discord.message import Attachment

from nfcli.models import Lobbies

SQL_PATH = Path(Path.home(), ".nfcli.sqlite")


def create_connection() -> Connection:
    connection = None
    try:
        connection = sqlite3.connect(SQL_PATH.absolute())
        logging.debug("Connection to SQLite DB successful")
        init_database(connection)
    except Error as e:
        logging.error(f"The error '{e}' occurred when connecting to SQLite DB")
    return connection


def execute_query(connection: Connection, query: str) -> Cursor:
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        logging.debug(f"Query '{query}' executed successfully")
        return cursor
    except Error as e:
        logging.error(f"The error '{e}' occurred when executing '{query}' query")


def init_database(connection: Connection):
    create_table_lobbies = """
    CREATE TABLE IF NOT EXISTS lobbies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        author TEXT NOT NULL,
        lobby_data TEXT NOT NULL
    );
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


def insert_lobby_data(connection: Connection, author: str, lobby_data: str):
    insert_lobby_data = "INSERT INTO lobbies (author, lobby_data) VALUES (?, ?)"
    cursor = connection.cursor()
    cursor.execute(insert_lobby_data, (author, lobby_data))
    connection.commit()


def fetch_lobby_data(connection: Connection) -> Lobbies:
    fetch_lobby_data = "SELECT timestamp, author, lobby_data FROM lobbies ORDER BY id DESC"
    cursor = execute_query(connection, fetch_lobby_data)
    if cursor is None:
        return Lobbies(time(), "")
    row = cursor.fetchone()
    if not row:
        return Lobbies(time(), "")
    return Lobbies(*row)


def insert_usage_data(connection: Connection, guild: int, user: int, files: List[Attachment]):
    extensions = [file.filename.split(".")[-1] for file in files]
    counter = Counter(extensions)
    insert_lobby_data = "INSERT INTO usage (guild, user, fleets, ships, missiles) VALUES (?, ?, ?, ?, ?)"
    cursor = connection.cursor()
    cursor.execute(insert_lobby_data, (guild, user, counter["fleet"], counter["ship"], counter["missile"]))
    connection.commit()
