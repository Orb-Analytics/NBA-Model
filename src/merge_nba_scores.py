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
    SCORES_FILE = Path(sys.argv[1])
else:
    score_files = sorted(YESTERDAY_DIR.glob("nba_scores_*.csv"), key=lambda p: p.stat().st_mtime)
    if not score_files:
        raise FileNotFoundError("❌ No score file found in yesterdays_scores/")
    SCORES_FILE = score_files[-1]

print(f"📂 Master file: {MASTER_FILE}")
print(f"📂 Scores file: {SCORES_FILE}")

# ==============================
# NAMING MAPS
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

# ==============================
# LOAD DATA
# ==============================
df_master = pd.read_csv(MASTER_FILE)
df_scores = pd.read_csv(SCORES_FILE)

# Normalize
df_scores["Home"] = df_scores["Home"].map(TEAM_NAME_MAP)
df_scores["Away"] = df_scores["Away"].map(TEAM_NAME_MAP)
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

    # find matching score - exact match first
    match = df_scores[
        (df_scores["Date"] == date)
        & (
            ((df_scores["Home"] == fav) & (df_scores["Away"] == dog))
            | ((df_scores["Home"] == dog) & (df_scores["Away"] == fav))
        )
    ]

    # If no exact match, try fuzzy matching
    if match.empty:
        # Get all games on this date
        date_games = df_scores[df_scores["Date"] == date]
        if not date_games.empty:
            available_teams = set(date_games["Home"].dropna()) | set(date_games["Away"].dropna())
            fav_match, fav_score = fuzzy_match(fav, available_teams)
            dog_match, dog_score = fuzzy_match(dog, available_teams)
            
            if fav_match and dog_match and fav_score >= 0.85 and dog_score >= 0.85:
                # Check if they play each other
                fuzzy_match_games = date_games[
                    ((date_games["Home"] == fav_match) & (date_games["Away"] == dog_match)) |
                    ((date_games["Home"] == dog_match) & (date_games["Away"] == fav_match))
                ]
                if not fuzzy_match_games.empty:
                    match = fuzzy_match_games
                    print(f"🔍 Fuzzy matched: {fav}/{dog} → {fav_match}/{dog_match} (scores: {fav_score:.2f}/{dog_score:.2f})")

    if match.empty:
        unmatched.append((date, fav, dog))
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

# ==============================
# SAVE RESULTS
# ==============================
df_master.to_csv(MASTER_FILE, index=False)
pd.DataFrame(unmatched, columns=["Date", "Fav", "Dog"]).to_csv(UNMATCHED_FILE, index=False)

print(f"💾 Updated file saved → {MASTER_FILE}")
print(f"📊 Games updated: {updated_rows}")
print(f"⚠️ Unmatched games exported → {UNMATCHED_FILE}")
