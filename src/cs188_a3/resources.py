from flask_restful import Resource, g
from auth import auth_required

class UserResource(Resource):
    @auth_required

    def post(self):
"""
    def get(self, id):

    def patch(self, id):

    def delete(self, id):
"""