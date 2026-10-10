"""
    AI USAGE: This file's tests for Parsers, services, and the review resource wer written by Claude. 
        I studied and closely read the code to understand the nature of the syntax, logic, and flows
        for my personal learning and development of these tests

    What I Did: I created the code for the watchlist tests using my knowledge of the other tests and 
        pytest in general. I deeply read, understood, and created code for these tests to have succinct
        and proper logic for the API.
"""

import pytest
import requests
from flask import Flask
from werkzeug.exceptions import HTTPException
from cs188_a3 import services
from cs188_a3.db import Database


# SHARED TEST DATA AND FIXTURES
FAKE_FIXTURES = {
    1001: {
        "home_id": 42, "away_id": 49,
        "home_team": "Arsenal", "away_team": "Chelsea",
        "home_goals": 2, "away_goals": 1,
        "league": "Premier League", "match_date": "2025-01-01T15:00:00+00:00",
    },
    1002: {
        "home_id": 541, "away_id": 529,
        "home_team": "Real Madrid", "away_team": "Barcelona",
        "home_goals": 0, "away_goals": 0,
        "league": "La Liga", "match_date": "2025-02-01T20:00:00+00:00",
    },
}
MISSING_FIXTURE_ID = 999
API_DOWN_FIXTURE_ID = 503

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    "Run every test in its own temp folder so activity.db starts empty and the real one is untouched."
    monkeypatch.chdir(tmp_path)

@pytest.fixture
def fake_api(monkeypatch):
    "Replace get_fixture so tests use canned matches instead of calling API-Football."
    def fake_get_fixture(fixture_id):
        if fixture_id == API_DOWN_FIXTURE_ID:
            raise services.ExternalAPIError("API unavailable")
        if fixture_id not in FAKE_FIXTURES:
            raise services.FixtureNotFound(fixture_id)
        return dict(FAKE_FIXTURES[fixture_id])

    monkeypatch.setattr(services, "get_fixture", fake_get_fixture)

# PARSERS

parser_app = Flask(__name__)

def run_parser(parser, json=None, query=""):
    "Run a parser inside a fake request. Returns the parsed dict, or the HTTP status if it aborts."
    with parser_app.test_request_context(f"/reviews{query}", method="POST", json=json):
        try:
            return parser()
        except HTTPException as e:
            return e.code

def test_parse_review_valid():
    data = run_parser(services.parse_review, {"fixture_id": 1001, "rating": 8, "review": "Great"})
    assert (data["fixture_id"], data["rating"], data["review"]) == (1001, 8, "Great")

def test_parse_review_text_optional():
    data = run_parser(services.parse_review, {"fixture_id": 1001, "rating": 8})
    assert data["review"] is None

@pytest.mark.parametrize("body", [
    {"rating": 8},                                  # missing fixture_id
    {"fixture_id": 1001},                           # missing rating
    {"fixture_id": "abc", "rating": 8},             # fixture_id not an int
    {"fixture_id": 1001, "rating": "great"},        # rating not an int
    {"fixture_id": 1001, "rating": 0},              # rating too low
    {"fixture_id": 1001, "rating": 11},             # rating too high
    {"fixture_id": 1001, "rating": 8, "review": "   "},  # blank review
])
def test_parse_review_rejects_bad_body(body):
    assert run_parser(services.parse_review, body) == 400

def test_parse_review_changes_rating_only():
    changes = run_parser(services.parse_review_changes, {"rating": 4})
    assert (changes["rating"], changes["review"]) == (4, None)

def test_parse_review_changes_review_only():
    changes = run_parser(services.parse_review_changes, {"review": "Better on rewatch"})
    assert (changes["rating"], changes["review"]) == (None, "Better on rewatch")

@pytest.mark.parametrize("body", [
    {},                     # nothing to change
    {"rating": 0},
    {"rating": 11},
    {"rating": "high"},
    {"review": "   "},
])
def test_parse_review_changes_rejects_bad_body(body):
    assert run_parser(services.parse_review_changes, body) == 400

def test_parse_filters_reads_league():
    with parser_app.test_request_context("/reviews?league=La%20Liga"):
        assert services.parse_filters()["league"] == "La Liga"

def test_parse_filters_league_optional():
    with parser_app.test_request_context("/reviews"):
        assert services.parse_filters()["league"] is None

# ======================================================================
# GAME REVIEWS RESOURCE
# ======================================================================

@pytest.fixture
def alice_review(db, fake_api):
    return services.create_review(db, "alice", 1001, 8, "Great game")

def test_create_review_stores_match_details(alice_review):
    assert alice_review["user_id"] == "alice"
    assert alice_review["fixture_id"] == 1001
    assert alice_review["home_team"] == "Arsenal"
    assert alice_review["league"] == "Premier League"
    assert alice_review["rating"] == 8
    assert alice_review["review"] == "Great game"
    assert isinstance(alice_review["id"], int)

def test_create_review_without_text(db, fake_api):
    review = services.create_review(db, "alice", 1001, 8, None)
    assert review["review"] is None

def test_create_review_duplicate(db, fake_api, alice_review):
    with pytest.raises(services.DuplicateReview):
        services.create_review(db, "alice", 1001, 2, "Again")

def test_create_review_unknown_fixture_stores_nothing(db, fake_api):
    with pytest.raises(services.FixtureNotFound):
        services.create_review(db, "alice", MISSING_FIXTURE_ID, 8, None)
    assert db.list_reviews(None) == []

def test_create_review_api_down_stores_nothing(db, fake_api):
    with pytest.raises(services.ExternalAPIError):
        services.create_review(db, "alice", API_DOWN_FIXTURE_ID, 8, None)
    assert db.list_reviews(None) == []

def test_get_review(db, alice_review):
    assert services.get_review(db, alice_review["id"]) == alice_review

def test_get_review_missing(db):
    with pytest.raises(services.ReviewNotFound):
        services.get_review(db, 123)

def test_list_reviews_filter(db, fake_api):
    services.create_review(db, "alice", 1001, 8, None)
    services.create_review(db, "alice", 1002, 5, None)
    assert len(services.list_reviews(db, None)) == 2
    assert [r["fixture_id"] for r in services.list_reviews(db, "La Liga")] == [1002]

def test_patch_review_by_owner(db, alice_review):
    updated = services.patch_review(db, "alice", alice_review["id"], 3, None)
    assert updated["rating"] == 3
    assert updated["review"] == "Great game"

def test_patch_review_by_other_user_forbidden(db, alice_review):
    with pytest.raises(services.Forbidden):
        services.patch_review(db, "bob", alice_review["id"], 1, "Hacked")
    assert services.get_review(db, alice_review["id"])["rating"] == 8

def test_patch_missing_review(db):
    with pytest.raises(services.ReviewNotFound):
        services.patch_review(db, "alice", 123, 5, None)

def test_delete_review_by_owner(db, alice_review):
    services.delete_review(db, "alice", alice_review["id"])
    with pytest.raises(services.ReviewNotFound):
        services.get_review(db, alice_review["id"])

def test_delete_review_by_other_user_forbidden(db, alice_review):
    with pytest.raises(services.Forbidden):
        services.delete_review(db, "bob", alice_review["id"])
    assert services.get_review(db, alice_review["id"]) is not None

def test_delete_missing_review(db):
    with pytest.raises(services.ReviewNotFound):
        services.delete_review(db, "alice", 123)

# ======================================================================
# WATCHLIST
# ======================================================================
# (no watchlist tests yet)


# ======================================================================
# OTHER
# ======================================================================
@pytest.fixture
def db():
    "A Database object backed by the temp folder's activity.db."
    database = Database()
    yield database
    database.conn.close()
