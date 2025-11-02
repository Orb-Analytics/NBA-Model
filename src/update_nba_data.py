import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
import pytz
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
    # Use US/Eastern to align with ESPN's notion of game dates (avoid UTC midnight issues)
    eastern = pytz.timezone('US/Eastern')
    now_eastern = datetime.now(eastern)
    target_date_dt = now_eastern - timedelta(days=1)
    target_date = target_date_dt.strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={target_date}"
    print(f"🔎 Target date (Eastern): {target_date_dt.date()} -> {target_date}")

    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"❌ ESPN request failed ({resp.status_code})")
        return None

    data = resp.json()
    events = data.get("events", [])
    # Only process yesterday's games - no fallback to avoid adding old data
    if not events:
        print(f"ℹ️ No games found for {target_date_dt.date()} — this is normal if no games were scheduled")
        return None

    records = []
    for event in events:
        comp = event["competitions"][0]
        status = comp["status"]["type"]["name"]
        # Competitors ordering may vary; find home/away by 'homeAway' field when available
        competitors = comp.get("competitors", [])
        home = None
        away = None
        if len(competitors) >= 2:
            for c in competitors:
                if c.get("homeAway") == "home":
                    home = c
                elif c.get("homeAway") == "away":
                    away = c
        # Fallback to index-based if fields not present
        if home is None or away is None:
            if len(competitors) >= 2:
                home = competitors[0]
                away = competitors[1]

        def _extract_team_name(comp_item):
            if not comp_item:
                return ""
            team = comp_item.get("team", {})
            return team.get("location") or team.get("displayName") or team.get("name") or ""

        home_team = _extract_team_name(home)
        away_team = _extract_team_name(away)

        def _extract_score(comp_item):
            if not comp_item:
                return None
            s = comp_item.get("score")
            try:
                return int(s) if s not in (None, "") else None
            except Exception:
                return None

        home_score = _extract_score(home)
        away_score = _extract_score(away)

        winner = None
        if home and home.get("winner"):
            winner = home_team
        elif away and away.get("winner"):
            winner = away_team

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
    csv_path = YESTERDAYS_DIR / f"nba_scores_{datetime.strptime(target_date, '%Y%m%d').strftime('%Y-%m-%d')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"💾 Saved scores → {csv_path}")

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
