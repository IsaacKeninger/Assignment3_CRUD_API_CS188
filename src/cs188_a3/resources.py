from flask_restful import Resource, reqparse
from auth import auth_required
from db import get_db
from cs188_a3.services import get_fixture, FixtureNotFound, ExternalAPIError

class GameReviews(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("fixture_id", type=int, required=True, location='json',
                            help="fixture_id is required and must be an integer.")
        parser.add_argument("rating", type=int, required=True, location='json',
                            help="rating is required and must be an integer.")
        parser.add_argument("review", type=str, required=False, location='json')
        args = parser.parse_args()

        if not 1 <= args["rating"] <= 10:
            return {"message": "rating must be between 1 and 10."}, 400
        if args["review"] is not None and not args["review"].strip():
            return {"message": "review cannot be blank."}, 400

        try:
            fixture = get_fixture(args["fixture_id"])
        except FixtureNotFound:
            return {"message": f"Fixture {args['fixture_id']} not found."}, 404
        except ExternalAPIError:
            return {"message": "Football API is unavailable, try again later."}, 502

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

        if cursor.rowcount == 0: # Meaning, if no rows have changed.
            return {"message": f"Team {team_id} not found"}, 404
        
        return {"message": f"Team {team_id} Successfully Deleted."}, 201