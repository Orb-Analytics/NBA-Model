import pandas as pd
from pathlib import Path
import sys
from difflib import SequenceMatcher

# ==============================
# CONFIGURATION
# ==============================
DATA_DIR = Path("data")
YESTERDAY_DIR = DATA_DIR / "yesterdays_scores"
MASTER_FILE = DATA_DIR / "NBA Training Set 25-26.csv"
UNMATCHED_FILE = DATA_DIR / "unmatched_games.csv"

# Allow CLI argument (path to scores file)
if len(sys.argv) > 1:
    SCORES_FILES = [Path(sys.argv[1])]
else:
    # Process all scores files
    SCORES_FILES = sorted(YESTERDAY_DIR.glob("nba_scores_*.csv"), key=lambda p: p.stat().st_mtime)

print(f"📂 Master file: {MASTER_FILE}")
print(f"📂 Scores files: {[str(f) for f in SCORES_FILES]}")

# ==============================
# NAMING MAPS
# ==============================
# Map from score file full names to master dataset abbreviated names
SCORE_TO_MASTER_TEAM_MAP = {
    "Atlanta": "Atlanta", "Boston": "Boston", "Brooklyn": "Brooklyn", "Charlotte": "Charlotte",
    "Chicago": "Chicago", "Cleveland": "Cleveland", "Dallas": "Dallas", "Denver": "Denver",
    "Detroit": "Detroit", "Golden State": "Golden State", "Houston": "Houston", "Indiana": "Indiana",
    "LA Clippers": "LA Clippers", "LA Lakers": "La Lakers", "Los Angeles": "La Lakers",
    "Memphis": "Memphis", "Miami": "Miami", "Milwaukee": "Milwaukee", "Minnesota": "Minnesota",
    "New Orleans": "New Orleans", "New York": "New York", "Oklahoma City": "Okla City",
    "Orlando": "Orlando", "Philadelphia": "Philadelphia", "Phoenix": "Phoenix", "Portland": "Portland",
    "Sacramento": "Sacramento", "San Antonio": "San Antonio", "Toronto": "Toronto",
    "Utah": "Utah", "Washington": "Washington"
}

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

def map_score_team_name(team_name, opponent=None):
    """Map score file team name to master dataset name, handling ambiguous cases."""
    if team_name == "LA":
        # Disambiguate LA based on opponent
        west_teams = {"Golden State", "LA Clippers", "Phoenix", "Sacramento", "Portland", "Utah", "Denver", "Minnesota", "Okla City", "Dallas", "San Antonio", "New Orleans", "Memphis"}
        if opponent in west_teams:
            return "LA Clippers"  # LA playing Western opponent = LA Clippers
        else:
            return "La Lakers"  # LA playing Eastern opponent = LA Lakers
    return SCORE_TO_MASTER_TEAM_MAP.get(team_name, team_name)

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

def fix_all_computed_columns(df):
    """
    Fix all computed columns to ensure they're correctly calculated.
    This runs at the end of merging to catch any errors.
    """
    print("🔧 Verifying and fixing all computed columns...")
    
    fixes = 0
    for idx, row in df.iterrows():
        # Fix Fav. At Home?
        expected_fav_home = 1 if row['Favorite'] == row['Home'] else 0
        if row['Fav. At Home?'] != expected_fav_home:
            df.at[idx, 'Fav. At Home?'] = expected_fav_home
            fixes += 1
        
        # For completed games
        if pd.notna(row['Favorite Score']) and pd.notna(row['Underdog Score']):
            # Fix Winner
            expected_winner = row['Favorite'] if row['Favorite Score'] > row['Underdog Score'] else row['Underdog']
            if row['Winner'] != expected_winner:
                df.at[idx, 'Winner'] = expected_winner
                fixes += 1
            
            # Fix Favorite - Underdog (+/-)
            expected_diff = row['Favorite Score'] - row['Underdog Score']
            if pd.isna(row['Favorite - Underdog (+/-)']) or abs(row['Favorite - Underdog (+/-)'] - expected_diff) > 0.01:
                df.at[idx, 'Favorite - Underdog (+/-)'] = expected_diff
                fixes += 1
            
            # Fix Favorite Cover?
            if pd.notna(row['Spread']):
                expected_cover = 1 if expected_diff > row['Spread'] else 0
                if pd.isna(row['Favorite Cover?']) or row['Favorite Cover?'] != expected_cover:
                    df.at[idx, 'Favorite Cover?'] = expected_cover
                    fixes += 1
            
            # Fix Favorite Win?
            expected_fav_win = 1 if row['Favorite Score'] > row['Underdog Score'] else 0
            if pd.isna(row['Favorite Win?']) or row['Favorite Win?'] != expected_fav_win:
                df.at[idx, 'Favorite Win?'] = expected_fav_win
                fixes += 1
        
        # Fix Home/Away +/-
        if pd.notna(row['Home Score']) and pd.notna(row['Away Score']):
            expected_home_diff = row['Home Score'] - row['Away Score']
            if pd.isna(row['Home/Away +/-']) or abs(row['Home/Away +/-'] - expected_home_diff) > 0.01:
                df.at[idx, 'Home/Away +/-'] = expected_home_diff
                fixes += 1
    
    if fixes > 0:
        print(f"   ✅ Fixed {fixes} computed column values")
    else:
        print(f"   ✅ All computed columns verified correct")
    
    return df

# ==============================
# LOAD DATA
# ==============================
# Moved inside main function to avoid loading at import time

def merge_scores():
    """Main function to merge scores into master dataset."""
    df_master = pd.read_csv(MASTER_FILE)
    print(f"📂 Loaded {len(df_master)} rows from master")

    total_updated = 0
    all_unmatched = []

    for scores_file in SCORES_FILES:
        print(f"📄 Processing {scores_file}")
        df_scores = pd.read_csv(scores_file)

        # Normalize - scores already have full team names, don't map them
        # df_scores["Home"] = df_scores["Home"].map(TEAM_NAME_MAP)
        # df_scores["Away"] = df_scores["Away"].map(TEAM_NAME_MAP)
        df_scores["Date"] = pd.to_datetime(df_scores["Date"]).dt.strftime("%Y-%m-%d")
        df_master["Date"] = pd.to_datetime(df_master["Date"], errors="coerce").dt.strftime("%Y-%m-%d")

        # ==============================
        # MERGE LOGIC
        # ==============================
        updated_rows = 0
        unmatched = []

        for i, row in df_master.iterrows():
            date = row["Date"]
            fav = row["Favorite"]
            dog = row["Underdog"]
            fav_home = int(row["Fav. At Home?"])

            # find matching score - exact match first (map score file names to master names)
            # Create mapped versions for comparison
            df_scores_copy = df_scores.copy()
            df_scores_copy["Home_mapped"] = df_scores_copy.apply(lambda row: map_score_team_name(row["Home"], map_score_team_name(row["Away"], None)), axis=1)
            df_scores_copy["Away_mapped"] = df_scores_copy.apply(lambda row: map_score_team_name(row["Away"], map_score_team_name(row["Home"], None)), axis=1)

            match = df_scores_copy[
                (df_scores_copy["Date"] == date)
                & (
                    ((df_scores_copy["Home_mapped"] == fav) & (df_scores_copy["Away_mapped"] == dog))
                    |
                    ((df_scores_copy["Home_mapped"] == dog) & (df_scores_copy["Away_mapped"] == fav))
                )
            ]

            # If no exact match, try fuzzy matching
            if match.empty:
                # Get all games on this date
                date_games = df_scores_copy[df_scores_copy["Date"] == date]
                if not date_games.empty:
                    # Try fuzzy matching against mapped team names
                    available_teams = set(date_games["Home_mapped"].dropna()) | set(date_games["Away_mapped"].dropna())

                    fav_match, fav_score = fuzzy_match(fav, available_teams)
                    dog_match, dog_score = fuzzy_match(dog, available_teams)

                    if fav_match and dog_match and fav_score >= 0.8 and dog_score >= 0.8:
                        # Check if they play each other using mapped names
                        fuzzy_match_games = date_games[
                            ((date_games["Home_mapped"] == fav_match) & (date_games["Away_mapped"] == dog_match)) |
                            ((date_games["Home_mapped"] == dog_match) & (date_games["Away_mapped"] == fav_match))
                        ]
                        if not fuzzy_match_games.empty:
                            match = fuzzy_match_games
                            print(f"🔍 Fuzzy matched: {fav}/{dog} → {fav_match}/{dog_match} (scores: {fav_score:.2f}/{dog_score:.2f})")

            if match.empty:
                continue

            game = match.iloc[0]
            home_team = game["Home"]
            away_team = game["Away"]
            home_score = game["Home Score"]
            away_score = game["Away Score"]
            winner = game["Winner"]

            # Assign scores
            if fav_home == 1:
                fav_score, dog_score = home_score, away_score
                df_master.at[i, "Home"] = fav
                df_master.at[i, "Away"] = dog
            else:
                fav_score, dog_score = away_score, home_score
                df_master.at[i, "Home"] = dog
                df_master.at[i, "Away"] = fav

            df_master.at[i, "Favorite Score"] = fav_score
            df_master.at[i, "Underdog Score"] = dog_score
            df_master.at[i, "Winner"] = winner

            # Compute metrics
            diff = fav_score - dog_score
            spread = row["Spread"]

            df_master.at[i, "Favorite - Underdog (+/-)"] = diff
            df_master.at[i, "Favorite Cover?"] = 1 if diff > spread else 0
            df_master.at[i, "Favorite Win?"] = 1 if diff > 0 else 0

            # Home/Away Scores
            if fav_home == 1:
                df_master.at[i, "Home Score"] = fav_score
                df_master.at[i, "Away Score"] = dog_score
            else:
                df_master.at[i, "Home Score"] = dog_score
                df_master.at[i, "Away Score"] = fav_score

            df_master.at[i, "Home/Away +/-"] = df_master.at[i, "Home Score"] - df_master.at[i, "Away Score"]

            updated_rows += 1

        total_updated += updated_rows
        all_unmatched.extend(unmatched)
        print(f"  ✅ Updated {updated_rows} games from {scores_file.name}")

    # ==============================
    # FIX ALL COMPUTED COLUMNS
    # ==============================
    df_master = fix_all_computed_columns(df_master)
    
    # ==============================
    # SAVE RESULTS
    # ==============================
    df_master.to_csv(MASTER_FILE, index=False)
    pd.DataFrame(all_unmatched, columns=["Date", "Fav", "Dog"]).to_csv(UNMATCHED_FILE, index=False)

    print(f"💾 Updated file saved → {MASTER_FILE}")
    print(f"📊 Total games updated: {total_updated}")
    print(f"⚠️ Unmatched games exported → {UNMATCHED_FILE}")

if __name__ == "__main__":
    merge_scores()
