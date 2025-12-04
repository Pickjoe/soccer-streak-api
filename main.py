from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.services.betsapi_client import betsapi

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


@app.get("/api/v1/games/march1")
def get_march1_games():
    """Get Ohio-legal games for March 1st - exact copy from working test"""

    # Get first page to see pagination info
    first_page = betsapi.get_ended_games(day='20240301', skip_esports=True)
    pager = first_page.get('pager', {})

    # Get all ended games
    all_ended_games = betsapi.get_all_ended_games_paginated('20240301', skip_esports=True)

    # Filter for Ohio-legal games
    ohio_ended = betsapi.get_ohio_legal_games_by_id(all_ended_games, 'ended')

    # Format for API response
    formatted_games = []
    for game in ohio_ended:
        league_name = game.get('ohio_league_name', 'Unknown')
        home = game.get('home', {}).get('name', 'Unknown')
        away = game.get('away', {}).get('name', 'Unknown')
        score = game.get('ss', 'No score')
        time = game.get('time')

        formatted_games.append({
            "home_team": home,
            "away_team": away,
            "score": score,
            "league": league_name,
            "kickoff_time": time,
            "game_id": game.get('id')
        })

    return {
        "success": True,
        "date": "March 1st, 2024 (Ended Games)",
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