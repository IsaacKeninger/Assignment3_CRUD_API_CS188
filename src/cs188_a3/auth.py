"""
    AI USAGE: This file was adapted from the class API activity. Claude  was used
    only to point out bugs: package-style imports, storing the numeric user id in g.user_id
    instead of the username, and status codes for /register (201 on success, 400 for a short
    password). It did not write the code in this file.
"""

from functools import wraps

from flask import g
from flask_restful import Resource, reqparse, request
from flask_bcrypt import Bcrypt
from cs188_a3.db import get_db

# Endpoint Authorization Decorator
def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if auth is None:
            return {"message": "Authentication required"}, 401

        db = get_db()
        hashed_pwd = db.get_password(auth.username)
        valid = hashed_pwd is not None and Bcrypt().check_password_hash(hashed_pwd, auth.password)
        if not valid:
            return {"message": "Invalid credentials"}, 401
        
        g.user_id = g.db.fetch_user_id(auth.username)
        return func(*args, **kwargs)
    return wrapper

# Register User Endpoint
class Register(Resource):
    """
    This endpoint will register a user with username and password for authentication purposes.
    """
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "username", type=str, required=True, location='json',
            help="Username cannot be blank",
        )
        parser.add_argument(
            "password", type=str, required=True, location='json',
            help="Password cannot be blank",
        )
        args = parser.parse_args()
        username = args['username']
        password = args['password']

        # Type Checking and Validation for Username and Password
        if not username or not password:
            return {"message": "Username or Password is undefined."}, 400
        elif len(password) < 8:
            return {"message": "Password must have a length of 8 or morecharacters."}, 400

        hashed_pwd = Bcrypt().generate_password_hash(password).decode('utf-8')

        db = get_db()
        if db.add_user(username, hashed_pwd):
            user_id = g.db.fetch_user_id(username)
            return {"message": f"User {username} registered successfully. User ID: {user_id}"}, 201
        else:
            user_id = g.db.fetch_user_id(username)
            return {"message": f"User {username} already exists. User ID: {user_id}"}, 409
