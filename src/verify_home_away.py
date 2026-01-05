#!/usr/bin/env python3
"""
Verify home/away team information is correct for the 2025-26 season.
Cross-references the 'Fav. At Home?' column with Away/Home columns.
"""

import pandas as pd
from datetime import datetime

def verify_home_away_consistency():
    """Check if home/away information is consistent in the dataset."""
    
    # Load data
    df = pd.read_csv('data/NBA Training Set 25-26.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter to Oct 22, 2025 onwards
    cutoff_date = pd.to_datetime('2025-10-22')
    df_season = df[df['Date'] >= cutoff_date].copy()
    
    print("="*80)
    print("HOME/AWAY VERIFICATION - 2025-26 SEASON")
    print(f"Games since {cutoff_date.date()}: {len(df_season)}")
    print("="*80)
    print()
    
    # Check 1: Verify Fav. At Home? matches the actual home/away columns
    print("CHECK 1: Verifying 'Fav. At Home?' consistency")
    print("-"*80)
    
    errors = []
    
    for idx, row in df_season.iterrows():
        date = row['Date']
        favorite = row['Favorite']
        underdog = row['Underdog']
        fav_at_home = row['Fav. At Home?']
        away_team = row['Away']
        home_team = row['Home']
        
        # Determine expected value
        if fav_at_home == 1:
            # Favorite should be home, underdog should be away
            expected_home = favorite
            expected_away = underdog
        else:
            # Favorite should be away, underdog should be home
            expected_home = underdog
            expected_away = favorite
        
        # Check if actual matches expected
        if home_team != expected_home or away_team != expected_away:
            errors.append({
                'date': date,
                'favorite': favorite,
                'underdog': underdog,
                'fav_at_home': fav_at_home,
                'expected_home': expected_home,
                'expected_away': expected_away,
                'actual_home': home_team,
                'actual_away': away_team,
                'issue': 'Mismatch'
            })
    
    if errors:
        print(f"❌ Found {len(errors)} inconsistencies:\n")
        for i, error in enumerate(errors[:20], 1):  # Show first 20
            print(f"{i}. Date: {error['date'].date()}")
            print(f"   Matchup: {error['favorite']} (fav) vs {error['underdog']} (dog)")
            print(f"   Fav. At Home?: {error['fav_at_home']}")
            print(f"   Expected: {error['expected_away']} @ {error['expected_home']}")
            print(f"   Actual:   {error['actual_away']} @ {error['actual_home']}")
            print()
        
        if len(errors) > 20:
            print(f"... and {len(errors) - 20} more errors")
    else:
        print("✅ All games have consistent home/away information")
    
    print()
    
    # Check 2: Verify no missing values
    print("CHECK 2: Checking for missing values")
    print("-"*80)
    missing_home = df_season['Home'].isna().sum()
    missing_away = df_season['Away'].isna().sum()
    missing_fav_home = df_season['Fav. At Home?'].isna().sum()
    
    if missing_home > 0:
        print(f"❌ Missing 'Home' values: {missing_home}")
    else:
        print("✅ No missing 'Home' values")
    
    if missing_away > 0:
        print(f"❌ Missing 'Away' values: {missing_away}")
    else:
        print("✅ No missing 'Away' values")
    
    if missing_fav_home > 0:
        print(f"❌ Missing 'Fav. At Home?' values: {missing_fav_home}")
    else:
        print("✅ No missing 'Fav. At Home?' values")
    
    print()
    
    # Check 3: Sample verification
    print("CHECK 3: Recent games sample (last 10)")
    print("-"*80)
    recent = df_season.tail(10)
    for _, row in recent.iterrows():
        fav_location = "Home" if row['Fav. At Home?'] == 1 else "Away"
        print(f"{row['Date'].date()}: {row['Away']} @ {row['Home']} | "
              f"Fav: {row['Favorite']} ({fav_location})")
    
    print()
    print("="*80)
    
    return errors

if __name__ == "__main__":
    errors = verify_home_away_consistency()
    
    if errors:
        print(f"\n⚠️  SUMMARY: Found {len(errors)} games with incorrect home/away information")
        print("These need to be corrected in the dataset.")
    else:
        print("\n✅ SUMMARY: All home/away information is correct!")
