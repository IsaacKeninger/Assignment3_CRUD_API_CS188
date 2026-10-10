from flask import Flask, g
from cs188_a3.auth import Register
from cs188_a3.resources import GameReviews
from flask_restful import Api
from flask_talisman import Talisman
from cs188_a3._constants import PROJECT_ROOT
import os 

_CERTIFICATE_PATH = os.path.join(PROJECT_ROOT, 'MyCertificate.crt')
_KEYFILE_PATH = os.path.join(PROJECT_ROOT, 'MyKey.pem')

def init_api(app):
    api = Api(app)
    api.add_resource(Register, '/register')
    api.add_resource(GameReviews, '/reviews', '/reviews/<int:review_id>')

def create_app(with_ssl=True) -> Flask:
    app = Flask(__name__)
    app.config["PREFERRED_URL_SCHEME"] = "https"
    Talisman(app, force_https=with_ssl)
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
    run_app()