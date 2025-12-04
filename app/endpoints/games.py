from app.services.betsapi_client import betsapi


def get_march1_ohio_games():
    """Get Ohio-legal games for March 1st - your exact working logic"""

    # Get first page to see pagination info
    first_page = betsapi.get_ended_games(day='20240301', skip_esports=True)
    pager = first_page.get('pager', {})

    # Get all ended games
    all_ended_games = betsapi.get_all_ended_games_paginated('20240301', skip_esports=True)

    # Filter for Ohio-legal games
    ohio_ended = betsapi.get_ohio_legal_games_by_id(all_ended_games, 'ended')

    # Build response exactly like your test
    games_list = []
    if ohio_ended:
        for i, game in enumerate(ohio_ended, 1):
            league_name = game.get('ohio_league_name', 'Unknown')
            home = game.get('home', {}).get('name', 'Unknown')
            away = game.get('away', {}).get('name', 'Unknown')
            score = game.get('ss', 'No score')
            time = game.get('time')

            games_list.append({
                "game_number": i,
                "match": f"{home} vs {away}",
                "score": score,
                "league": league_name,
                "time": time
            })

    return {
        "success": True,
        "total_games": pager.get('total', 0),
        "per_page": pager.get('per_page', 0),
        "pages_needed": (pager.get('total', 0) + pager.get('per_page', 50) - 1) // pager.get('per_page', 50),
        "total_ended_games": len(all_ended_games),
        "ohio_legal_games": len(ohio_ended),
        "games": games_list
    }