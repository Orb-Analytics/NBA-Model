#!/usr/bin/env python3
"""
Merge data from raw NBA Training Set file into the main training set.
Aligns columns 17-230 from raw file with columns 19-232 in main file.
"""

import pandas as pd

# Read both files
raw_file = "/workspaces/NBA-model/data/raw/NBA_Training_Set_2025-11-01.csv"
main_file = "/workspaces/NBA-model/data/NBA Training Set 25-26.csv"

print("Reading raw file...")
raw_df = pd.read_csv(raw_file)
print(f"Raw file has {len(raw_df)} rows and {len(raw_df.columns)} columns")

print("\nReading main training set...")
main_df = pd.read_csv(main_file)
print(f"Main file has {len(main_df)} rows and {len(main_df.columns)} columns")

# Display column counts to verify alignment
print(f"\nRaw file columns 17-230 = {len(raw_df.columns[16:230])} columns")
print(f"Main file columns 19-232 = {len(main_df.columns[18:232])} columns")

# Process each row from the raw file
for idx, raw_row in raw_df.iterrows():
    date = raw_row['Date']
    print(f"\nProcessing row for date: {date}")
    
    # Create a new row for the main dataframe with the same structure
    new_row = pd.Series(index=main_df.columns, dtype=object)
    
    # Copy the first 18 columns from raw to main (columns 0-15 go to 0-15 in main)
    # But main has 2 extra columns (Fav. Odds, Dog Odds) at positions 6 and 7
    # So: raw[0-5] -> main[0-5], then empty for main[6-7], raw[6-15] -> main[8-17]
    for i in range(6):  # Date through Spread
        new_row.iloc[i] = raw_row.iloc[i]
    
    # Columns 6-7 in main (Fav. Odds, Dog Odds) are empty
    new_row.iloc[6] = None
    new_row.iloc[7] = None
    
    # Raw columns 6-15 go to main columns 8-17
    for i in range(6, 16):
        new_row.iloc[i + 2] = raw_row.iloc[i]
    
    # Now align columns 17-230 from raw with columns 19-232 in main
    # Raw column index 16 -> Main column index 18
    raw_start = 16  # Column 17 (0-indexed as 16)
    raw_end = 230   # Column 230 (0-indexed as 229, but slice end is exclusive so use 230)
    main_start = 18 # Column 19 (0-indexed as 18)
    
    # Copy the aligned columns
    for i, raw_col_idx in enumerate(range(raw_start, min(raw_end, len(raw_row)))):
        main_col_idx = main_start + i
        if main_col_idx < len(new_row):
            new_row.iloc[main_col_idx] = raw_row.iloc[raw_col_idx]
    
    # Append the new row to main dataframe
    main_df = pd.concat([main_df, pd.DataFrame([new_row])], ignore_index=True)
    print(f"  Added row for {raw_row['Favorite']} vs {raw_row['Underdog']}")

# Save the updated main file
print(f"\nSaving updated main file with {len(main_df)} total rows...")
main_df.to_csv(main_file, index=False)
print("Done!")
