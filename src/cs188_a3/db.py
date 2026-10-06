import sqlite3
from flask import g

def connect():
    return sqlite3.connect('activity.db')

class Database:
    def __init__(self):
        self.conn = connect()
        self.create_users_table()
        self.create_teams_table()

    def create_users_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                    )""")

    def create_teams_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                league TEXT NOT NULL)""")            

    def add_user(self, username, hashed_pwd):
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pwd)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_id(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?",
                       (username,)
                       )
        row = cursor.fetchone()
        return row[0] if row is not None else None

    def get_password(self, username) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?",
                       (username,)
                       )
        row = cursor.fetchone()
        return row[0] if row is not None else None

def get_db() -> Database:
    if "db" not in g:
        g.db = Database()
    return g.db