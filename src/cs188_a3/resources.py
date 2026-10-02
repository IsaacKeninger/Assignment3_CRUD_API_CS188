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
            "leauge", type=str, required=True, location='json',
            help="Team must be in a leauge",
        )
        args = parser.parse_args()

        # Insert Team into DB
        db = get_db()
        cursor = db.conn.cursor()
        cursor.execute(
            "INSERT INTO teams (name, leauge) VALUES (?, ?);",
            (args['name'], args['leauge'])
        )
        new_id = cursor.lastrowid
        db.conn.commit()

        # Generate  Output
        response = {
            "id": new_id,
            "name": args['name'],
            "leauge": args['leauge']
        }

        return response, 201, {"Location": f"/teams/{new_id}"} 

    def get(self, leauge):
        db = get_db()

        cursor = db.conn.cursor()
        cursor.execute(
            "SELECT * FROM teams WHERE leauge = ?",
            (leauge,)
        )
        response = cursor.fetchall()
        return response, 201