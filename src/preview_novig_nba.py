import pandas as pd
from pathlib import Path

# Directory containing Novig odds CSVs
odds_dir = Path("data/novig-odds")

# Find the most recent file
csv_files = sorted(odds_dir.glob("novig_nba_spreads_*.csv"), reverse=True)

if not csv_files:
    print("⚠️ No Novig NBA CSV files found in data/novig-odds/")
else:
    latest_file = csv_files[0]
    print(f"📂 Loading latest Novig NBA odds file:\n{latest_file}\n")

    # Load full dataset
    df = pd.read_csv(latest_file)

    print(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns\n")

    # Print entire DataFrame (no truncation)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.colheader_justify", "left")
    pd.set_option("display.max_colwidth", None)

    print("📊 Full DataFrame:\n")
    print(df.to_string(index=False))

    print("\n🧾 Columns:", ", ".join(df.columns))
