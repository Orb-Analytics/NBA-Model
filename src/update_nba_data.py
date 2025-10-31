"""
🏀 update_nba_data.py
Automates the daily NBA data workflow:
  1️⃣ Fetches latest Novig spreads
  2️⃣ Fetches yesterday's scores from ESPN
  3️⃣ Merges scores into master dataset
  4️⃣ Commits and pushes updates to GitHub
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import requests

# === CONFIG ===
DATA_DIR = Path("data")
NOVIG_DIR = DATA_DIR / "novig-odds"
YESTERDAYS_DIR = DATA_DIR / "yesterdays_scores"
MASTER_FILE = DATA_DIR / "NBA Training Set 25-26.csv"

for d in [DATA_DIR, NOVIG_DIR, YESTERDAYS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# === STEP 1: Run Novig Odds Script ===
def fetch_novig_odds():
    print("🎯 Fetching today's Novig NBA spreads...")
    try:
        result = subprocess.run(
            ["python", "src/novig_nba_odds.py"],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
        print("✅ Novig odds successfully fetched and saved.")
    except subprocess.CalledProcessError as e:
        print("❌ Novig odds script failed:")
        print(e.stderr)


# === STEP 2: Fetch Yesterday’s Scores from ESPN ===
def fetch_yesterdays_scores():
    print("🏀 Fetching yesterday’s NBA scores...")
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={target_date}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ ESPN request failed: {e}")
        return None

    data = resp.json()
    events = data.get("events", [])
    if not events:
        print("❌ No games found for that date.")
        return None

    records = []
    for event in events:
        comp = event["competitions"][0]
        status = comp["status"]["type"]["name"]
        home = comp["competitors"][0]
        away = comp["competitors"][1]
        home_team = home["team"]["location"]
        away_team = away["team"]["location"]
        home_score = int(home["score"]) if home.get("score") else None
        away_score = int(away["score"]) if away.get("score") else None
        winner = home_team if home.get("winner") else away_team

        records.append({
            "Date": datetime.strptime(target_date, "%Y%m%d").strftime("%Y-%m-%d"),
            "Home": home_team,
            "Away": away_team,
            "Home Score": home_score,
            "Away Score": away_score,
            "Winner": winner,
            "Status": status
        })

    date_str = datetime.strptime(target_date, "%Y%m%d").strftime("%Y-%m-%d")
    csv_path = DATA_DIR / f"nba_scores_{date_str}.csv"
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    print(f"💾 Saved scores → {csv_path}")

    shutil.copy(csv_path, YESTERDAYS_DIR / csv_path.name)
    print(f"📂 Copied to yesterdays_scores/")
    print(df)

    return csv_path

TEAM_NAME_MAP = {
    "Atlanta": "Atlanta",
    "Boston": "Boston",
    "Brooklyn": "Brooklyn",
    "Charlotte": "Charlotte",
    "Chicago": "Chicago",
    "Cleveland": "Cleveland",
    "Dallas": "Dallas",
    "Denver": "Denver",
    "Detroit": "Detroit",
    "Golden State": "Golden State",
    "Houston": "Houston",
    "Indiana": "Indiana",
    "LA Clippers": "LA Clippers",
    "LA Lakers": "LA Lakers",
    "Memphis": "Memphis",
    "Miami": "Miami",
    "Milwaukee": "Milwaukee",
    "Minnesota": "Minnesota",
    "New Orleans": "New Orleans",
    "New York": "New York",
    "Oklahoma City": "Okla City",
    "Orlando": "Orlando",
    "Philadelphia": "Philadelphia",
    "Phoenix": "Phoenix",
    "Portland": "Portland",
    "Sacramento": "Sacramento",
    "San Antonio": "San Antonio",
    "Toronto": "Toronto",
    "Utah": "Utah",
    "Washington": "Washington"
}

# === STEP 3: Merge Scores into Master Dataset ===
def merge_into_master(scores_path):
    master["Home"] = master["Home"].replace(TEAM_NAME_MAP)
    master["Away"] = master["Away"].replace(TEAM_NAME_MAP)
    scores["Home"] = scores["Home"].replace(TEAM_NAME_MAP)
    scores["Away"] = scores["Away"].replace(TEAM_NAME_MAP)

    print("🔄 Merging scores into master dataset...")
    if not MASTER_FILE.exists():
        print(f"⚠️ Master file not found at {MASTER_FILE}")
        return

    master = pd.read_csv(MASTER_FILE)
    scores = pd.read_csv(scores_path)

    updated = 0
    unmatched = []

    for _, row in scores.iterrows():
        date, home, away = row["Date"], row["Home"], row["Away"]
        h_score, a_score, winner = row["Home Score"], row["Away Score"], row["Winner"]

        mask = (
            (master["Date"].astype(str) == date)
            & (
                ((master["Home"] == home) & (master["Away"] == away)) |
                ((master["Home"] == away) & (master["Away"] == home))
            )
        )

        if mask.any():
            master.loc[mask, "Home Score"] = h_score
            master.loc[mask, "Away Score"] = a_score
            master.loc[mask, "Winner"] = winner
            updated += mask.sum()
        else:
            unmatched.append(row)

    master.to_csv(MASTER_FILE, index=False)
    print(f"💾 Updated master → {MASTER_FILE}")
    print(f"📊 Games updated: {updated}")

    if unmatched:
        unmatched_path = DATA_DIR / "unmatched_games.csv"
        pd.DataFrame(unmatched).to_csv(unmatched_path, index=False)
        print(f"⚠️ Unmatched games exported → {unmatched_path}")


# === STEP 4: Commit and Push to GitHub ===
def push_to_github():
    print("📤 Pushing updates to GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        msg = f"🏀 NBA Auto-Update: {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git push failed: {e}")


# === MAIN PIPELINE ===
if __name__ == "__main__":
    print("🚀 Starting daily NBA data update...")
    fetch_novig_odds()
    scores_path = fetch_yesterdays_scores()

    if scores_path:
        merge_into_master(scores_path)
    else:
        print("⚠️ Skipping merge — no scores fetched.")

    push_to_github()
    print("✅ Daily NBA data update complete.")
