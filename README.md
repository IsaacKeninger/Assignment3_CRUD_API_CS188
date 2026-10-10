# Purpose

This CRUD API is a match reviewer and watchlist for soccer games around the world.
External API: https://www.api-football.com/


## Setup / Getting Started

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Create a `.env` file in the project root with tje API-Football key:
   ```
   API_KEY= api_football_key, sent in blackboard submission
   ```
3. Start the server via:
   ```bash
   uv run app.py
   ```

## How to Test

### Automated tests

```bash
uv run pytest
```

### Endpoints

'*' = Needs Auth

| Method | URL | Auth | JSON Body |
|---|---|---|---|
| POST* | `/register` | – | `username`, `password` (8+ chars) | 
| GET | `/reviews` | – | – |
| GET | `/reviews?league=<name>` | – | – |
| GET | `/reviews/<review_id>` | – | – |
| POST* | `/reviews` | Basic | `fixture_id`, `rating` (1–10), `review` (optional) |
| PATCH* | `/reviews/<review_id>` | Basic | `rating` and/or `review` |
| DELETE* | `/reviews/<review_id>` | Basic | – |
| GET | `/watchlist` | Basic | – |
| POST* | `/watchlist` | Basic | `fixture_id` |
| DELETE* | `/watchlist/<fixture_id>` | Basic | – |

### Example session (curl)

With the server running, open a terminal and run these commands in the shell (Git Bash, WSL, macOS or Linux). 

```bash
B=https://127.0.0.1:5000
J='Content-Type: application/json'
```

**1. Register user.**

```bash
curl -k -X POST $B/register -H "$J" -d '{"username":"test","password":"password123"}'
```

**2. Create a review as `test`.** The match details are fetched from API-Football using `fixture_id`.

```bash
curl -k -u test:password123 -X POST $B/reviews -H "$J" \
  -d '{"fixture_id":1035037,"rating":8,"review":"Great match"}'
```

**3. List all reviews.**

```bash
curl -k $B/reviews
```

### More curl commands

```bash
# Filter reviews by league, and get one review
curl -k "$B/reviews?league=Premier%20League"
curl -k $B/reviews/1

# Update your own review
curl -k -u test:password123 -X PATCH $B/reviews/1 -H "$J" -d '{"rating":9}'

# Add to, list, and remove from your watchlist
curl -k -u test:password123 -X POST $B/watchlist -H "$J" -d '{"fixture_id":1035037}'
curl -k -u test:password123 $B/watchlist
curl -k -u test:password123 -X DELETE $B/watchlist/1035037

# Delete your own review
curl -k -u test:password123 -X DELETE $B/reviews/1
```

# Resources and AI

Each code file has an AI Overview regarding the file including what AI did, what I did, and 
potentialyl what I had learned from using it. While AI (Claude) was used in creating parts of this API, the 
decisions were still human made and vetted. I was able to use AI to help me learn and create 
software in a manner similar to what professional pracices would be while still writing the
majority of code and logic within the program. Overall, AI was documented through the overviews over 
each file, and was a useful tool to supplement my learning and project building for this project without
being used as a crutch or unethical source of information for my academic learning. 