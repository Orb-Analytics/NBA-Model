# 🧠 NBA Data Pipeline — Copilot Framework

## ⚙️ 1. Overview

This repository powers the **NBA Model ETL pipeline**, which automates the creation and maintenance of a master dataset used for predictive modeling.  
The workflow integrates **Google Sheets (raw metrics)**, **Novig odds data**, and **ESPN scores** into a unified dataset stored at:

/data/NBA Training Set 25-26.csv

yaml
Copy code

---

## 🧩 2. Core Data Flow

Each daily update performs the following sequence:

1. **Fetch daily raw sheet** (from Google Apps Script export → `/data/raw/NBA_Training_Set_YYYY-MM-DD.csv`)
2. **Fetch today’s spreads & odds** from Novig (`src/novig_nba_odds.py`)
3. **Fetch yesterday’s ESPN scores** (`src/update_nba_data.py`)
4. **Normalize & merge** into the master training set
5. **Commit and push** updates to GitHub automatically

---

## 📁 3. Folder Structure

/data
├── NBA Training Set 25-26.csv # Master dataset
├── raw/ # Daily Google Sheet exports
├── novig-odds/ # Daily Novig API CSVs
├── yesterdays_scores/ # Daily ESPN score files
├── unmatched_games.csv # Diagnostics for failed merges
/src
├── novig_nba_odds.py # Fetches Novig spreads
├── update_nba_data.py # Fetches ESPN scores + merges results
├── merge_nba_scores.py # Aligns scores to training set
├── daily_update.py # (new) master orchestrator script

yaml
Copy code

---

## 🧮 4. Column Alignment

### 🏀 Master Dataset — `/data/NBA Training Set 25-26.csv`
Key initial columns:
Date, Favorite, Favorite Score, Underdog, Underdog Score, Spread,
Fav. At Home?, Winner, Favorite - Underdog (+/-),
Favorite Cover?, Favorite Win?, Away, Away Score, Home, Home Score, Home/Away +/-

kotlin
Copy code
Followed by team statistics (PPG, efficiency, rebounds, etc.).

### 📊 Scores File — `/data/yesterdays_scores/nba_scores_YYYY-MM-DD.csv`
Date, Home, Away, Home Score, Away Score, Winner, Status

shell
Copy code

### 💵 Odds File — `/data/novig-odds/novig_nba_spreads_YYYY-MM-DD.csv`
fav_team, dog_team, fav_line, dog_line,
fav_price, dog_price, fav_price_american, dog_price_american,
home_favorite, game_time_est, market, market_timestamp

swift
Copy code

---

## 🔁 5. Merge Rules

### Step 1 — Normalize
- All dates → `YYYY-MM-DD`
- Trim whitespace
- Ensure numeric columns are `float` or `int`
- Ensure `Fav. At Home?` is `0` or `1`

### Step 2 — Integrate ESPN Scores
- Match by `Date`, `Favorite`, `Underdog` (or Home/Away via mapping)
- Fill:
  - `Favorite Score`, `Underdog Score`
  - `Winner`
  - `Favorite - Underdog (+/-)` = `Favorite Score - Underdog Score`
  - `Favorite Win?` = `1 if Favorite Score > Underdog Score else 0`
  - `Favorite Cover?` = `1 if Favorite - Underdog (+/-) > Spread else 0`
  - `Home/Away +/-` = `Home Score - Away Score`

### Step 3 — Integrate Novig Odds
- Replace existing `Spread` with `fav_line`
- Insert **two new columns** right after `Spread`:
  - `Fav. Odds` ← `fav_price_american`
  - `Dog Odds` ← `dog_price_american`
- If no odds found → default both to `-110`
- Update `Fav. At Home?` from Novig’s `home_favorite`

---

## 🧱 6. Team Mapping Reference

```python
TEAM_NAME_MAP = {
  "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
  "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
  "Detroit": "DET", "Golden State": "GS", "Houston": "HOU", "Indiana": "IND",
  "LA Clippers": "LAC", "LA Lakers": "LAL", "Memphis": "MEM", "Miami": "MIA",
  "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NO", "New York": "NY",
  "Okla City": "OKC", "Orlando": "ORL", "Philadelphia": "PHI", "Phoenix": "PHX",
  "Portland": "POR", "Sacramento": "SAC", "San Antonio": "SA", "Toronto": "TOR",
  "Utah": "UTAH", "Washington": "WSH"
}
Use this map to normalize team names across ESPN, Novig, and the Google Sheet.

🧾 7. Output Expectations
After merging:

/data/NBA Training Set 25-26.csv is the updated master

/data/unmatched_games.csv logs unmatched rows

Dates are normalized to ISO format

Odds columns are populated or defaulted

New daily commit message is formatted as:

scss
Copy code
🏀 NBA Auto-Update: YYYY-MM-DD
✅ 8. Copilot To-Do Checklist
🗂 Data Normalization
 Normalize all Date fields to YYYY-MM-DD

 Clean whitespace, ensure consistent casing for teams

 Convert numeric columns to proper types

 Validate Fav. At Home? = {0, 1}

🔗 Merging & Mapping
 Match games using TEAM_NAME_MAP

 Add fuzzy matching (Levenshtein ≥ 85%)

 Export data/unmatched_games.csv for review

 Recalculate spreads and cover/win metrics after merges

💵 Odds Integration
 Replace Spread with fav_line

 Add columns Fav. Odds and Dog Odds

 Default to -110 if missing

 Update Fav. At Home? from Novig data

📊 Dataset Automation
 Build unified script (src/daily_update.py)

 Sequence: Novig fetch → ESPN fetch → Merge → Push

 Commit daily updates automatically via GitHub Action

🧹 Repository Maintenance
 Remove deprecated ETL scripts

 Add .gitignore for temp CSVs and caches

 Create version tags (v1.0.0, v1.1.0, etc.)

🧠 Validation
 Test that all merges increase row count

 No nulls in Date, Favorite, Underdog, Spread

 Validate odds range (−10000 to +10000)

 Add pytest for merge logic and odds population

🧰 9. src/daily_update.py — Skeleton
python
Copy code
"""
Daily NBA Data Update Pipeline
Author: Orb Analytics (Liam Chaitin)
Purpose: Orchestrate full daily ETL (Novig odds, ESPN scores, raw sheet merge)
"""

import subprocess
import sys
from datetime import datetime

def run_script(script_path):
    print(f"🚀 Running {script_path} ...")
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"✅ Completed: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_path}: {e}")
        sys.exit(1)

def main():
    print("\n🏀 Starting Daily NBA Data Pipeline...\n")
    today = datetime.now().strftime("%Y-%m-%d")

    # 1️⃣ Fetch today's Novig odds
    run_script("src/novig_nba_odds.py")

    # 2️⃣ Fetch yesterday’s ESPN scores
    run_script("src/update_nba_data.py")

    # 3️⃣ Merge raw sheet (latest file in /data/raw)
    run_script("src/merge_nba_scores.py")

    print(f"\n🎯 Daily NBA Data Pipeline Complete — {today}\n")

    # 4️⃣ Commit + Push
    try:
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"🏀 NBA Auto-Update: {today}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Successfully pushed updates to GitHub.")
    except Exception as e:
        print(f"⚠️ Git push failed: {e}")

if __name__ == "__main__":
    main()
🧩 10. Notes for Copilot
When editing or generating code in this repository, always:

Keep file paths consistent (/data/... and /src/...)

Preserve ISO date formatting

Maintain logs and emoji indicators (✅, ⚠️, ❌)

Never overwrite NBA Training Set 25-26.csv destructively — always update in place

Always produce human-readable console output for debugging

