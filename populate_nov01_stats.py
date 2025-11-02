#!/usr/bin/env python3
"""
Populate statistical columns for Nov 01 2025 games in the main training set
from the raw data file. Maps columns 17-230 from raw to columns 19-232 in main.
"""

import pandas as pd

# Read both files
raw_file = "/workspaces/NBA-model/data/raw/NBA_Training_Set_2025-11-01.csv"
main_file = "/workspaces/NBA-model/data/NBA Training Set 25-26.csv"

print("Reading files...")
raw_df = pd.read_csv(raw_file)
main_df = pd.read_csv(main_file)

print(f"Raw file: {len(raw_df)} rows, {len(raw_df.columns)} columns")
print(f"Main file: {len(main_df)} rows, {len(main_df.columns)} columns")

# Filter main dataframe to Nov 01 rows (lines 1072-1077, which are rows 1071-1076 in 0-indexed)
nov01_rows = main_df[(main_df['Date'] == '2025-11-01')].copy()
print(f"\nFound {len(nov01_rows)} Nov 01 2025 rows in main file")

# Create a mapping based on team matchups
for idx, main_row in nov01_rows.iterrows():
    favorite = main_row['Favorite']
    underdog = main_row['Underdog']
    
    # Find matching row in raw data
    raw_match = raw_df[(raw_df['Favorite'] == favorite) & (raw_df['Underdog'] == underdog)]
    
    if len(raw_match) == 0:
        print(f"WARNING: No match found for {favorite} vs {underdog}")
        continue
    
    raw_row = raw_match.iloc[0]
    print(f"\nMatching: {favorite} vs {underdog}")
    
    # Map columns 17-230 from raw (indices 16-229) to columns 19-232 in main (indices 18-231)
    # Column 17 in raw = index 16, Column 19 in main = index 18
    raw_start_idx = 16
    raw_end_idx = 230
    main_start_idx = 18
    
    # Copy the statistical columns
    for i in range(raw_start_idx, min(raw_end_idx, len(raw_row))):
        main_col_idx = main_start_idx + (i - raw_start_idx)
        if main_col_idx < len(main_df.columns):
            main_df.loc[idx, main_df.columns[main_col_idx]] = raw_row.iloc[i]
    
    print(f"  Populated {min(raw_end_idx - raw_start_idx, len(raw_row) - raw_start_idx)} columns")

# Save updated file
print(f"\nSaving updated file...")
main_df.to_csv(main_file, index=False)
print("Done!")
