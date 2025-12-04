from app.services.filter import ohio_filter
from app.services.streak_analyzer import streak_analyzer


def test_july_5_games():
    print("🔥 JULY 5, 2025 GAMES WITH STREAK ANALYSIS")
    print("=" * 70)

    # Get July 5, 2025 games
    july_5_games = ohio_filter.get_ohio_games_by_date('20250705')
    print(f"📅 July 5, 2025 Games: {len(july_5_games)}")
    print()

    if not july_5_games:
        print("❌ No games found for July 5, 2025")
        return

    # Analyze games for streaks
    analyses = streak_analyzer.analyze_todays_games_for_streaks(july_5_games)

    for i, analysis in enumerate(analyses, 1):
        # Game info
        home = analysis['home_team']
        away = analysis['away_team']
        league = analysis['league']
        time = analysis['kickoff_time']

        # Streak info
        home_streak = analysis['home_streak']
        away_streak = analysis['away_streak']

        home_count = home_streak['streak_count']
        home_type = home_streak['streak_type'] or "none"

        away_count = away_streak['streak_count']
        away_type = away_streak['streak_type'] or "none"

        # Only highlight if 5+
        home_display = f"{home_count} {home_type}"
        away_display = f"{away_count} {away_type}"

        if home_count >= 5:
            home_display += " 🔥"
        if away_count >= 5:
            away_display += " 🔥"

        # Print game
        print(f"{i:2d}. {home} vs {away} | {league} | {time}")
        print(f"    {home}: {home_display}")
        print(f"    {away}: {away_display}")
        print()

    # Summary
    highlighted = len(
        [a for a in analyses if a['home_streak']['streak_count'] >= 5 or a['away_streak']['streak_count'] >= 5])

    print("📊 SUMMARY:")
    print(f"🔥 Games with 5+ streaks: {highlighted}")
    print(f"⚪ Normal games: {len(analyses) - highlighted}")


if __name__ == "__main__":
    test_july_5_games()