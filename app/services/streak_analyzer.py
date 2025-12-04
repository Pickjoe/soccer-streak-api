from typing import List, Dict, Optional
from ..models.game import Game


class OddEvenStreakAnalyzer:
    def __init__(self):
        pass

    def analyze_team_streak(self, team_id: str, team_games: List[Game]) -> Dict:
        """
        Analyze odd/even streak for a specific team

        Args:
            team_id: Team ID to analyze
            team_games: List of team's recent finished games (newest first)

        Returns:
            Dict with streak analysis
        """

        # Filter only finished games involving this team
        finished_games = [game for game in team_games if game.is_finished() and game.involves_team(team_id)]

        if not finished_games:
            return {
                'team_id': team_id,
                'streak_count': 0,
                'streak_type': None,
                'games_analyzed': 0,
                'highlight_level': 'none'
            }

        # Sort by most recent first
        finished_games.sort(key=lambda x: x.time, reverse=True)

        # Find current streak
        current_streak = 0
        streak_type = None  # 'odd' or 'even'

        for game in finished_games:
            if game.total_goals is None:
                continue

            game_type = game.get_odd_even_type()

            if current_streak == 0:
                # First game sets the streak type
                streak_type = game_type
                current_streak = 1
            else:
                # Check if streak continues
                if streak_type == game_type:
                    current_streak += 1
                else:
                    # Streak broken
                    break

        # Determine highlight level
        highlight_level = 'none'
        if current_streak >= 7:
            highlight_level = 'green'  # Your betting signal
        elif current_streak >= 5:
            highlight_level = 'yellow'  # Worth watching

        return {
            'team_id': team_id,
            'streak_count': current_streak,
            'streak_type': streak_type,
            'games_analyzed': len(finished_games),
            'highlight_level': highlight_level
        }

    def analyze_todays_games_for_streaks(self, upcoming_games: List[Game]) -> List[Dict]:
        """
        Analyze all today's games for team streaks

        Args:
            upcoming_games: Today's upcoming games

        Returns:
            List of game analyses with team streaks
        """
        from .filter import ohio_filter

        game_analyses = []

        # Get recent finished games for streak analysis
        recent_finished = ohio_filter.get_ohio_finished_games(days_back=30)

        for game in upcoming_games:
            home_team_id = game.home_id
            away_team_id = game.away_id

            # Get games for each team
            home_team_games = [g for g in recent_finished if g.involves_team(home_team_id)]
            away_team_games = [g for g in recent_finished if g.involves_team(away_team_id)]

            # Analyze streaks
            home_streak = self.analyze_team_streak(home_team_id, home_team_games)
            away_streak = self.analyze_team_streak(away_team_id, away_team_games)

            # Create game analysis
            game_analysis = {
                'game_id': game.id,
                'home_team': game.home_name,
                'away_team': game.away_name,
                'league': game.league_name,
                'kickoff_time': game.get_time_string(),
                'home_streak': home_streak,
                'away_streak': away_streak,
                'betting_signal': self._get_betting_signal(home_streak, away_streak)
            }

            game_analyses.append(game_analysis)

        return game_analyses

    def _get_betting_signal(self, home_streak: Dict, away_streak: Dict) -> str:
        """Determine betting signal based on team streaks"""

        home_count = home_streak['streak_count']
        away_count = away_streak['streak_count']

        # Your criteria: 7+ consecutive = betting signal
        if home_count >= 7 or away_count >= 7:
            return 'STRONG'  # Green - bet this game
        elif home_count >= 5 or away_count >= 5:
            return 'WATCH'  # Yellow - monitor
        else:
            return 'NORMAL'  # No signal

    def get_betting_opportunities(self, upcoming_games: List[Game]) -> List[Dict]:
        """Get only games with strong betting signals"""

        all_analyses = self.analyze_todays_games_for_streaks(upcoming_games)

        # Filter for strong signals only
        opportunities = [analysis for analysis in all_analyses
                         if analysis['betting_signal'] == 'STRONG']

        return opportunities


# Global analyzer
streak_analyzer = OddEvenStreakAnalyzer()