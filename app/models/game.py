from datetime import datetime
from typing import Optional


class Game:
    def __init__(self, api_data: dict):
        """Initialize Game from B365API response"""

        # Basic game info
        self.id = api_data.get('id')
        self.sport_id = api_data.get('sport_id')
        self.time = int(api_data.get('time', 0))
        self.time_status = api_data.get('time_status')

        # League info
        league = api_data.get('league', {})
        self.league_id = league.get('id')
        self.league_name = league.get('name')
        self.league_cc = league.get('cc')

        # Team info
        home = api_data.get('home', {})
        away = api_data.get('away', {})

        self.home_id = home.get('id')
        self.home_name = home.get('name')
        self.away_id = away.get('id')
        self.away_name = away.get('name')

        # Score analysis
        self.raw_score = api_data.get('ss')  # "2-1" or None
        self.home_score = None
        self.away_score = None
        self.total_goals = None

        # Parse score if available
        if self.raw_score:
            self._parse_score()

    def _parse_score(self):
        """Parse score string like '2-1' into individual components"""
        if self.raw_score and '-' in str(self.raw_score):
            try:
                parts = str(self.raw_score).split('-')
                if len(parts) >= 2:
                    self.home_score = int(parts[0])
                    self.away_score = int(parts[1])
                    self.total_goals = self.home_score + self.away_score
            except (ValueError, IndexError):
                # Handle bad score formats
                pass

    def is_finished(self) -> bool:
        """Check if game has finished (has a score)"""
        return self.raw_score is not None and self.total_goals is not None

    def is_odd_total(self) -> Optional[bool]:
        """Check if total goals is odd number"""
        if self.total_goals is not None:
            return self.total_goals % 2 == 1
        return None

    def is_even_total(self) -> Optional[bool]:
        """Check if total goals is even number"""
        if self.total_goals is not None:
            return self.total_goals % 2 == 0
        return None

    def get_odd_even_type(self) -> Optional[str]:
        """Get 'odd' or 'even' string"""
        if self.is_odd_total():
            return 'odd'
        elif self.is_even_total():
            return 'even'
        return None

    def get_datetime(self) -> datetime:
        """Convert timestamp to readable datetime"""
        return datetime.fromtimestamp(self.time)

    def get_time_string(self) -> str:
        """Get formatted time string"""
        return self.get_datetime().strftime('%H:%M')

    def involves_team(self, team_id: str) -> bool:
        """Check if this game involves a specific team"""
        return self.home_id == team_id or self.away_id == team_id

    def get_opponent(self, team_id: str) -> Optional[dict]:
        """Get opponent info for a specific team"""
        if self.home_id == team_id:
            return {'id': self.away_id, 'name': self.away_name}
        elif self.away_id == team_id:
            return {'id': self.home_id, 'name': self.home_name}
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output"""
        return {
            'id': self.id,
            'home_team': self.home_name,
            'away_team': self.away_name,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'total_goals': self.total_goals,
            'odd_even': self.get_odd_even_type(),
            'time': self.get_time_string(),
            'league': self.league_name,
            'is_finished': self.is_finished()
        }

    def __str__(self):
        """String representation"""
        score_str = self.raw_score or "vs"
        return f"{self.home_name} {score_str} {self.away_name}"

    def __repr__(self):
        return f"Game(id={self.id}, {self.home_name} vs {self.away_name}, score={self.raw_score})"