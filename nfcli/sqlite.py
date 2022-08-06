import logging
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, Error

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
    create_table = """
    CREATE TABLE IF NOT EXISTS lobbies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lobby_data TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(connection, create_table)


def insert_lobby_data(connection: Connection, lobby_data: str):
    insert_lobby_data = f"INSERT INTO lobbies (lobby_data) VALUES {lobby_data}"
    execute_query(connection, insert_lobby_data)


def fetch_lobby_data(connection: Connection) -> Lobbies:
    fetch_lobby_data = "SELECT lobby_data, timestamp FROM lobbies ORDER BY id DESC"
    cursor = execute_query(connection, fetch_lobby_data)
    if cursor is None:
        return Lobbies()
    return Lobbies(cursor.fetchone())
