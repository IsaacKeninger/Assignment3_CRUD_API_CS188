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
        db = get_db()

        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT * FROM teams",
        )
        response = cursor.fetchall()
        return response, 201
    
    def get(self, league):
        db = get_db()

        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT * FROM teams WHERE league = ?",
            (league,)
        )

        response = cursor.fetchall()
        return response, 201
"""
TO DO

    def patch(self, id):

    def delete(self, id):
"""