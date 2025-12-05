import time

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


# Ohio-legal league IDs (confirmed from full catalog)
OHIO_TARGET_LEAGUE_IDS = {
    # English Football
    "94": "Premier League",
    "880": "EFL Championship",
    "587": "EFL League One",
    "611": "EFL League Two",
    "1259": "EFL Cup",
    "2481": "FA Cup",

    # Spain
    "38223": "LaLiga",
    "425": "Copa del Rey",

    # Italy
    "199": "Serie A",

    # Germany
    "123": "Bundesliga",

    # France
    "99": "Ligue 1",

    # Portugal
    "172": "Liga Portugal",

    # Greece
    "910": "Super League Greece",
    "2267": "Greek Cup",

    # Japan
    "895": "J1 League",

    # Americas
    "242": "MLS",
    "32373": "Liga MX",

    # Saudi Arabia
    "34172": "Saudi Pro League",

    # European Competitions
    "1040": "UEFA Champions League",
    "1067": "UEFA Europa League",
    "34541": "UEFA Europa Conference League",
}

class BetsAPIClient:
    def __init__(self):
        self.token = "60160-2APiC3gXTwG7oG"
        self.base_url = "https://api.b365api.com/v3"

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request to B365API"""
        if params is None:
            params = {}

        params['token'] = self.token
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.get(url, params=params)
            print(f"📡 API: {endpoint} - Status: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return {'success': 0, 'results': []}

        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {'success': 0, 'results': []}

    def get_upcoming_games(self, day: str = None, league_id: str = None,
                           team_id: str = None, skip_esports: bool = True) -> List[Dict]:
        """
        Get upcoming games

        Args:
            day: YYYYMMDD format (default: today)
            league_id: Filter by specific league
            team_id: Filter by specific team
            skip_esports: Skip virtual games
        """
        params = {
            'sport_id': 1  # Soccer
        }

        if day is None:
            day = datetime.now().strftime('%Y%m%d')
        params['day'] = day

        if league_id:
            params['league_id'] = league_id

        if team_id:
            params['team_id'] = team_id

        if skip_esports:
            params['skip_esports'] = '1'

        response = self._make_request('events/upcoming', params)

        if response.get('success'):
            return response

        else:
            print(f"❌ No upcoming games found")
            return []

    def get_ended_games(self, day: str = None, league_id: str = None,
                        team_id: str = None, skip_esports: bool = True) -> List[Dict]:
        """
        Get finished games

        Args:
            day: YYYYMMDD format (default: yesterday)
            league_id: Filter by specific league
            team_id: Filter by specific team
            skip_esports: Skip virtual games
        """
        params = {
            'sport_id': 1  # Soccer
        }

        if day is None:
            yesterday = datetime.now() - timedelta(days=1)
            day = yesterday.strftime('%Y%m%d')
        params['day'] = day

        if league_id:
            params['league_id'] = league_id

        if team_id:
            params['team_id'] = team_id

        if skip_esports:
            params['skip_esports'] = '1'

        response = self._make_request('events/ended', params)
        return response
    def get_event_history(self, event_id: str, qty: int = 10) -> Dict:
        """
        Get event history including H2H and team past games

        Args:
            event_id: Event ID from upcoming/ended games
            qty: Number of past games per team (1-20, default: 10)
        """
        # Note: History endpoint uses v1, not v3
        url = "https://api.b365api.com/v1/event/history"

        params = {
            'token': self.token,
            'event_id': event_id,
            'qty': min(qty, 20)  # Max 20 allowed
        }

        try:
            response = requests.get(url, params=params)
            print(f"📡 History for event {event_id} - Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Got history for event {event_id}")
                    return result
                else:
                    print(f"❌ History failed for event {event_id}")
                    return {}
            else:
                print(f"❌ History error: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ History request failed: {e}")
            return {}



    def get_ohio_legal_games_by_id(self, all_games: List[Dict], game_type: str = "upcoming") -> List[Dict]:
        """Filter games to only Ohio-legal leagues using confirmed league IDs"""

        ohio_legal_games = []

        for game in all_games:
            league = game.get('league', {})
            league_id = str(league.get('id', ''))

            # Check if this league is in our Ohio-legal list
            if league_id in OHIO_TARGET_LEAGUE_IDS:
                # Add league name for reference
                game['ohio_league_name'] = OHIO_TARGET_LEAGUE_IDS[league_id]
                ohio_legal_games.append(game)

        return ohio_legal_games

    # Add to betsapi_client.py
    def _get_date_string(self, days_ago: int = 0) -> str:
        """Get date string in YYYYMMDD format"""
        target_date = datetime.now() - timedelta(days=days_ago)
        return target_date.strftime('%Y%m%d')

    def get_all_soccer_leagues(self) -> Dict:
        """Get all soccer leagues with pagination info"""

        params = {
            'sport_id': 1  # Soccer
        }

        response = self._make_request('league', params)

        if response.get('success'):
            return response  # Return full response with pager info
        else:
            return {'success': 0, 'results': [], 'pager': {}}

    def get_all_leagues_paginated(self) -> List[Dict]:
        """Get ALL leagues by fetching all pages"""

        all_leagues = []
        page = 1

        while True:
            params = {
                'sport_id': 1,
                'page': page
            }

            response = self._make_request('league', params)

            if response.get('success'):
                results = response.get('results', [])
                if not results:
                    break  # No more results

                all_leagues.extend(results)
                time.sleep(1)

                # Check if we have more pages
                pager = response.get('pager', {})
                total_pages = (pager.get('total', 0) + pager.get('per_page', 100) - 1) // pager.get('per_page', 100)

                if page >= total_pages:
                    break

                page += 1
            else:
                break

        return all_leagues

    def get_all_ended_games_paginated(self, day: str, skip_esports: bool = True) -> List[Dict]:
        """Get ALL ended games by fetching all pages"""

        all_games = []
        page = 1

        while True:
            params = {
                'sport_id': 1,  # Soccer
                'day': day,
                'page': page
            }

            if skip_esports:
                params['skip_esports'] = 1

            response = self._make_request('events/ended', params)

            if response.get('success'):
                results = response.get('results', [])
                if not results:
                    break  # No more results

                all_games.extend(results)

                # Check if we have more pages
                pager = response.get('pager', {})
                total_pages = (pager.get('total', 0) + pager.get('per_page', 50) - 1) // pager.get('per_page', 50)

                if page >= total_pages:
                    break

                page += 1
            else:
                break

        return all_games

    def get_all_ended_games_paginated(self, day: str, skip_esports: bool = True) -> List[Dict]:
        """Get ALL ended games by fetching all pages"""

        all_games = []
        page = 1

        while True:
            params = {
                'sport_id': 1,  # Soccer
                'day': day,
                'page': page
            }

            if skip_esports:
                params['skip_esports'] = 1

            response = self._make_request('events/ended', params)

            if response.get('success'):
                results = response.get('results', [])
                if not results:
                    break  # No more results

                all_games.extend(results)

                # Check if we have more pages
                pager = response.get('pager', {})
                total_pages = (pager.get('total', 0) + pager.get('per_page', 50) - 1) // pager.get('per_page', 50)

                if page >= total_pages:
                    break

                page += 1
            else:
                break

        return all_games
    def get_all_upcoming_games_paginated(self, day: str, skip_esports: bool = True) -> List[Dict]:
        """Get ALL upcoming games by fetching all pages"""

        all_games = []
        page = 1

        while True:
            params = {
                'sport_id': 1,  # Soccer
                'day': day,
                'page': page
            }

            if skip_esports:
                params['skip_esports'] = 1

            # Note: endpoint is 'events/upcoming' now
            response = self._make_request('events/upcoming', params)

            if response.get('success'):
                results = response.get('results', [])
                if not results:
                    break  # No more results

                all_games.extend(results)

                # Pagination logic (same as ended)
                pager = response.get('pager', {}) or {}
                total = pager.get('total', 0) or 0
                per_page = pager.get('per_page', 50) or 50

                # Protect against division by zero
                if per_page <= 0:
                    break

                total_pages = (total + per_page - 1) // per_page

                if page >= total_pages:
                    break

                page += 1
            else:
                break

        return all_games

# Global instance
betsapi = BetsAPIClient()