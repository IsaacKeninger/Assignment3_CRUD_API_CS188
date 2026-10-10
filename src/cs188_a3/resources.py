"""
    AI USAGE: I used Claude to help restructure this file into thin request handlers that parse
    the request, call the service layer, and turn service exceptions into HTTP responses. Claude
    suggested the layout of post, get, patch and delete and the parse_review function, which I
    adapted. Claude wrote parse_review_changes, parse_filters and the list mode of get.
"""

from flask import g
from flask_restful import Resource, reqparse, abort
from cs188_a3.auth import auth_required
from cs188_a3.db import get_db
from cs188_a3 import services

def parse_review() -> dict:
    "Read and Validate the body of POST /reviews"
    parser = reqparse.RequestParser()
    parser.add_argument("fixture_id", type=int, required=True, location='json',
                        help="fixture_id is required and must be an integer.")
    parser.add_argument("rating", type=int, required=True, location='json',
                        help="rating is required and must be an integer.")
    parser.add_argument("review", type=str, required=False, location='json')
    return parser.parse_args()

def parse_review_changes() -> dict:
    "Read and validate the body of PATCH /reviews/<id>. Both fields are optional."
    parser = reqparse.RequestParser()
    parser.add_argument("rating", type=int, required=False, location='json',
                        help="rating must be an integer.")
    parser.add_argument("review", type=str, required=False, location='json')
    changes = parser.parse_args()

    if changes["rating"] is None and changes["review"] is None:
        abort(400, message="Provide a rating and/or review to update.")
    if changes["rating"] is not None and not 1 <= changes["rating"] <= 10:
        abort(400, message="rating must be between 1 and 10.")
    if changes["review"] is not None and not changes["review"].strip():
        abort(400, message="review cannot be blank.")
    return changes

# CLAUDE
def parse_filters() -> dict:
    "Read the optional query parameters of GET /reviews."
    parser = reqparse.RequestParser()
    parser.add_argument("league", type=str, required=False, location='args')
    return parser.parse_args()

class GameReviews(Resource):

    @auth_required
    def post(self):
        "Add a users review."

        data = parse_review()

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
            filters = parse_filters()
            return services.list_reviews(get_db(), filters["league"]), 200

        try:
            return services.get_review(get_db(), review_id), 200
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404

    @auth_required
    def patch(self, review_id: int):
        "Update a users review."

        changes = parse_review_changes()

        try:
            review = services.patch_review(get_db(), g.user_id, review_id, changes["rating"], changes["review"])
        except services.ReviewNotFound:
            return {"message": f"Fixture {review_id} not found."}, 404       

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