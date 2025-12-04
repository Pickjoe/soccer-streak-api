from app.services.betsapi_client import betsapi


def show_paginated_leagues():
    print("🔍 ALL SOCCER LEAGUES (FULL CATALOG)")
    print("=" * 60)

    # Get first page to see pagination info
    first_page = betsapi.get_all_soccer_leagues()
    pager = first_page.get('pager', {})

    print(f"Total leagues: {pager.get('total', 0)}")
    print(f"Per page: {pager.get('per_page', 0)}")
    print(f"Pages needed: {(pager.get('total', 0) + pager.get('per_page', 100) - 1) // pager.get('per_page', 100)}")
    print()

    # Get all leagues
    print("📥 Fetching all leagues...")
    all_leagues = betsapi.get_all_leagues_paginated()

    print(f"✅ Got {len(all_leagues)} total leagues")
    print()

    # Show all leagues
    for i, league in enumerate(all_leagues, 1):
        league_id = league.get('id')
        name = league.get('name')
        cc = league.get('cc', 'N/A')

        print(f"{i:4d}. ID: {league_id:4s} | {name} | {cc}")


if __name__ == "__main__":
    show_paginated_leagues()