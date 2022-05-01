import sqlite3
from typing import List

conn = sqlite3.connect('telega.db')
cursor = conn.cursor()
TABLE_NAME = 'chats'


def initialize_db() -> None:
    """Creates db and adds tables"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def fetch_chat_ids() -> List[str]:
    """Returns list of all chats"""
    cursor.execute(f"SELECT chat_id FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    ids = [t[0] for t in rows]
    return ids


def insert_chat_id(chat_id: int) -> None:
    """Inserts chat id into db"""
    cursor.execute(
        f"INSERT INTO {TABLE_NAME} "
        f"(chat_id) "
        f"VALUES ({chat_id})")
    conn.commit()


def delete_chat_id(chat_id: int) -> None:
    cursor.execute(f"delete from {TABLE_NAME} where chat_id={chat_id}")
    conn.commit()


def check_if_db_exists() -> None:
    """Creates db if it doesn't exist"""
    cursor.execute("SELECT name FROM sqlite_master "
                   f"WHERE type='table' AND name='{TABLE_NAME}'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    initialize_db()

