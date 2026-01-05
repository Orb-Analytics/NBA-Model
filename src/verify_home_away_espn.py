#!/usr/bin/env python3
"""
Verify home/away team information against ESPN NBA schedule.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

def get_espn_games_for_date(date):
    """Scrape ESPN schedule for a specific date."""
    date_str = date.strftime('%Y%m%d')
    url = f'https://www.espn.com/nba/schedule/_/date/{date_str}'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        games = []
        
        # Find all game containers
        game_rows = soup.find_all('tr', class_='Table__TR')
        
        for row in game_rows:
            teams = row.find_all('span', class_='Table__Team')
            if len(teams) == 2:
                away_team = teams[0].get_text(strip=True)
                home_team = teams[1].get_text(strip=True)
                
                games.append({
                    'away': away_team,
                    'home': home_team
                })
        
        return games
    except Exception as e:
        print(f"Error scraping ESPN for {date}: {e}")
        return None

def normalize_team_name(espn_name):
    """Convert ESPN team name to our dataset format."""
    mapping = {
        'LA Lakers': 'La Lakers',
        'LA Clippers': 'La Clippers',
        'Oklahoma City': 'Okla City',
        'San Antonio': 'San Antonio',
        'Golden State': 'Golden State',
        'New York': 'New York',
        'New Orleans': 'New Orleans',
        # Add full names
        'Atlanta Hawks': 'Atlanta',
        'Boston Celtics': 'Boston',
        'Brooklyn Nets': 'Brooklyn',
        'Charlotte Hornets': 'Charlotte',
        'Chicago Bulls': 'Chicago',
        'Cleveland Cavaliers': 'Cleveland',
        'Dallas Mavericks': 'Dallas',
        'Denver Nuggets': 'Denver',
        'Detroit Pistons': 'Detroit',
        'Golden State Warriors': 'Golden State',
        'Houston Rockets': 'Houston',
        'Indiana Pacers': 'Indiana',
        'LA Clippers': 'La Clippers',
        'Los Angeles Clippers': 'La Clippers',
        'LA Lakers': 'La Lakers',
        'Los Angeles Lakers': 'La Lakers',
        'Memphis Grizzlies': 'Memphis',
        'Miami Heat': 'Miami',
        'Milwaukee Bucks': 'Milwaukee',
        'Minnesota Timberwolves': 'Minnesota',
        'New Orleans Pelicans': 'New Orleans',
        'New York Knicks': 'New York',
        'Oklahoma City Thunder': 'Okla City',
        'Orlando Magic': 'Orlando',
        'Philadelphia 76ers': 'Philadelphia',
        'Phoenix Suns': 'Phoenix',
        'Portland Trail Blazers': 'Portland',
        'Sacramento Kings': 'Sacramento',
        'Sacremento Kings': 'Sacramento',  # Handle typo in our data
        'San Antonio Spurs': 'San Antonio',
        'Toronto Raptors': 'Toronto',
        'Utah Jazz': 'Utah',
        'Washington Wizards': 'Washington'
    }
    
    return mapping.get(espn_name, espn_name)

def verify_with_espn():
    """Compare our dataset against ESPN schedule."""
    
    # Load our data
    df = pd.read_csv('data/NBA Training Set 25-26.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter to current season
    cutoff_date = pd.to_datetime('2025-10-22')
    df_season = df[df['Date'] >= cutoff_date].copy()
    
    print("="*80)
    print("VERIFYING AGAINST ESPN NBA SCHEDULE")
    print("="*80)
    print()
    
    # Get last 7 days with games
    unique_dates = sorted(df_season['Date'].dt.date.unique())
    recent_dates = unique_dates[-7:]
    
    print(f"Checking last 7 dates with games: {recent_dates[0]} to {recent_dates[-1]}")
    print("-"*80)
    
    errors = []
    total_checked = 0
    
    for date in recent_dates:
        print(f"\n{date}:")
        
        # Get ESPN games
        espn_games = get_espn_games_for_date(datetime.combine(date, datetime.min.time()))
        
        if espn_games is None:
            print("  ❌ Could not fetch ESPN data")
            continue
        
        if not espn_games:
            print("  ⚪ No games on ESPN")
            continue
        
        # Get our games
        our_games = df_season[df_season['Date'].dt.date == date]
        
        print(f"  ESPN: {len(espn_games)} games | Our data: {len(our_games)} games")
        
        # Check each of our games
        for _, our_game in our_games.iterrows():
            our_away = our_game['Away']
            our_home = our_game['Home']
            
            # Try to find matching ESPN game
            found_match = False
            for espn_game in espn_games:
                espn_away = normalize_team_name(espn_game['away'])
                espn_home = normalize_team_name(espn_game['home'])
                
                if espn_away == our_away and espn_home == our_home:
                    found_match = True
                    break
            
            if found_match:
                print(f"  ✅ {our_away} @ {our_home}")
                total_checked += 1
            else:
                # Check if teams are swapped
                swapped_match = False
                for espn_game in espn_games:
                    espn_away = normalize_team_name(espn_game['away'])
                    espn_home = normalize_team_name(espn_game['home'])
                    
                    if espn_away == our_home and espn_home == our_away:
                        swapped_match = True
                        error = {
                            'date': date,
                            'our_matchup': f"{our_away} @ {our_home}",
                            'espn_matchup': f"{espn_away} @ {espn_home}",
                            'issue': 'HOME/AWAY SWAPPED'
                        }
                        errors.append(error)
                        print(f"  ❌ SWAPPED: Our data says {our_away} @ {our_home}")
                        print(f"             ESPN says {espn_away} @ {espn_home}")
                        break
                
                if not swapped_match:
                    print(f"  ⚠️  Could not match: {our_away} @ {our_home}")
        
        time.sleep(1)  # Be nice to ESPN
    
    print()
    print("="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Games checked: {total_checked}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print(f"\n❌ Found {len(errors)} home/away mismatches:")
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error['date']}")
            print(f"   Our data: {error['our_matchup']}")
            print(f"   ESPN:     {error['espn_matchup']}")
            print(f"   Issue:    {error['issue']}")
    else:
        print("\n✅ All games match ESPN schedule!")
    
    return errors

if __name__ == "__main__":
    errors = verify_with_espn()
