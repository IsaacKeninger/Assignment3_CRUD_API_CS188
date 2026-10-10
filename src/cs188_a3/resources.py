"""
    AI USAGE: I used Claude to help restructure this file into thin request handlers that parse
    the request, call the service layer, and turn service exceptions into HTTP responses. Claude
    suggested the layout of post, get, patch and delete and the parse_review function, which I
    adapted. Claude wrote parse_review_changes, parse_filters and the list mode of get. Claude also
    added the Forbidden (403) handling to patch and fixed its 404 message.
"""

from flask import g
from flask_restful import Resource, reqparse, abort
from cs188_a3.auth import auth_required
from cs188_a3.db import get_db
from cs188_a3 import services

class GameReviews(Resource):

    @auth_required
    def post(self):
        "Add a users review."

        data = services.parse_review()

        try: 
            review = services.create_review(get_db(), g.user_id, data["fixture_id"], data["rating"], data["review"])
        except services.FixtureNotFound:
            return {"message": f"Fixture {data['fixture_id']} not found."}, 404
        except services.DuplicateReview:
            return {"message": "This review has already been reviewed."}, 409
        except services.ExternalAPIError:
            return {"message": "Football API is currently unavailable"}, 502
        return review, 201, {"Location": f"/reviews/{review['id']}"}

    def get(self, review_id: int | None = None):
        "Return one review, or list all reviews)."
        if review_id is None:
            filters = services.parse_filters()
            return services.list_reviews(get_db(), filters["league"]), 200

        try:
            return services.get_review(get_db(), review_id), 200
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404

    @auth_required
    def patch(self, review_id: int):
        "Update a users review."

        changes = services.parse_review_changes()

        try:
            review = services.patch_review(get_db(), g.user_id, review_id, changes["rating"], changes["review"])
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404
        except services.Forbidden:
            return {"message": "You can only edit your own reviews."}, 403

        return review, 200

    @auth_required
    def delete(self, review_id):
        "Delete a users review."
        try:
            services.delete_review(get_db(), g.user_id, review_id)
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404
        except services.Forbidden:
            return {"message": "You can only delete your own reviews."}, 403
        return {"message": f"Review {review_id} deleted."}, 200            