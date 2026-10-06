from flask_restful import Resource, reqparse
from auth import auth_required
from db import get_db

class Teams(Resource):

    @auth_required
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            "name", type=str, required=True, location='json',
            help="Team name cannot be blank.",
        )
        parser.add_argument(
            "league", type=str, required=True, location='json',
            help="Team must be in a league",
        )
        args = parser.parse_args()

        # Insert Team into DB
        db = get_db()
        cursor = db.conn.cursor()
        cursor.execute(
            "INSERT INTO teams (name, league) VALUES (?, ?);",
            (args['name'], args['league'])
        )
        new_id = cursor.lastrowid
        db.conn.commit()

        # Generate  Output
        response = {
            "id": new_id,
            "name": args['name'],
            "league": args['league']
        }

        return response, 201, {"Location": f"/teams/{new_id}"} 
    
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