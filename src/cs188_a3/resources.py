from flask_restful import Resource
from auth import auth_required

# example endpoint
class Profile(Resource):
    @auth_required
    def get(self):
        return {"message": f"Hello, {g.username}!"}