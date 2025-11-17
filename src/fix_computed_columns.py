"""
Fix Computed Columns in NBA Training Set
Author: Orb Analytics (Liam Chaitin)
Purpose: Ensure all computed columns are correctly calculated from base data
"""

import pandas as pd
import numpy as np

def fix_computed_columns(file_path='data/NBA Training Set 25-26.csv'):
    """
    Fix all computed columns in the training set.
    
    Columns to fix:
    1. Fav. At Home? - 1 if Favorite == Home, 0 otherwise
    2. Winner - Team with higher score
    3. Favorite - Underdog (+/-) - Favorite Score - Underdog Score
    4. Favorite Cover? - 1 if (Fav - Dog) > Spread, 0 otherwise
    5. Favorite Win? - 1 if Favorite Score > Underdog Score, 0 otherwise
    6. Home/Away +/- - Home Score - Away Score
    """
    
    print("📂 Loading training set...")
    df = pd.read_csv(file_path)
    print(f"✅ Loaded {len(df)} rows")
    
    # Keep track of changes
    changes = {
        'Fav. At Home?': 0,
        'Winner': 0,
        'Favorite - Underdog (+/-)': 0,
        'Favorite Cover?': 0,
        'Favorite Win?': 0,
        'Home/Away +/-': 0
    }
    
    print("\n🔧 Fixing computed columns...")
    
    for idx, row in df.iterrows():
        # 1. Fix Fav. At Home?
        expected_fav_home = 1 if row['Favorite'] == row['Home'] else 0
        if row['Fav. At Home?'] != expected_fav_home:
            df.at[idx, 'Fav. At Home?'] = expected_fav_home
            changes['Fav. At Home?'] += 1
        
        # For completed games (have scores)
        if pd.notna(row['Favorite Score']) and pd.notna(row['Underdog Score']):
            
            # 2. Fix Winner
            expected_winner = row['Favorite'] if row['Favorite Score'] > row['Underdog Score'] else row['Underdog']
            if row['Winner'] != expected_winner:
                df.at[idx, 'Winner'] = expected_winner
                changes['Winner'] += 1
            
            # 3. Fix Favorite - Underdog (+/-)
            expected_diff = row['Favorite Score'] - row['Underdog Score']
            if pd.isna(row['Favorite - Underdog (+/-)']) or abs(row['Favorite - Underdog (+/-)'] - expected_diff) > 0.01:
                df.at[idx, 'Favorite - Underdog (+/-)'] = expected_diff
                changes['Favorite - Underdog (+/-)'] += 1
            
            # 4. Fix Favorite Cover?
            if pd.notna(row['Spread']):
                expected_cover = 1 if expected_diff > row['Spread'] else 0
                if pd.isna(row['Favorite Cover?']) or row['Favorite Cover?'] != expected_cover:
                    df.at[idx, 'Favorite Cover?'] = expected_cover
                    changes['Favorite Cover?'] += 1
            
            # 5. Fix Favorite Win?
            expected_fav_win = 1 if row['Favorite Score'] > row['Underdog Score'] else 0
            if pd.isna(row['Favorite Win?']) or row['Favorite Win?'] != expected_fav_win:
                df.at[idx, 'Favorite Win?'] = expected_fav_win
                changes['Favorite Win?'] += 1
        
        # 6. Fix Home/Away +/-
        if pd.notna(row['Home Score']) and pd.notna(row['Away Score']):
            expected_home_diff = row['Home Score'] - row['Away Score']
            if pd.isna(row['Home/Away +/-']) or abs(row['Home/Away +/-'] - expected_home_diff) > 0.01:
                df.at[idx, 'Home/Away +/-'] = expected_home_diff
                changes['Home/Away +/-'] += 1
    
    # Save fixed data
    df.to_csv(file_path, index=False)
    print(f"\n💾 Saved fixed data to {file_path}")
    
    # Report changes
    print("\n📊 CHANGES MADE:")
    total_changes = 0
    for col, count in changes.items():
        if count > 0:
            print(f"   {col}: {count} rows fixed")
            total_changes += count
        else:
            print(f"   {col}: ✓ No changes needed")
    
    print(f"\n✅ Total changes: {total_changes}")
    
    return df

if __name__ == "__main__":
    fix_computed_columns()
