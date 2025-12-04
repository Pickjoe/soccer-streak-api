from typing import List, Dict
from .betsapi_client import betsapi
from datetime import datetime, timedelta


class OhioLeagueFilter:

    def get_ohio_upcoming_games(self, date: str) -> List[Dict]:
        """Get Ohio-legal upcoming games for a specific date"""

        # Handle 'today' keyword
        if date == 'today':
            date = datetime.now().strftime('%Y%m%d')

        # Get all upcoming games for the date
        response = betsapi.get_upcoming_games(day=date, skip_esports=True)

        if not response.get('success'):
            return []

        all_games = response.get('results', [])

        # Filter for Ohio-legal leagues
        ohio_games = betsapi.get_ohio_legal_games_by_id(all_games, 'upcoming')

        return ohio_games

    def get_ohio_ended_games(self, date: str, days_back: int = 30) -> List[Dict]:
        """Get Ohio-legal ended games for analysis"""

        ohio_games = []

        # Get games for multiple days back
        for i in range(days_back):
            target_date = datetime.strptime(date, '%Y%m%d') - timedelta(days=i)
            date_str = target_date.strftime('%Y%m%d')

            response = betsapi.get_ended_games(day=date_str, skip_esports=True)

            if response.get('success'):
                all_games = response.get('results', [])
                daily_ohio_games = betsapi.get_ohio_legal_games_by_id(all_games, 'ended')
                ohio_games.extend(daily_ohio_games)

        return ohio_games