from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

from app.services.betsapi_client import betsapi
from app.services.streak_analyzer import streak_analyzer
from app.models.game import Game
import uvicorn

app = FastAPI(
    title="Soccer Streak Analyzer API",
    description="Ohio-legal soccer betting analysis API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Soccer Streak Analyzer API", "status": "running"}


@app.get("/api/v1/games/{date}")
def get_games_by_date(date: str):
    """
    Get Ohio-legal games with streak analysis.

    Args:
        date: YYYYMMDD format (e.g., 20240301)
    """
    # --- 1. Validate and parse date ---
    try:
        target_date = datetime.strptime(date, "%Y%m%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYYMMDD, e.g. 20240301."
        )

    today = datetime.now().date()

    if target_date < today:
        # Past date: ended only
        game_type = "ended"
        date_label_suffix = "Ended Games"
        first_page = betsapi.get_ended_games(day=date, skip_esports=True)
        all_games = betsapi.get_all_ended_games_paginated(day=date, skip_esports=True)

    elif target_date == today:
        # Today: both ended + upcoming
        game_type = "both"
        date_label_suffix = "Ended + Upcoming Games"
        first_page = betsapi.get_ended_games(day=date, skip_esports=True)
        ended_games = betsapi.get_all_ended_games_paginated(day=date, skip_esports=True)
        upcoming_games = betsapi.get_all_upcoming_games_paginated(day=date, skip_esports=True)
        all_games = ended_games + upcoming_games

    else:
        # Future date: upcoming only
        game_type = "upcoming"
        date_label_suffix = "Upcoming Games"
        first_page = betsapi.get_upcoming_games(day=date, skip_esports=True)
        all_games = betsapi.get_all_upcoming_games_paginated(day=date, skip_esports=True)

    # Make sure we have a dict before trying to use .get()
    pager = first_page.get("pager", {}) if isinstance(first_page, dict) else {}

    # --- 3. Filter for Ohio-legal games ---
    ohio_games = betsapi.get_ohio_legal_games_by_id(all_games, game_type)

    # --- 4. For each game, get history + streaks + signal ---
    formatted_games = []

    for game in ohio_games:
        league_name = game.get("ohio_league_name", "Unknown")
        home = game.get("home", {}).get("name", "Unknown")
        away = game.get("away", {}).get("name", "Unknown")
        score = game.get("ss", "No score")
        game_time = int(game.get("time", 0) or 0)
        game_id = game.get("id")

        # Fetch event history (past matches / H2H) - works for both ended & upcoming
        history = betsapi.get_event_history(game_id, qty=20)
        time.sleep(0.5)  # throttle / respect rate limits

        results = history.get("results", {}) if isinstance(history, dict) else {}
        home_history = results.get("home", []) or []
        away_history = results.get("away", []) or []

        home_streak = streak_analyzer.analyze_from_history(game_time, home_history)
        away_streak = streak_analyzer.analyze_from_history(game_time, away_history)
        signal = streak_analyzer.get_signal(home_streak, away_streak)

        # Convert kickoff time to Eastern using your Game model
        game_obj = Game(game)
        kickoff_time_str = game_obj.get_eastern_time_string()

        formatted_games.append({
            "game_id": game_id,
            "home_team": home,
            "away_team": away,
            "score": score,
            "league": league_name,
            "kickoff_time": kickoff_time_str,
            "home_streak": home_streak,
            "away_streak": away_streak,
            "signal": signal
        })

    # --- 5. Pagination info (safe calc) ---
    total = int(pager.get("total", 0) or 0)
    per_page = int(pager.get("per_page", 50) or 50)
    if per_page > 0 and total > 0:
        pages_fetched = (total + per_page - 1) // per_page
    else:
        pages_fetched = 0

    # --- 6. Final response ---
    return {
        "success": True,
        "date": f"{date} ({date_label_suffix})",
        "pagination": {
            "total_games": total,
            "per_page": per_page,
            "pages_fetched": pages_fetched
        },
        "ohio_legal_games": len(ohio_games),
        "games": formatted_games
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
