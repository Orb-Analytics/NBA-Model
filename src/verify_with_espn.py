#!/usr/bin/env python3
"""
Verify home/away team information using ESPN's public API.
Much faster and doesn't require authentication.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta

def get_espn_games_for_date(date):
    """Fetch games from ESPN API for a specific date."""
    # ESPN API format: YYYYMMDD
    date_str = date.strftime('%Y%m%d')
    url = f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}'
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        games = []
        for event in data.get('events', []):
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            # ESPN format: [0] is usually home, [1] is usually away
            # But check homeAway field to be sure
            home_team = None
            away_team = None
            
            for comp in competitors:
                team_name = comp['team']['displayName']
                # Simplify team names to match our format
                team_name = team_name.replace('LA ', 'La ').replace('LA Clippers', 'La Clippers')
                
                if comp['homeAway'] == 'home':
                    home_team = team_name
                else:
                    away_team = team_name
            
            if home_team and away_team:
                games.append({
                    'away': away_team,
                    'home': home_team,
                    'status': event.get('status', {}).get('type', {}).get('description', 'Unknown')
                })
        
        return games
    except Exception as e:
        print(f"Error fetching {date_str}: {e}")
        return None

def normalize_team_name(name):
    """Normalize team names for comparison."""
    # Handle common variations
    name = name.strip()
    name = name.replace('Los Angeles Lakers', 'La Lakers')
    name = name.replace('Los Angeles Clippers', 'La Clippers')
    name = name.replace('LA Lakers', 'La Lakers')
    name = name.replace('LA Clippers', 'La Clippers')
    name = name.replace('Oklahoma City Thunder', 'Okla City')
    name = name.replace('Oklahoma City', 'Okla City')
    
    # Sometimes ESPN uses just city name
    city_to_full = {
        'Lakers': 'La Lakers',
        'Clippers': 'La Clippers',
        'Thunder': 'Okla City',
    }
    
    for short, full in city_to_full.items():
        if name.endswith(short):
            name = full
    
    return name

def verify_with_espn_api():
    """Compare our dataset against ESPN API data."""
    
    # Load our data
    df = pd.read_csv('data/NBA Training Set 25-26.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter to current season
    cutoff_date = pd.to_datetime('2025-10-22')
    df_season = df[df['Date'] >= cutoff_date].copy()
    
    print("="*80)
    print("VERIFYING HOME/AWAY INFO WITH ESPN API")
    print("="*80)
    print()
    
    # Check last 5 days with games
    unique_dates = sorted(df_season['Date'].dt.date.unique())[-5:]
    
    print(f"Checking last 5 dates: {unique_dates[0]} to {unique_dates[-1]}")
    print("-"*80)
    print()
    
    errors = []
    verified_games = 0
    
    for date in unique_dates:
        print(f"📅 {date}")
        
        # Get ESPN games
        espn_games = get_espn_games_for_date(pd.to_datetime(date))
        
        if espn_games is None:
            print("  ❌ API error\n")
            continue
        
        if not espn_games:
            print("  ⚪ No games\n")
            continue
        
        # Get our games for this date
        our_games = df_season[df_season['Date'].dt.date == date]
        
        print(f"  ESPN API: {len(espn_games)} games")
        print(f"  Our data: {len(our_games)} games")
        
        # Try to match each of our games with ESPN data
        for _, our_game in our_games.iterrows():
            our_home = normalize_team_name(our_game['Home'])
            our_away = normalize_team_name(our_game['Away'])
            
            # Find matching ESPN game
            match_found = False
            for espn_game in espn_games:
                espn_home = normalize_team_name(espn_game['home'])
                espn_away = normalize_team_name(espn_game['away'])
                
                # Check if teams match (in either order - we're flexible)
                teams_match = (
                    (our_home in espn_home or espn_home in our_home) and
                    (our_away in espn_away or espn_away in our_away)
                )
                
                if teams_match:
                    # Found a match - check if home/away is correct
                    home_correct = our_home in espn_home or espn_home in our_home
                    away_correct = our_away in espn_away or espn_away in our_away
                    
                    if home_correct and away_correct:
                        verified_games += 1
                        match_found = True
                        print(f"  ✅ {our_away} @ {our_home}")
                    else:
                        # Home/away swapped!
                        errors.append({
                            'date': date,
                            'our_data': f"{our_away} @ {our_home}",
                            'espn_data': f"{espn_away} @ {espn_home}",
                            'favorite': our_game['Favorite'],
                            'underdog': our_game['Underdog'],
                            'fav_at_home': our_game['Fav. At Home?']
                        })
                        print(f"  ❌ MISMATCH:")
                        print(f"     Our data: {our_away} @ {our_home}")
                        print(f"     ESPN:     {espn_away} @ {espn_home}")
                    break
            
            if not match_found:
                print(f"  ⚠️  Could not match: {our_away} @ {our_home}")
        
        print()
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Verified correct: {verified_games} games")
    print(f"❌ Errors found: {len(errors)} games")
    print()
    
    if errors:
        print("ERRORS DETAIL:")
        print("-"*80)
        for error in errors:
            print(f"\nDate: {error['date']}")
            print(f"  Matchup: {error['favorite']} (fav) vs {error['underdog']} (dog)")
            print(f"  Fav at home? {error['fav_at_home']}")
            print(f"  Our data: {error['our_data']}")
            print(f"  ESPN:     {error['espn_data']}")
            print(f"  → Home/away are SWAPPED!")
    else:
        print("🎉 All games verified correctly!")
    
    return errors

if __name__ == "__main__":
    errors = verify_with_espn_api()
    
    if errors:
        print(f"\n⚠️  Action needed: {len(errors)} games have incorrect home/away data")
