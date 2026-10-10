"""
    AI USAGE: The _get helper function was developed by Claude. I used claude as a way to teach me
    and demonstrate how to make this effective requests helper function of which I could use.This
    helped make my learning process more enjoyable and showed me how to write good code for reaching
    external API's. Claude also suggested the get_fixture and get_head_to_head functions and the
    choice of API-Football endpoints, which I typed in, debugged and documented myself.
"""


import os
import requests
from dotenv import load_dotenv

load_dotenv() # Load in Environment Variable

# API Configuration from API-Football API
BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.environ.get("API_KEY")

class FixtureNotFound(Exception):
    """
    The API answered to fixtures but the match was not found.
    """

class ExternalAPIError(Exception):
    """
    The API did not answer or other errors occured.
    """

# CLAUDE CREATED THIS FUNCTION
def _get(path, params):
    """
    This helper function will send a get request to the football-api with the pre-loaded key
    in the header. This will take in a path to the specific endpoint it wants and the
    parameters needed for the query. It will return the JSON the the response.
    """
    try:
        resp = requests.get(
            f"{BASE_URL}{path}",
            headers={"x-apisports-key": API_KEY},
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ExternalAPIError(str(e))

    data = resp.json()
    if data.get("errors"):
        raise ExternalAPIError(str(data["errors"]))
    return data.get("response", [])

def get_fixture(fixture_id):
    """
    This function will look up matches by ID.
    It recieves the fixture ID and will return Python dict of the details of the match.
    """
    results = _get("/fixtures", {"id": fixture_id})
    if not results:
        raise FixtureNotFound(fixture_id)

    match = results[0]
    return {
        "home_id": match["teams"]["home"]["id"],
        "away_id": match["teams"]["away"]["id"],
        "home_team": match["teams"]["home"]["name"],
        "away_team": match["teams"]["away"]["name"],
        "home_goals": match["goals"]["home"],
        "away_goals": match["goals"]["away"],
        "league": match["league"]["name"],
        "match_date": match["fixture"]["date"],
    }

def get_head_to_head(home_id, away_id, last=5):
    """
    This function will look up head-to-head matches of teams.
    It will take in a home and an away id for teams as well as the specified number of games wanted.
    It will return details about those specific fixtures in python dictionary.
    """
    response = _get("/fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "last": last})
    return [
        {
            "date": m["fixture"]["date"],
            "home_team": m["teams"]["home"]["name"],
            "away_team": m["teams"]["away"]["name"],
            "score": f'{m["goals"]["home"]}-{m["goals"]["away"]}',
        }
        for m in response
    ]