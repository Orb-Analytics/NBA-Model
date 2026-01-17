#!/usr/bin/env python3
"""
Fix ALL Score Mismatches - Automatically fix Favorite/Underdog scores to match Home/Away

This script automatically corrects all games where Favorite/Underdog scores don't match
their corresponding Home/Away scores.
"""

import pandas as pd
import numpy as np

def fix_all_score_mismatches(csv_path='data/NBA Training Set 25-26.csv'):
    """
    Fix all score mismatches by updating Favorite/Underdog scores to match Home/Away.
    """
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    fixed_count = 0
    
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
        spread = row['Spread']
        
        # Skip if any scores are missing
        if pd.isna(fav_score) or pd.isna(dog_score) or pd.isna(home_score) or pd.isna(away_score):
            continue
        
        # Determine expected scores based on Fav. At Home? flag
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
            print(f"Fixing {row['Date'].strftime('%Y-%m-%d')}: {favorite} vs {underdog}")
            print(f"  Before: Fav {fav_score}, Dog {dog_score}")
            
            # Fix the scores
            df.loc[idx, 'Favorite Score'] = expected_fav_score
            df.loc[idx, 'Underdog Score'] = expected_dog_score
            
            print(f"  After:  Fav {expected_fav_score}, Dog {expected_dog_score}")
            
            # Recalculate derived columns
            if pd.notna(expected_fav_score) and pd.notna(expected_dog_score):
                margin = expected_fav_score - expected_dog_score
                df.loc[idx, 'Favorite - Underdog (+/-)'] = margin
                
                # Recalculate Favorite Cover?
                if pd.notna(spread):
                    df.loc[idx, 'Favorite Cover?'] = 1.0 if margin + spread > 0 else 0.0
                    old_cover = row['Favorite Cover?']
                    new_cover = df.loc[idx, 'Favorite Cover?']
                    if old_cover != new_cover:
                        print(f"  ⚠️  Cover changed: {old_cover} → {new_cover}")
            
            fixed_count += 1
            print()
    
    return df, fixed_count


def main():
    print("="*100)
    print("🔧 FIXING ALL SCORE MISMATCHES")
    print("="*100)
    print()
    
    df, fixed_count = fix_all_score_mismatches()
    
    if fixed_count == 0:
        print("✅ No mismatches found!")
        return 0
    
    print("="*100)
    print(f"✅ Fixed {fixed_count} games")
    print("="*100)
    print()
    
    # Save
    df.to_csv('data/NBA Training Set 25-26.csv', index=False)
    print("💾 Saved to data/NBA Training Set 25-26.csv")
    print()
    print("🎯 Next steps:")
    print("  1. Run: python src/daily_backtest_update.py")
    print("  2. Verify: python src/verify_scores_match_home_away.py")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
