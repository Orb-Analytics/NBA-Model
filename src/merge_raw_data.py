import pandas as pd
from pathlib import Path
from datetime import datetime

def merge_raw_training_sets():
    """Merge raw training set files into the master dataset."""
    master_file = Path("data/NBA Training Set 25-26.csv")
    raw_dir = Path("data/raw")

    # Load master
    df_master = pd.read_csv(master_file)
    print(f"📂 Loaded {len(df_master)} rows from master")

    # Get all raw files
    raw_files = sorted(raw_dir.glob("NBA_Training_Set_*.csv"))
    print(f"📂 Found {len(raw_files)} raw files")

    new_rows = 0

    for raw_file in raw_files:
        print(f"📄 Processing {raw_file.name}")

        # Load raw file
        df_raw = pd.read_csv(raw_file)

        # Normalize dates from DD-MMM to YYYY-MM-DD
        def normalize_date(date_str):
            if pd.isna(date_str):
                return None
            try:
                # Parse DD-MMM format
                parsed = datetime.strptime(str(date_str), "%d-%b")
                # Assume current year 2025
                normalized = parsed.replace(year=2025).strftime("%Y-%m-%d")
                return normalized
            except:
                return date_str

        df_raw['Date'] = df_raw['Date'].apply(normalize_date)

        # Add odds columns if they don't exist
        if 'Fav. Odds' not in df_raw.columns:
            df_raw['Fav. Odds'] = -110
        if 'Dog Odds' not in df_raw.columns:
            df_raw['Dog Odds'] = -110

        # Ensure all columns match master
        for col in df_master.columns:
            if col not in df_raw.columns:
                df_raw[col] = None

        # Only keep columns that exist in master
        df_raw = df_raw[df_master.columns]

        # Remove duplicates based on Date, Favorite, Underdog
        existing_games = set()
        for _, row in df_master.iterrows():
            key = (row['Date'], row['Favorite'], row['Underdog'])
            existing_games.add(key)

        new_games = []
        for _, row in df_raw.iterrows():
            key = (row['Date'], row['Favorite'], row['Underdog'])
            if key not in existing_games:
                new_games.append(row)

        if new_games:
            df_new = pd.DataFrame(new_games)
            df_master = pd.concat([df_master, df_new], ignore_index=True)
            new_rows += len(new_games)
            print(f"  ✅ Added {len(new_games)} new games")

    # Save updated master
    df_master.to_csv(master_file, index=False)
    print(f"💾 Saved updated master with {len(df_master)} total rows (+{new_rows} new)")

if __name__ == "__main__":
    merge_raw_training_sets()