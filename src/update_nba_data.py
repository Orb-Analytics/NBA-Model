import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import requests

# === CONFIG ===
DATA_DIR = Path("data")
YESTERDAYS_DIR = DATA_DIR / "yesterdays_scores"
MASTER_FILE = DATA_DIR / "NBA Training Set 25-26.csv"

DATA_DIR.mkdir(exist_ok=True)
YESTERDAYS_DIR.mkdir(exist_ok=True)


def fetch_yesterdays_scores():
    """Fetch NBA scores from ESPN public API."""
    print("🏀 Fetching yesterday’s NBA scores...")
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={target_date}"

    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"❌ ESPN request failed ({resp.status_code})")
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

    df = pd.DataFrame(records)
    csv_path = DATA_DIR / f"nba_scores_{datetime.strptime(target_date, '%Y%m%d').strftime('%Y-%m-%d')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"💾 Saved scores → {csv_path}")

    # Copy to yesterdays_scores
    shutil.copy(csv_path, YESTERDAYS_DIR / csv_path.name)
    print(f"📂 Copied to yesterdays_scores/")

    print(df)
    return csv_path


def merge_into_master(scores_path):
    """Merge yesterday's scores into the master training set."""
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
        pd.DataFrame(unmatched).to_csv(DATA_DIR / "unmatched_games.csv", index=False)
        print("⚠️ Unmatched games exported → data/unmatched_games.csv")


def push_to_github():
    """Commit and push changes to GitHub."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        msg = f"🏀 NBA update {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Successfully pushed to GitHub.")
    except Exception as e:
        print(f"⚠️ Git push failed: {e}")


if __name__ == "__main__":
    scores_path = fetch_yesterdays_scores()
    if scores_path:
        merge_into_master(scores_path)
        push_to_github()
