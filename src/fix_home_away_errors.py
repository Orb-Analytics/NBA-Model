#!/usr/bin/env python3
"""
Fix the home/away errors identified by ESPN verification.
Swaps Away/Home columns and updates Fav. At Home? flag for affected games.
"""

import pandas as pd
from datetime import datetime

# Load the dataset
df = pd.read_csv('data/NBA Training Set 25-26.csv')

# Convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Define the errors to fix (date, current_away, current_home)
errors_to_fix = [
    ('2025-12-29', 'Okla City', 'Atlanta'),
    ('2025-12-29', 'San Antonio', 'Cleveland'),
    ('2025-12-30', 'Memphis', 'Philadelphia'),
    ('2025-12-31', 'Okla City', 'Portland'),
    ('2026-01-02', 'Washington', 'Brooklyn'),
    ('2026-01-02', 'Phoenix', 'Sacramento'),
    ('2026-01-03', 'San Antonio', 'Portland'),
]

print("Fixing home/away errors...")
print("=" * 80)

fixed_count = 0

for date_str, current_away, current_home in errors_to_fix:
    date = pd.to_datetime(date_str)
    
    # Find the game
    mask = (df['Date'] == date) & (df['Away'] == current_away) & (df['Home'] == current_home)
    
    if mask.sum() == 0:
        print(f"⚠️  Could not find game: {date_str} {current_away} @ {current_home}")
        continue
    
    if mask.sum() > 1:
        print(f"⚠️  Multiple matches for: {date_str} {current_away} @ {current_home}")
        continue
    
    idx = df[mask].index[0]
    
    # Get current values
    old_away = df.loc[idx, 'Away']
    old_home = df.loc[idx, 'Home']
    old_fav_at_home = df.loc[idx, 'Fav. At Home?']
    favorite = df.loc[idx, 'Favorite']
    underdog = df.loc[idx, 'Underdog']
    
    # Swap Away and Home
    df.loc[idx, 'Away'] = old_home
    df.loc[idx, 'Home'] = old_away
    
    # Update Fav. At Home? flag
    # If Favorite is now Home, set to 1, otherwise 0
    new_fav_at_home = 1 if df.loc[idx, 'Home'] == favorite else 0
    df.loc[idx, 'Fav. At Home?'] = new_fav_at_home
    
    print(f"✅ Fixed: {date_str}")
    print(f"   Before: {old_away} @ {old_home} (Fav. At Home? = {old_fav_at_home})")
    print(f"   After:  {df.loc[idx, 'Away']} @ {df.loc[idx, 'Home']} (Fav. At Home? = {new_fav_at_home})")
    print(f"   Favorite: {favorite}, Underdog: {underdog}")
    print()
    
    fixed_count += 1

print("=" * 80)
print(f"Fixed {fixed_count} games")

# Save the corrected dataset
df.to_csv('data/NBA Training Set 25-26.csv', index=False)
print("\nSaved corrected dataset to data/NBA Training Set 25-26.csv")

# Verify the fixes
print("\nVerifying fixes...")
for date_str, old_away, old_home in errors_to_fix:
    date = pd.to_datetime(date_str)
    # Should now have old_home @ old_away
    mask = (df['Date'] == date) & (df['Away'] == old_home) & (df['Home'] == old_away)
    
    if mask.sum() == 1:
        print(f"✅ {date_str}: {old_home} @ {old_away}")
    else:
        print(f"❌ {date_str}: Fix verification failed")
