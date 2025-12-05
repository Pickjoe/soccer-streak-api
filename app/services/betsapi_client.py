import time

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


# Ohio-legal league IDs (confirmed from full catalog)
OHIO_TARGET_LEAGUE_IDS = {
    # ===================
    # ENGLAND
    # ===================
    "94": "Premier League",
    "880": "EFL Championship",
    "587": "EFL League One",
    "611": "EFL League Two",
    "1259": "EFL Cup (Carabao Cup)",
    "2481": "FA Cup",
    "1814": "FA Trophy",
    "394": "EFL Trophy",
    "30510": "Community Shield",

    # ===================
    # SPAIN
    # ===================
    "38223": "La Liga",
    "425": "Copa del Rey",
    "6426": "Supercopa de España",

    # ===================
    # ITALY
    # ===================
    "199": "Serie A",
    "2916": "Coppa Italia",
    "3179": "Supercoppa Italiana",

    # ===================
    # GERMANY
    # ===================
    "123": "Bundesliga",
    "2266": "DFB Pokal",
    "6307": "DFL Supercup",

    # ===================
    # FRANCE
    # ===================
    "99": "Ligue 1",
    "1789": "Coupe de France",
    "6197": "Trophée des Champions",

    # ===================
    # PORTUGAL
    # ===================
    "172": "Primeira Liga",
    "614": "Taça de Portugal",
    "1781": "Taça da Liga",
    "6308": "Supertaça Cândido de Oliveira",

    # ===================
    # GREECE
    # ===================
    "910": "Super League Greece",
    "2267": "Greek Cup",

    # ===================
    # JAPAN
    # ===================
    "895": "J1 League",
    "13": "Emperor's Cup",
    "409": "J.League Cup (Levain Cup)",
    "3852": "Japanese Super Cup",

    # ===================
    # MEXICO
    # ===================
    "32373": "Liga MX",
    "1044": "Copa MX",
    "5961": "Campeón de Campeones",
    "5958": "Supercopa MX",
    "3277":" Mexico Clausura",
    "219":" Mexico Apertura",

    # ===================
    # USA
    # ===================
    "242": "MLS",
    "1045": "US Open Cup",
    "17650": "Leagues Cup",
    "34801": "Campeones Cup",

    # ===================
    # SAUDI ARABIA
    # ===================
    "34172": "Saudi Pro League",
    "3467": "King Cup",
    "21661": "Saudi Super Cup",

    # ===================
    # EUROPEAN CLUB COMPETITIONS
    # ===================
    "1040": "UEFA Champions League",
    "5708": "UEFA Champions League Qualifying",
    "1067": "UEFA Europa League",
    "5720": "UEFA Europa League Qualifying",
    "34541": "UEFA Conference League",
    "33931": "UEFA Conference League Qualifying",
    "6388": "UEFA Super Cup",
    "1018": "UEFA Youth League",

    # ===================
    # INTERNATIONAL - UEFA
    # ===================
    "12051": "UEFA Nations League",
    "30974": "UEFA Nations League A",
    "30973": "UEFA Nations League B",
    "30976": "UEFA Nations League C",
    "30975": "UEFA Nations League D",
    "681": "World Cup Qualifying (UEFA)",
    "35624": "Euro 2024",
    "11035": "Euro 2020",
    "5477": "European U21 Championship",
    "461": "European U21 Championship Qualifying",
    "4291": "European U19 Championship",
    "9999": "U17 European Championship",

    # ===================
    # INTERNATIONAL - CONCACAF
    # ===================
    "4374": "CONCACAF Gold Cup",
    "26297": "CONCACAF Gold Cup Qualifying",
    "36174": "CONCACAF Champions Cup",
    "1043": "CONCACAF Champions League",
    "6288": "CONCACAF League",
    "14717": "CONCACAF Nations League",
    "12056": "CONCACAF Nations League Qualifying",
    "28749": "World Cup Qualifying (CONCACAF)",
    "2175": "CONCACAF U20 Championship",
    "15599": "CONCACAF U17 Championship",

    # ===================
    # INTERNATIONAL - CONMEBOL
    # ===================
    "14180": "Copa America",
    "3514": "Copa Libertadores",
    "32482": "Copa Libertadores Qualifying",
    "445": "Copa Sudamericana",
    "4462": "Recopa Sudamericana",
    "3468": "U20 South American Championship",
    "473": "World Cup Qualifying (CONMEBOL)",

    # ===================
    # INTERNATIONAL - AFC (ASIA)
    # ===================
    "767": "AFC Asian Cup",
    "4314": "AFC Asian Cup Qualifying",
    "1014": "AFC Champions League",
    "38252": "AFC Champions League Elite",
    "38266": "AFC Champions League Two",
    "29060": "AFC Champions League Qualifying",
    "1019": "AFC Cup",
    "455": "World Cup Qualifying (AFC)",
    "5946": "AFC U23 Championship",
    "1934": "AFC U19 Championship",

    # ===================
    # INTERNATIONAL - CAF (AFRICA)
    # ===================
    "3361": "Africa Cup of Nations",
    "511": "Africa Cup of Nations Qualifying",
    "1102": "CAF Champions League",
    "1131": "CAF Confederations Cup",
    "3861": "CAF Super Cup",
    "1735": "World Cup Qualifying (CAF)",
    "8445": "African Nations Championship",

    # ===================
    # INTERNATIONAL - FIFA / WORLD
    # ===================
    "3034": "FIFA Club World Cup",
    "38782": "FIFA Intercontinental Cup",
    "33207": "World Cup 2026",
    "29334": "World Cup 2022",
    "8538": "World Cup 2018",
    "5071": "FIFA U20 World Cup",
    "7396": "FIFA U17 World Cup",
    "24458": "World Cup Qualifying",
    "250": "International Match",
    "598": "Friendlies",
    "375": "World Club Friendlies",
    "631": "Elite Club Friendlies",
    "23911":"mexico liga mx de expansion"

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