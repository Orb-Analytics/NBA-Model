#!/usr/bin/env python3
"""
Verify Score Consistency - Check that Favorite/Underdog scores match Home/Away scores

This script checks for mismatches where:
- Favorite Score doesn't match the correct Home/Away score
- Underdog Score doesn't match the correct Home/Away score

These mismatches occur when home/away is corrected but scores aren't updated.
"""

import pandas as pd
from datetime import datetime

def verify_score_consistency(csv_path='data/NBA Training Set 25-26.csv'):
    """
    Verify that Favorite/Underdog scores match their Home/Away scores.
    
    Returns a DataFrame of games with mismatches.
    """
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    mismatches = []
    
    for idx, row in df.iterrows():
        favorite = row['Favorite']
        underdog = row['Underdog']
        home = row['Home']
        away = row['Away']
        
        fav_score = row['Favorite Score']
        dog_score = row['Underdog Score']
        home_score = row['Home Score']
        away_score = row['Away Score']
        fav_at_home = row['Fav. At Home?']
        
        # Skip if any scores are missing
        if pd.isna(fav_score) or pd.isna(dog_score) or pd.isna(home_score) or pd.isna(away_score):
            continue
        
        # Determine expected scores
        if fav_at_home == 1:
            # Favorite is home
            expected_fav_score = home_score
            expected_dog_score = away_score
        else:
            # Favorite is away
            expected_fav_score = away_score
            expected_dog_score = home_score
        
        # Check for mismatches
        fav_mismatch = (fav_score != expected_fav_score)
        dog_mismatch = (dog_score != expected_dog_score)
        
        if fav_mismatch or dog_mismatch:
            mismatches.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Favorite': favorite,
                'Underdog': underdog,
                'Home': home,
                'Away': away,
                'Fav_At_Home': fav_at_home,
                'Fav_Score_Current': fav_score,
                'Fav_Score_Expected': expected_fav_score,
                'Dog_Score_Current': dog_score,
                'Dog_Score_Expected': expected_dog_score,
                'Home_Score': home_score,
                'Away_Score': away_score,
                'Fav_Mismatch': fav_mismatch,
                'Dog_Mismatch': dog_mismatch
            })
    
    return pd.DataFrame(mismatches)


def main():
    print("="*100)
    print("🔍 VERIFYING SCORE CONSISTENCY")
    print("="*100)
    print()
    
    mismatches = verify_score_consistency()
    
    if len(mismatches) == 0:
        print("✅ All scores are consistent! No mismatches found.")
        print()
        return 0
    
    print(f"⚠️  Found {len(mismatches)} games with score mismatches:")
    print()
    
    for _, row in mismatches.iterrows():
        print(f"📅 {row['Date']}: {row['Favorite']} vs {row['Underdog']}")
        print(f"   Home/Away: {row['Away']} @ {row['Home']} (Fav at home: {row['Fav_At_Home']})")
        print(f"   Actual Scores: {row['Away']} {row['Away_Score']} @ {row['Home']} {row['Home_Score']}")
        
        if row['Fav_Mismatch']:
            print(f"   ❌ Favorite score: {row['Fav_Score_Current']} (should be {row['Fav_Score_Expected']})")
        
        if row['Dog_Mismatch']:
            print(f"   ❌ Underdog score: {row['Dog_Score_Current']} (should be {row['Dog_Score_Expected']})")
        
        print()
    
    print("="*100)
    print(f"⚠️  Total mismatches: {len(mismatches)}")
    print("="*100)
    print()
    print("To fix these issues, run:")
    print("  1. Update src/fix_home_away_errors.py to include these dates")
    print("  2. Run: python src/fix_home_away_errors.py")
    print("  3. Run: python src/daily_backtest_update.py")
    print()
    
    return 1


if __name__ == "__main__":
    exit(main())
