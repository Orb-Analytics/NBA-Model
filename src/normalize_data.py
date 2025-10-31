import pandas as pd
from pathlib import Path

def normalize_data():
    """Normalize the master NBA training set data."""
    master_file = Path("data/NBA Training Set 25-26.csv")

    # Load data
    df = pd.read_csv(master_file)
    print(f"📂 Loaded {len(df)} rows from {master_file}")

    # 1. Normalize Date fields to YYYY-MM-DD
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    print("✅ Normalized Date fields")

    # 2. Clean whitespace and ensure consistent casing for teams
    team_cols = ['Favorite', 'Underdog', 'Away', 'Home']
    for col in team_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    print("✅ Cleaned team name whitespace")

    # 3. Convert numeric columns to proper types
    # Score columns
    score_cols = ['Favorite Score', 'Underdog Score', 'Away Score', 'Home Score']
    for col in score_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Spread and calculated columns
    calc_cols = ['Spread', 'Favorite - Underdog (+/-)', 'Favorite Cover?', 'Favorite Win?', 'Home/Away +/-']
    for col in calc_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fav. At Home?
    if 'Fav. At Home?' in df.columns:
        df['Fav. At Home?'] = df['Fav. At Home?'].astype(int)

    # Stat columns (all columns from 'Favorite PPG' onwards)
    stat_start_idx = df.columns.get_loc('Favorite PPG')
    stat_cols = df.columns[stat_start_idx:]
    for col in stat_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    print(f"✅ Converted {len(stat_cols)} stat columns to numeric")

    # 4. Validate Fav. At Home? = {0, 1}
    if 'Fav. At Home?' in df.columns:
        invalid_home = df[~df['Fav. At Home?'].isin([0, 1])]
        if not invalid_home.empty:
            print(f"⚠️ Found {len(invalid_home)} rows with invalid Fav. At Home? values")
            # Fix invalid values (assume 0 if not 1)
            df['Fav. At Home?'] = df['Fav. At Home?'].apply(lambda x: 1 if x == 1 else 0)
        else:
            print("✅ Fav. At Home? values are valid (0 or 1)")

    # Check for nulls in critical columns
    critical_cols = ['Date', 'Favorite', 'Underdog', 'Spread']
    null_counts = df[critical_cols].isnull().sum()
    if null_counts.sum() > 0:
        print(f"⚠️ Null values found: {null_counts.to_dict()}")
    else:
        print("✅ No nulls in critical columns")

    # Save normalized data
    df.to_csv(master_file, index=False)
    print(f"💾 Saved normalized data to {master_file}")

if __name__ == "__main__":
    normalize_data()