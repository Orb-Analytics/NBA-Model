import pandas as pd
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

# ==============================
# CONFIGURATION
# ==============================
DATA_DIR = Path("data")
NOVIG_DIR = DATA_DIR / "novig-odds"
MASTER_FILE = DATA_DIR / "NBA Training Set 25-26.csv"

# ==============================
# TEAM NAME MAPPING (for consistency)
# ==============================
TEAM_NAME_MAP = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GS", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "LA Lakers": "LAL", "Memphis": "MEM", "Miami": "MIA",
    "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NO", "New York": "NY",
    "Okla City": "OKC", "Orlando": "ORL", "Philadelphia": "PHI", "Phoenix": "PHX",
    "Portland": "POR", "Sacramento": "SAC", "San Antonio": "SA",
    "Toronto": "TOR", "Utah": "UTAH", "Washington": "WSH"
}

# Reverse map for odds files
REVERSE_TEAM_MAP = {v: k for k, v in TEAM_NAME_MAP.items()}
# Handle variations in odds data
REVERSE_TEAM_MAP.update({
    "SAS": "San Antonio",  # odds use SAS instead of SA
    "GSW": "Golden State", # odds use GSW instead of GS  
    "WAS": "Washington",   # odds use WAS instead of WSH
    "BKN": "Brooklyn",     # odds use BKN instead of Brooklyn
    "NY": "New York",      # odds use NY instead of New York
    "NO": "New Orleans",   # odds use NO instead of New Orleans
    "UTAH": "Utah",        # odds use UTAH instead of Utah
})

def fuzzy_match(team, candidates, threshold=0.85):
    """Find best fuzzy match for team name."""
    best_match = None
    best_score = 0
    for candidate in candidates:
        score = SequenceMatcher(None, team, candidate).ratio()
        if score > best_score and score >= threshold:
            best_match = candidate
            best_score = score
    return best_match, best_score

def merge_novig_odds():
    """Merge Novig odds into the master training set."""
    # Load master data
    df_master = pd.read_csv(MASTER_FILE)
    print(f"📂 Loaded {len(df_master)} rows from {MASTER_FILE}")

    # Add odds columns if they don't exist
    if 'Fav. Odds' not in df_master.columns:
        # Insert after Spread
        spread_idx = df_master.columns.get_loc('Spread')
        df_master.insert(spread_idx + 1, 'Fav. Odds', -110)
        df_master.insert(spread_idx + 2, 'Dog Odds', -110)
        print("✅ Added Fav. Odds and Dog Odds columns")

    # Get all odds files
    odds_files = sorted(NOVIG_DIR.glob("novig_nba_spreads_*.csv"))
    print(f"📂 Found {len(odds_files)} odds files")

    updated_odds = 0

    # Process each odds file
    for odds_file in odds_files:
        print(f"📄 Processing {odds_file.name}")
        try:
            df_odds = pd.read_csv(odds_file)
            if df_odds.empty:
                print(f"  ⚠️ Skipping empty file {odds_file.name}")
                continue
        except pd.errors.EmptyDataError:
            print(f"  ⚠️ Skipping empty file {odds_file.name}")
            continue

        # Normalize odds data
        df_odds['game_date'] = pd.to_datetime(df_odds['game_time_est']).dt.date.astype(str)
        
        # Convert odds team abbreviations to full names
        df_odds['fav_team_full'] = df_odds['fav_team'].map(REVERSE_TEAM_MAP).fillna(df_odds['fav_team'])
        df_odds['dog_team_full'] = df_odds['dog_team'].map(REVERSE_TEAM_MAP).fillna(df_odds['dog_team'])

        # Process each game in odds file
        for i, row in df_master.iterrows():
            date = row["Date"]
            fav = row["Favorite"]
            dog = row["Underdog"]

            # Find matching odds
            match = df_odds[
                (df_odds["game_date"] == date)
                & (
                    ((df_odds["fav_team_full"] == fav) & (df_odds["dog_team_full"] == dog))
                    | ((df_odds["fav_team_full"] == dog) & (df_odds["dog_team_full"] == fav))
                )
            ]

            # Try fuzzy matching if exact match fails
            if match.empty:
                date_odds = df_odds[df_odds["game_date"] == date]
                if not date_odds.empty:
                    available_teams = set(date_odds["fav_team_full"].dropna()) | set(date_odds["dog_team_full"].dropna())
                    fav_match, fav_score = fuzzy_match(fav, available_teams)
                    dog_match, dog_score = fuzzy_match(dog, available_teams)
                    
                    if fav_match and dog_match and fav_score >= 0.85 and dog_score >= 0.85:
                        fuzzy_match_odds = date_odds[
                            ((date_odds["fav_team_full"] == fav_match) & (date_odds["dog_team_full"] == dog_match)) |
                            ((date_odds["fav_team_full"] == dog_match) & (date_odds["dog_team_full"] == fav_match))
                        ]
                        if not fuzzy_match_odds.empty:
                            match = fuzzy_match_odds
                            print(f"🔍 Fuzzy matched odds: {fav}/{dog} → {fav_match}/{dog_match}")

            if match.empty:
                continue

            odds_row = match.iloc[0]
            fav_team_odds = odds_row["fav_team"]
            dog_team_odds = odds_row["dog_team"]
            fav_line = odds_row["fav_line"]
            fav_odds = odds_row["fav_price_american"]
            dog_odds = odds_row["dog_price_american"]
            home_fav = odds_row["home_favorite"]

            # Update spread (fav_line)
            df_master.at[i, "Spread"] = fav_line

            # Update odds
            df_master.at[i, "Fav. Odds"] = fav_odds
            df_master.at[i, "Dog Odds"] = dog_odds

            # Update Fav. At Home? from Novig
            df_master.at[i, "Fav. At Home?"] = int(home_fav)

            updated_odds += 1

    # Save updated master
    df_master.to_csv(MASTER_FILE, index=False)
    print(f"💾 Updated master with odds → {MASTER_FILE}")
    print(f"📊 Games updated with odds: {updated_odds}")

if __name__ == "__main__":
    merge_novig_odds()