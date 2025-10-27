import requests
import pandas as pd
from datetime import datetime, timedelta, UTC
from pathlib import Path
import time

# --------------------------
# Team name map (ESPN → Your dataset)
# --------------------------
TEAM_MAP = {
    "ATL": "Atlanta",
    "BOS": "Boston",
    "BKN": "Brooklyn",
    "CHA": "Charlotte",
    "CHI": "Chicago",
    "CLE": "Cleveland",
    "DAL": "Dallas",
    "DEN": "Denver",
    "DET": "Detroit",
    "GS": "Golden State", "GSW": "Golden State",
    "HOU": "Houston",
    "IND": "Indiana",
    "LAC": "LA Clippers",
    "LAL": "LA Lakers",
    "MEM": "Memphis",
    "MIA": "Miami",
    "MIL": "Milwaukee",
    "MIN": "Minnesota",
    "NO": "New Orleans", "NOP": "New Orleans",
    "NY": "New York", "NYK": "New York",
    "OKC": "Okla City",
    "ORL": "Orlando",
    "PHI": "Philadelphia",
    "PHX": "Phoenix",
    "POR": "Portland",
    "SAC": "Sacramento",
    "SA": "San Antonio", "SAS": "San Antonio",
    "TOR": "Toronto",
    "UTA": "Utah", "UTAH": "Utah",
    "WSH": "Washington",
}

# --------------------------
# Config
# --------------------------
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

# Compute yesterday’s date (timezone-aware)
yesterday = datetime.now(UTC) - timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")
espn_date = yesterday.strftime("%Y%m%d")

print(f"📅 Fetching NBA games for {date_str}...")

# --------------------------
# Retry logic
# --------------------------
for attempt in range(1, 4):
    try:
        print(f"🔄 Attempt {attempt} of 3...")
        resp = requests.get(f"{ESPN_URL}?dates={espn_date}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        break
    except Exception as e:
        print(f"⚠️ Attempt {attempt} failed: {e}")
        if attempt < 3:
            print("⏳ Waiting 5 seconds before retrying...")
            time.sleep(5)
        else:
            print("❌ Failed to retrieve data after 3 attempts.")
            exit()

# --------------------------
# Parse and map game data
# --------------------------
games = []
for event in data.get("events", []):
    comp = event["competitions"][0]
    home = comp["competitors"][0]
    away = comp["competitors"][1]

    home_team = home["team"]["abbreviation"]
    away_team = away["team"]["abbreviation"]
    home_name = TEAM_MAP.get(home_team, home_team)
    away_name = TEAM_MAP.get(away_team, away_team)

    home_score = int(home.get("score", 0)) if home.get("score") else None
    away_score = int(away.get("score", 0)) if away.get("score") else None
    winner = home_name if home.get("winner") else away_name if away.get("winner") else None
    status = comp["status"]["type"]["name"]

    games.append({
        "Date": date_str,
        "Home": home_name,
        "Away": away_name,
        "Home Score": home_score,
        "Away Score": away_score,
        "Winner": winner,
        "Status": status,
    })

# --------------------------
# Save to CSV
# --------------------------
if games:
    df = pd.DataFrame(games)
    out_path = OUTPUT_DIR / f"nba_scores_{date_str}.csv"
    df.to_csv(out_path, index=False)
    print(df)
    print(f"💾 Saved to {out_path}")
else:
    print("⚠️ No games found for that date.")
