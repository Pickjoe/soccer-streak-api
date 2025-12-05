from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.services.betsapi_client import betsapi
from app.services.streak_analyzer import streak_analyzer
from app.models.game import Game
import time
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
    Get Ohio-legal games with streak analysis

    Args:
        date: YYYYMMDD format (e.g., 20240301)
    """
    # Get first page to see pagination info
    first_page = betsapi.get_ended_games(day=date, skip_esports=True)
    pager = first_page.get('pager', {})

    # Get all ended games
    all_ended_games = betsapi.get_all_ended_games_paginated(date, skip_esports=True)
    # Filter for Ohio-legal games
    ohio_ended = betsapi.get_ohio_legal_games_by_id(all_ended_games, 'ended')

    # Format for API response
    formatted_games = []
    for game in ohio_ended:
        league_name = game.get('ohio_league_name', 'Unknown')
        home = game.get('home', {}).get('name', 'Unknown')
        away = game.get('away', {}).get('name', 'Unknown')
        score = game.get('ss', 'No score')
        game_time = int(game.get('time', 0))
        game_id = game.get('id')

        # Get event history (max 20 games)
        history = betsapi.get_event_history(game_id, qty=20)
        time.sleep(0.5)
        results = history.get('results', {})

        # Analyze streaks
        home_streak = streak_analyzer.analyze_from_history(game_time, results.get('home', []))
        away_streak = streak_analyzer.analyze_from_history(game_time, results.get('away', []))
        signal = streak_analyzer.get_signal(home_streak, away_streak)

        # Convert time to Eastern
        game_obj = Game(game)

        formatted_games.append({
            "game_id": game_id,
            "home_team": home,
            "away_team": away,
            "score": score,
            "league": league_name,
            "kickoff_time": game_obj.get_eastern_time_string(),
            "home_streak": home_streak,
            "away_streak": away_streak,
            "signal": signal
        })

    return {
        "success": True,
        "date": f"{date} (Ended Games)",
        "pagination": {
            "total_games": pager.get('total', 0),
            "per_page": pager.get('per_page', 0),
            "pages_fetched": (pager.get('total', 0) + pager.get('per_page', 50) - 1) // pager.get('per_page', 50)
        },
        "ohio_legal_games": len(ohio_ended),
        "games": formatted_games
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)