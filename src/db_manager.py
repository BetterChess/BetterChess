import sqlite3
import os
from sql_querys import (
    DROP_MOVE_TABLE,
    DROP_GAME_TABLE,
    CREATE_MOVE_TABLE,
    CREATE_GAME_TABLE,
    SELECT_GAME_DATA,
    SELECT_MOVE_DATA
)


class FileHandler:
    """Storage location for the data/lib/log filepaths."""

    def __init__(self):
        self.dir = os.path.dirname(__file__)
        self.db_location = "./data/betterchess.db"
        self.log_path = r"../logs/logs.log"


def reset_db():
    conn = sqlite3.connect(FileHandler().db_location)
    curs = conn.cursor()
    curs.execute(DROP_MOVE_TABLE)
    curs.execute(DROP_GAME_TABLE)
    curs.execute(CREATE_MOVE_TABLE)
    curs.execute(CREATE_GAME_TABLE)
    conn.commit()
    conn.close()


def view_table_column_info():
    conn = sqlite3.connect(FileHandler().db_location)
    curs = conn.cursor()
    curs.execute("""PRAGMA table_info(move_data)""")
    print(curs.fetchall())
    curs.execute("""PRAGMA table_info(game_data)""")
    print(curs.fetchall())
    conn.close()


def view_table_size():
    conn = sqlite3.connect(FileHandler().db_location)
    curs = conn.cursor()
    curs.execute(SELECT_MOVE_DATA)
    move_rows = curs.fetchall()
    print(f"move_data rows: {len(move_rows)}")
    curs.execute(SELECT_GAME_DATA)
    game_rows = curs.fetchall()
    print(f"game_rows rows: {len(game_rows)}")
    conn.close()


def view_db_tables():
    conn = sqlite3.connect(FileHandler().db_location)
    curs = conn.cursor()
    curs.execute(SELECT_MOVE_DATA)
    rows = curs.fetchall()
    for row in rows:
        print(row)
    print("-------------------------------------------------")
    curs.execute(SELECT_GAME_DATA)
    rows = curs.fetchall()
    for row in rows:
        print(row)
    conn.close()


if __name__ == "__main__":
    print("=================================================")
    x = str.upper(input("R = RESET, S = SELECT ALL TABLES, I = TABLE COLUMN INFO, S = TABLE SIZE: "))
    if x == ("R"):
        print("Resetting Database")
        reset_db()
        print("Database Reset Successfully")
        print("=================================================")
    elif x == ("S"):
        view_db_tables()
        print("=================================================")
    elif x == ("I"):
        view_table_column_info()
        print("=================================================")
    elif x == ("S"):
        view_table_size()
        print("=================================================")
    else:
        pass
