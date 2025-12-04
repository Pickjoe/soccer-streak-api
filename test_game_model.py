from app.services.betsapi_client import betsapi
from app.models.game import Game


def test_game_model():
    print("🎮 Testing Game Model")
    print("=" * 50)

    # Test with upcoming games
    print("\n📅 UPCOMING GAMES:")
    upcoming = betsapi.get_upcoming_games()

    if upcoming:
        for i, game_data in enumerate(upcoming[:3]):
            game = Game(game_data)
            print(f"{i + 1}. {game}")
            print(f"   Time: {game.get_time_string()}")
            print(f"   League: {game.league_name}")
            print(f"   Finished: {game.is_finished()}")
            print(f"   Dict: {game.to_dict()}")
            print()

    # Test with finished games
    print("\n🏁 FINISHED GAMES:")
    ended = betsapi.get_ended_games()

    if ended:
        for i, game_data in enumerate(ended[:3]):
            game = Game(game_data)
            print(f"{i + 1}. {game}")
            print(f"   Total Goals: {game.total_goals}")
            print(f"   Odd/Even: {game.get_odd_even_type()}")
            print(f"   Is Odd: {game.is_odd_total()}")
            print(f"   Is Even: {game.is_even_total()}")
            print(f"   Dict: {game.to_dict()}")
            print()


def test_score_parsing():
    print("🧮 Testing Score Parsing")
    print("=" * 30)

    # Test different score formats
    test_scores = [
        {'ss': '2-1'},  # Normal score
        {'ss': '0-0'},  # Draw
        {'ss': '3-2'},  # High scoring
        {'ss': '1-4'},  # Away win
        {'ss': None},  # No score (upcoming)
        {'ss': ''},  # Empty score
    ]

    for i, test_data in enumerate(test_scores):
        # Create minimal game data
        game_data = {
            'id': f'test_{i}',
            'home': {'name': 'Team A', 'id': '1'},
            'away': {'name': 'Team B', 'id': '2'},
            'league': {'name': 'Test League'},
            'time': '1633184100',
            'ss': test_data['ss']
        }

        game = Game(game_data)

        print(f"Score: {game.raw_score}")
        print(f"  Parsed: {game.home_score}-{game.away_score}")
        print(f"  Total: {game.total_goals}")
        print(f"  Type: {game.get_odd_even_type()}")
        print()


if __name__ == "__main__":
    test_game_model()
    test_score_parsing()