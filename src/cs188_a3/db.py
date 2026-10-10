"""
    AI USAGE: I used Claude to help me with creating the SQL queries for creating the reviews table
        as well as for helping in general understanding of the file for development purposes. The
        insert_review, get_review and list_reviews methods, update_review, and delete_review,
        were suggested to be created (no code generated) which I eventually coded and  in and adjusted.
        Claude also pointed out bugs here (missing IF NOT EXISTS, user_id column type, hard-coded database path)
        along with the watchlist (3rd endpoint related) methods. Claude explained to me how to pass the
        database path into Database and read it in get_db from the app config to me as well. 
     
    What I did:  I created the rest of the file myself or it was copied over from past class activites and adjusted accordingly.
        I still have a good understanding of the code and wrote a the majority of it. 
"""

import sqlite3
from flask import g, current_app

DEFAULT_DB = "activity.db"

def connect(path: str):
    return sqlite3.connect(path)

class Database:
    def __init__(self, path: str = DEFAULT_DB):
        """
        This function initizlies the database connection and creates the tables.
        """
        self.conn = connect(path)
        self.create_users_table()
        self.create_reviews_table()
        self.create_watchlist_table()

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
                CREATE TABLE IF NOT EXISTS reviews (
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

    def insert_review(self, user_id: int, fixture_id: int, fixture: dict, rating: int, review: str | None) -> int:
        "Insert a review and returns its id. Raises error on a duplicate insertion."
        with self.conn:
            cursor = self.conn.execute(
                """INSERT INTO reviews (user_id, fixture_id, home_team, away_team, home_goals,
                away_goals, league, match_date, rating, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, fixture_id, fixture["home_team"], fixture["away_team"], fixture["home_goals"], 
                 fixture["away_goals"], fixture["league"], fixture["match_date"], rating, review), 
            )
        return cursor.lastrowid

    def get_review(self, review_id: int) -> dict:
        cursor = self.conn.execute(
        """SELECT id, user_id, fixture_id, home_team, away_team, home_goals,
        away_goals, league, match_date, rating, review FROM reviews WHERE id = ?""",
        (review_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "fixture_id": row[2],
            "home_team": row[3],
            "away_team": row[4],
            "home_goals": row[5],
            "away_goals": row[6],
            "league": row[7],
            "match_date": row[8],
            "rating": row[9],
            "review": row[10],
        }

    def update_review(self, review_id: int, rating: int | None, review: str | None) -> None:
        with self.conn:
            if rating is not None:
                self.conn.execute("UPDATE reviews SET rating = ? WHERE id = ?",
                                  (rating, review_id),
                                  )
            if review is not None:
                self.conn.execute(
                    "UPDATE reviews SET review = ? WHERE id = ?",
                    (review, review_id),
                )

    def delete_review(self, review_id: int) -> None:
        "Delete a review via id."
        with self.conn:
            self.conn.execute(
                "DELETE FROM reviews WHERE id = ?",
                (review_id,),
            )

    def list_reviews(self, league: str | None) -> list[dict]:
        if league:
            cursor = self.conn.execute(
                """SELECT id, user_id, fixture_id, home_team, away_team, home_goals,
                away_goals, league, match_date, rating, review FROM reviews WHERE league = ?""",
                (league,),
            )
        else:
            cursor = self.conn.execute(
                """SELECT id, user_id, fixture_id, home_team, away_team, home_goals,
                away_goals, league, match_date, rating, review FROM reviews"""
            )
        return [
            {"id": row[0], "user_id": row[1], "fixture_id": row[2], "home_team": row[3],
            "away_team": row[4], "home_goals": row[5], "away_goals": row[6], "league": row[7],
            "match_date": row[8], "rating": row[9], "review": row[10]}
            for row in cursor.fetchall()
        ]

    # WATCHLIST
    def create_watchlist_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                fixture_id INTEGER NOT NULL,
                home_team TEXT, away_team TEXT,
                league TEXT, match_date TEXT,
                UNIQUE (user_id, fixture_id)
                );""")

    def add_watch(self, user_id, fixture_id: int, fixture: dict) -> None:
        "Save a fixture to a user's watchlist. Raises IntegrityError if it is already saved."
        with self.conn:
            self.conn.execute(
                """INSERT INTO watchlist (user_id, fixture_id, home_team, away_team, league, match_date)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, fixture_id, fixture["home_team"], fixture["away_team"],
                 fixture["league"], fixture["match_date"]),
            )

    def list_watchlist(self, user_id) -> list[dict]:
        "Return every fixture a user has saved, soonest match first."
        cursor = self.conn.execute(
            """SELECT fixture_id, home_team, away_team, league, match_date FROM watchlist
            WHERE user_id = ? ORDER BY match_date""",
            (user_id,),
        )
        return [
            {"fixture_id": row[0], "home_team": row[1], "away_team": row[2],
             "league": row[3], "match_date": row[4]}
            for row in cursor.fetchall()
        ]

    def remove_watch(self, user_id, fixture_id: int) -> bool:
        "Remove a fixture from a user's watchlist. Returns False if it wasn't saved."
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM watchlist WHERE user_id = ? AND fixture_id = ?",
                (user_id, fixture_id),
            )
        return cursor.rowcount > 0

def get_db() -> Database:
    if "db" not in g:
        g.db = Database(current_app.config["DATABASE"])
    return g.db
