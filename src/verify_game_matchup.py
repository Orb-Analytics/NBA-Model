#!/usr/bin/env python3
"""
Verify Game Matchup Consistency
Author: Orb Analytics (Liam Chaitin)
Purpose: Verify that games in training set match games in Novig odds file
         to prevent duplicate/incorrect data from being used for predictions
"""

import pandas as pd
import os
import sys
from datetime import datetime

# Mapping from Novig abbreviations to full team names (as used in training set)
NOVIG_TO_FULL_NAME = {
    'ATL': 'Atlanta', 'BOS': 'Boston', 'BKN': 'Brooklyn', 'CHA': 'Charlotte',
    'CHI': 'Chicago', 'CLE': 'Cleveland', 'DAL': 'Dallas', 'DEN': 'Denver',
    'DET': 'Detroit', 'GSW': 'Golden State', 'HOU': 'Houston', 'IND': 'Indiana',
    'LAC': 'La Clippers', 'LAL': 'La Lakers', 'MEM': 'Memphis', 'MIA': 'Miami',
    'MIL': 'Milwaukee', 'MIN': 'Minnesota', 'NOP': 'New Orleans', 'NYK': 'New York',
    'OKC': 'Okla City', 'ORL': 'Orlando', 'PHI': 'Philadelphia', 'PHX': 'Phoenix',
    'POR': 'Portland', 'SAC': 'Sacramento', 'SAS': 'San Antonio', 'TOR': 'Toronto',
    'UTA': 'Utah', 'WAS': 'Washington'
}


def get_novig_games(date_str):
    """Load games from Novig odds file for a given date.
    
    Returns:
        set: Set of tuples (team1, team2) where teams are sorted alphabetically
    """
    novig_file = f"data/novig-odds/novig_nba_spreads_{date_str}.csv"
    
    if not os.path.exists(novig_file):
        print(f"⚠️  Novig file not found: {novig_file}")
        return None
    
    try:
        df = pd.read_csv(novig_file)
        games = set()
        
        for _, row in df.iterrows():
            fav_abbrev = row['fav_team'].upper()
            dog_abbrev = row['dog_team'].upper()
            
            # Convert to full names
            fav_full = NOVIG_TO_FULL_NAME.get(fav_abbrev)
            dog_full = NOVIG_TO_FULL_NAME.get(dog_abbrev)
            
            if not fav_full or not dog_full:
                print(f"⚠️  Unknown team abbreviation: {fav_abbrev} or {dog_abbrev}")
                continue
            
            # Create matchup (sorted for consistent comparison)
            matchup = tuple(sorted([fav_full, dog_full]))
            games.add(matchup)
        
        return games
    
    except Exception as e:
        print(f"❌ Error reading Novig file: {e}")
        return None


def get_training_set_games(date_str):
    """Load games from training set for a given date.
    
    Returns:
        set: Set of tuples (team1, team2) where teams are sorted alphabetically
    """
    training_file = "data/NBA Training Set 25-26.csv"
    
    if not os.path.exists(training_file):
        print(f"❌ Training set not found: {training_file}")
        return None
    
    try:
        df = pd.read_csv(training_file)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Filter for the specific date
        date_games = df[df['Date'] == date_str]
        
        games = set()
        for _, row in date_games.iterrows():
            team1 = row['Home']
            team2 = row['Away']
            
            # Create matchup (sorted for consistent comparison)
            matchup = tuple(sorted([team1, team2]))
            games.add(matchup)
        
        return games
    
    except Exception as e:
        print(f"❌ Error reading training set: {e}")
        return None


def verify_games(date_str, verbose=True):
    """Verify that games in training set match games in Novig odds.
    
    Args:
        date_str: Date to verify (YYYY-MM-DD format)
        verbose: Whether to print detailed output
    
    Returns:
        bool: True if games match, False otherwise
    """
    if verbose:
        print("="*80)
        print(f"🔍 VERIFYING GAME MATCHUPS FOR {date_str}")
        print("="*80)
    
    # Get games from both sources
    novig_games = get_novig_games(date_str)
    training_games = get_training_set_games(date_str)
    
    if novig_games is None or training_games is None:
        print("❌ Could not load game data for verification")
        return False
    
    if verbose:
        print(f"\n📊 Novig odds file: {len(novig_games)} games")
        print(f"📊 Training set: {len(training_games)} games")
    
    # Check for perfect match
    if novig_games == training_games:
        if verbose:
            print(f"\n✅ ALL GAMES MATCH! ({len(novig_games)} games)")
            print("\nMatchups:")
            for game in sorted(novig_games):
                print(f"   • {game[0]} vs {game[1]}")
        return True
    
    # If not matching, show differences
    print(f"\n❌ MISMATCH DETECTED!")
    
    # Games in Novig but not in training set
    novig_only = novig_games - training_games
    if novig_only:
        print(f"\n⚠️  Games in Novig odds but NOT in training set ({len(novig_only)}):")
        for game in sorted(novig_only):
            print(f"   • {game[0]} vs {game[1]}")
    
    # Games in training set but not in Novig
    training_only = training_games - novig_games
    if training_only:
        print(f"\n⚠️  Games in training set but NOT in Novig odds ({len(training_only)}):")
        for game in sorted(training_only):
            print(f"   • {game[0]} vs {game[1]}")
    
    # Games that match
    matching = novig_games & training_games
    if matching and verbose:
        print(f"\n✅ Games that DO match ({len(matching)}):")
        for game in sorted(matching):
            print(f"   • {game[0]} vs {game[1]}")
    
    print("\n" + "="*80)
    print("🚨 VERIFICATION FAILED - Games do not match!")
    print("Please check data sources and re-run data pipeline if needed.")
    print("="*80)
    
    return False


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify game matchup consistency')
    parser.add_argument('--date', type=str, default=None,
                       help='Date to verify (YYYY-MM-DD, default: today)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress detailed output, only show result')
    
    args = parser.parse_args()
    
    # Get date
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Verify games
    success = verify_games(date_str, verbose=not args.quiet)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
