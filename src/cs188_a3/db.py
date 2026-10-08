"""
    AI USAGE: I used Claude to help me with creating the SQL queries for creating the reviews table
    as well as for helping in general understanding of the file. I either created the rest of the
    file myself or it was copied over from past class activites and adjusted accordingly.
"""

import sqlite3
from flask import g

def connect():
    return sqlite3.connect('activity.db')

class Database:
    def __init__(self):
        """
        This function initizlies the database connection and creates the tables.
        """
        self.conn = connect()
        self.create_users_table()
        self.create_reviews_table()

    def create_users_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                    )""")

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

    def fetch_user_id(self, username):
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

    def create_reviews_table(self):
        # Claude was used here!
        with self.conn:
            self.conn.execute("""
                CREATE TABLE reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                fixture_id INTEGER NOT NULL,
                home_team TEXT, away_team TEXT,
                home_goals INTEGER, away_goals INTEGER,
                league TEXT, match_date TEXT,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 10),
                review TEXT,
                UNIQUE (user_id, fixture_id)
                );""")

def get_db() -> Database:
    if "db" not in g:
        g.db = Database()
    return g.db