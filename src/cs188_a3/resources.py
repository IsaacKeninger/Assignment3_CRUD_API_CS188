<<<<<<< Updated upstream
import sqlite3
from flask_restful import Resource, reqparse
from auth import auth_required
=======
"""
    AI USAGE: I used Claude to help restructure this file into thin request handlers that parse
    the request, call the service layer, and turn service exceptions into HTTP responses. Claude
    suggested the layout of post, get, patch and delete and the parse_review function, which I
    adapted. Claude wrote parse_review_changes, parse_filters and the list mode of get. Claude also
    added the Forbidden (403) handling to patch and fixed its 404 message. Claude wrote the
    Watchlist resource.
"""

from flask import g
from flask_restful import Resource, reqparse, abort
from cs188_a3.auth import auth_required
>>>>>>> Stashed changes
from cs188_a3.db import get_db

class GameReviews(Resource):

    @auth_required
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            "fixture_id", type=int, required=True, location='json',
            help="Fixture ID cannot be blank.",
        )
        parser.add_argument(
            "rating", type=str, required=True, location='json',
            help="rating cannot be blank.",
        )
        parser.add_argument("review", type=str, required=False, location='json')
        args = parser.parse_args()


        fixture, error = fetch_fixture(args['fixture_id'])
        if error:
            return error
    
        # Insert review into DB
        db = get_db()
        cursor = db.conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO reviews (user_id, fixture_id, home_team, away_team,
                   home_goals, away_goals, league, match_date, rating, review)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (g.user_id, args["fixture_id"], fixture["home_team"], fixture["away_team"],
                 fixture["home_goals"], fixture["away_goals"], fixture["league"],
                 fixture["match_date"], args["rating"], args["review"]),
            )
            db.conn.commit()
        except sqlite3.IntegrityError:
            return {"message": "You have already reviewed this fixture."}, 409
        new_id = cursor.lastrowid

        response = {
            "id": new_id,
            "user_id": g.user_id,
            "fixture_id": args["fixture_id"],
            "home_team": fixture["home_team"],
            "away_team": fixture["away_team"],
            "home_goals": fixture["home_goals"],
            "away_goals": fixture["away_goals"],
            "league": fixture["league"],
            "match_date": fixture["match_date"],
            "rating": args["rating"],
            "review": args["review"],
        }
        return response, 201, {"Location": f"/reviews/{new_id}"}
    
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "league", type=str, required=False, location='args'
        )
        parser.add_argument(
            "id", type=str, required=False, location='args'
        )

        args = parser.parse_args()
        league = args["league"]
        team_id = args["id"]

        db = get_db()

        cursor = db.conn.cursor()

        if team_id:
            cursor.execute(
                "SELECT * FROM teams WHERE id = ?",
                (team_id,)
            )
        elif league:
            cursor.execute(
                "SELECT * FROM teams WHERE league = ?",
                (league,)
            )
        else:
            cursor.execute(
                "SELECT * FROM teams",
            )

        response = cursor.fetchall()
        return response, 201

    # Tried out AI on implement. Claude Code.
    @auth_required
    def patch(self):
        parser = reqparse.RequestParser()

        parser.add_argument(
            "id", type=str, required=True, location='args'
        )
        parser.add_argument(
            "league", type=str, required=False, location='json'
        )

        args = parser.parse_args()
        team_id = args["id"]
        league = args["league"]

        db = get_db()
        cursor = db.conn.cursor()

        if league:
            cursor.execute(
                "UPDATE teams SET league = ? WHERE id = ?",
                (league, team_id)
            )
            db.conn.commit()

        cursor.execute(
            "SELECT * FROM teams WHERE id = ?",
            (team_id,)
        )
        team = cursor.fetchone()
        if team is None:
            return {"message": f"Team {team_id} not found"}, 404

        return team, 200

    @auth_required
    def delete(self):
        parser = reqparse.RequestParser()

        parser.add_argument(
            "id", type=str, required=True, location='args'
        )
        
        args = parser.parse_args()
        team_id = args["id"]

        db = get_db()
        cursor = db.conn.cursor()

        cursor.execute("DELETE FROM teams WHERE id = ?",
                        (team_id,))
        db.conn.commit()

<<<<<<< Updated upstream
        if cursor.rowcount == 0: # Meaning, if no rows have changed.
            return {"message": f"Team {team_id} not found"}, 404
        
        return {"message": f"Team {team_id} Successfully Deleted."}, 201
=======
    @auth_required
    def delete(self, review_id):
        "Delete a users review."
        try:
            services.delete_review(get_db(), g.user_id, review_id)
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404
        except services.Forbidden:
            return {"message": "You can only delete your own reviews."}, 403
        return {"message": f"Review {review_id} deleted."}, 200

class Watchlist(Resource):

    @auth_required
    def post(self):
        "Save a fixture to the user's watchlist."

        data = services.parse_watch()

        try:
            watch = services.add_to_watchlist(get_db(), g.user_id, data["fixture_id"])
        except services.FixtureNotFound:
            return {"message": f"Fixture {data['fixture_id']} not found."}, 404
        except services.DuplicateWatch:
            return {"message": f"Fixture {data['fixture_id']} is already on your watchlist."}, 409
        except services.ExternalAPIError:
            return {"message": "Football API is currently unavailable"}, 502
        return watch, 201, {"Location": "/watchlist"}

    @auth_required
    def get(self):
        "List the user's watchlist."
        return services.list_watchlist(get_db(), g.user_id), 200

    @auth_required
    def delete(self, fixture_id: int):
        "Remove a fixture from the user's watchlist."
        try:
            services.remove_from_watchlist(get_db(), g.user_id, fixture_id)
        except services.WatchNotFound:
            return {"message": f"Fixture {fixture_id} is not on your watchlist."}, 404
        return {"message": f"Fixture {fixture_id} removed from your watchlist."}, 200
>>>>>>> Stashed changes
