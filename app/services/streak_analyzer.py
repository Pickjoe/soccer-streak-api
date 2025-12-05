from typing import List, Dict
from ..models.game import Game


class OddEvenStreakAnalyzer:
    def __init__(self):
        pass

    def analyze_from_history(self, main_game_time: int, team_history: List[Dict]) -> Dict:
        """
        Analyze streak from event history API response

        Args:
            main_game_time: Unix timestamp of the main game
            team_history: Raw API history array (home or away)

        Returns:
            Dict with streak_count, streak_type
        """
        # Filter to only games BEFORE main game
        filtered = [g for g in team_history if int(g.get('time', 0)) < main_game_time]

        # Sort by time descending (most recent first)
        filtered.sort(key=lambda x: int(x.get('time', 0)), reverse=True)

        # Calculate streak
        streak_count = 0
        streak_type = None

        for raw_game in filtered:
            game = Game(raw_game)
            if not game.is_finished():
                continue

            current_type = game.get_odd_even_type()

            if streak_count == 0:
                streak_type = current_type
                streak_count = 1
            elif current_type == streak_type:
                streak_count += 1
            else:
                break

        return {
            'streak_count': streak_count,
            'streak_type': streak_type
        }

    def get_signal(self, home_streak: Dict, away_streak: Dict) -> str:
        """Determine betting signal based on streaks"""
        home_count = home_streak.get('streak_count', 0)
        away_count = away_streak.get('streak_count', 0)

        if home_count >= 7 or away_count >= 7:
            return 'STRONG'
        elif home_count >= 5 or away_count >= 5:
            return 'WATCH'
        return 'NORMAL'


# Global analyzer
streak_analyzer = OddEvenStreakAnalyzer()