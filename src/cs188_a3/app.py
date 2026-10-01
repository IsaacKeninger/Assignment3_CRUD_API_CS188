from flask import Flask, jsonify, request, g
from flask_restful import Resource, Api, reqparse
from flask_talisman import Talisman
from api_activity._constants import PROJECT_ROOT
from api_activity.db import Database
from flask_bcrypt import Bcrypt
from functools import wraps
import os 

_KEYFILE_PATH = os.path.join(PROJECT_ROOT, "MyKey.pem")
_CERTIFICATE_PATH = os.path.join(PROJECT_ROOT, "MyCertificate.crt")

app = Flask(__name__)
api = Api(app)

# AUTH
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

        g.user_id = auth.username
        return func(*args, **kwargs)
    return wrapper

class Register(Resource):
    def put(self):
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

        if not username or not password:
            return {"message": "Username or Password is undefined."}, 400
        elif len(username) < 8:
            return {"message": "Password must have a length of 8 or morecharacters."}

        hashed_pwd = Bcrypt().generate_password_hash(password).decode('utf-8')

        db = get_db()
        if db.add_user(username, hashed_pwd):
            return {"message": f"User {username} registered successfully"}
        else:
            return {"message": f"User {username} already exists"}, 409

# example endpoint
class Profile(Resource):
    @auth_required
    def get(self):
        return {"message": f"Hello, {g.username}!"}

#API
def init_api(app):
    api = Api(app)
    api.add_resource(Hello, '/')
    api.add_resource(Square, "/square/<int(signed=True):num>")
    api.add_resource(Echo, "/echo")
    api.add_resource(Register, "/register")
    api.add_resource(Profile, "/profile")

def create_app(with_ssl=True) -> Flask:
    app = Flask(__name__)
    app.config["PREFERRED_URL_SCHEME"] = "https"
    ssl_context = (_CERTIFICATE_PATH, _KEYFILE_PATH) if with_ssl else None
    Talisman(app, force_https=True)
    init_api(app)
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.conn.close()
    return app

def run_app(debug: bool = True, with_ssl: bool = True) -> None:
    ssl_context = (_CERTIFICATE_PATH, _KEYFILE_PATH) if with_ssl else None
    create_app().run(debug=debug, ssl_context=ssl_context)

# Run
if __name__ == "__main__":
    app.run(debug=True)