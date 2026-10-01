from flask import jsonify, url_for

from flask_restful import Resource, reqparse
from auth import auth_required
from db import get_db

class Teams(Resource):

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
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO teams (name, leauge) VALUES (?, ?);",
            (args['name'], args['leauge'])
        )
        new_id = cursor.lastrowid
        db.commit()

        # Generate  Output
        response = {
            "id": new_id,
            "name": args['name'],
            "leauge": args['leauge']
        }
        location = url_for('get_resource', resource_id=new_id)

        return jsonify(response), 201, {"Location": location} 