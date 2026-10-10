"""
    AI USAGE: I used Claude to in general help me restructure this file into thin handlers that parse
        the request, call the service layer, and turn service exceptions into HTTP responses. These adapations
        included loose suggestions for the layout of post, get, patch and delete and the parse_review function, which I
        adapted. Claude wrote parse_review_changes, parse_filters and the list mode of get for helper functions as well as
        small fixed that added the Forbidden (403) handling to patch and fixed its 404 message and watchlists resource layout.

    What I did: I was still the primary writer organizer of the code, writing the main logic loops and flows with full understanding.

    I learned: How to create efficent and modular resources. How to user HTTP Status Codes. How to write good helper functions.
        How to use Git Branches. How to do proper exception handling.  
"""

from flask import g
from flask_restful import Resource, reqparse, abort
from cs188_a3.auth import auth_required
from cs188_a3.db import get_db
from cs188_a3 import services

class GameReviews(Resource):

    @auth_required
    def post(self):
        "Add a users review using POST /reviews with the review as JSON data input."

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
        "Return one review or list all reviews in the database via GET /reviews or GET /reviews/<int:review_id>."

        # Allows to search reviews by league via query paramters wo/ review_id
        if review_id is None:
            filters = services.parse_filters()
            return services.list_reviews(get_db(), filters["league"]), 200

        try:
            return services.get_review(get_db(), review_id), 200
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404

    @auth_required
    def patch(self, review_id: int):
        "Update a users review via PATCH /reviews/<int:review_id>."

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
        "Delete a users review via DELETE /reviews/<int:review_id>."
        try:
            services.delete_review(get_db(), g.user_id, review_id)
        except services.ReviewNotFound:
            return {"message": f"Review {review_id} not found."}, 404
        except services.Forbidden:
            return {"message": "You can only delete your own reviews."}, 403
        return {"message": f"Review {review_id} deleted."}, 200

class Watchlist(Resource):

    @auth_required
    def post(self):
        "Save a fixture to the user's watchlist."

        data = services.parse_watch()

        try:
            watch = services.add_to_watchlist(get_db(), g.user_id, data["fixture_id"])
        except services.FixtureNotFound:
            return {"message": f"Fixture {data['fixture_id']} not found."}, 404
        except services.DuplicateWatch:
            return {"message": f"Fixture {data['fixture_id']} is already on your watchlist."}, 409
        except services.ExternalAPIError:
            return {"message": "Football API is currently unavailable"}, 502
        return watch, 201, {"Location": "/watchlist"}

    @auth_required
    def get(self):
        "List the user's watchlist."
        return services.list_watchlist(get_db(), g.user_id), 200

    @auth_required
    def delete(self, fixture_id: int):
        "Remove a fixture from the user's watchlist."
        try:
            services.remove_from_watchlist(get_db(), g.user_id, fixture_id)
        except services.WatchNotFound:
            return {"message": f"Fixture {fixture_id} is not on your watchlist."}, 404
        return {"message": f"Fixture {fixture_id} removed from your watchlist."}, 200