# 🏀 NBA Data Pipeline — Repo Overview and Cleanup Framework

## 🎯 Purpose
This repository automates the **daily ingestion and enrichment of NBA data** for model training and betting analysis.  
Each day, the pipeline collects raw team and odds data, merges it with prior-day scores, and updates the master dataset:
`data/NBA Training Set 25-26.csv`.

---

## 🧩 Data Flow Overview

### 🧾 Step 1: Google Sheets → GitHub (Automated via Apps Script)
- The Google Apps Script (`GoogleSheetsCopyAndExport.gs`) runs daily and:
  1. Copies the master Google Sheet `NBA Statistics Export - Model Export YYYY-MM-DD`
  2. Extracts only the `"Training Set"` sheet
  3. Uploads it to GitHub as a CSV file:
     ```
     data/raw/NBA_Training_Set_YYYY-MM-DD.csv
     ```
- This file is the **raw input** for the daily pipeline.

> ❌ The old extractor `google_sheet_extract.py` is **no longer used** — remove it.

---

### 🧮 Step 2: Novig API — Daily Odds Extraction
- The `novig_nba_odds.py` script fetches **daily betting odds** from the Novig API:
  - Favorite & underdog teams
  - Spread values
  - Odds (moneyline, spread)
- Output: data/novig-odds/novig_nba_spreads_YYYY-MM-DD.csv
- These odds will later **replace** the spreads from the Sheets data and populate missing columns like:
- `Fav Odds`
- `Dog Odds`

> ⚠️ Keep this file but prepare to refactor it for better naming + API consistency.

---

### 🏁 Step 3: ESPN API — Prior Day Final Scores
- The `nba_scores_yesterday.py` script fetches final scores for yesterday’s NBA games: data/yesterdays_scores/nba_scores_YYYY-MM-DD.csv
- These are merged with the master dataset via `merge_nba_scores.py`.

> The individual score CSVs in `data/` are redundant (e.g., `nba_scores_2025-10-26.csv` to `nba_scores_2025-10-30.csv`).  
> ✅ Move them to `/data/yesterdays_scores/` or delete — the subfolder version is what’s used.

---

### 🔄 Step 4: Data Merge + Transformation
- The `merge_nba_scores.py` script merges:
- The latest Google Sheets CSV (training data)
- Novig odds
- ESPN scores

- It then computes or updates:
- `Favorite - Underdog (+/-)` = `Fav Score - Dog Score`
- `Favorite Cover?` = `1 if (FavDiff > Spread) else 0`
- `Favorite Win?` = `1 if Fav Score > Dog Score else 0`
- `Home/Away +/-` = `Home Score - Away Score`
- Replaces `Spread` with Novig’s updated spread
- Adds `Fav Odds` and `Dog Odds` columns from Novig

- The processed file becomes: data/processed/NBA_Training_Set_Processed_YYYY-MM-DD.csv
and optionally updates the master: data/NBA Training Set 25-26.csv

---

## 🧹 CLEANUP PLAN

### ❌ Files to Remove
These are outdated or replaced:

google_sheet_extract.py
src/etl/google_sheet_extract.py
src/etl/novig_nba_odds.py
src/etl/update_nba_data.py
data/nba_scores_2025-10-26.csv
data/nba_scores_2025-10-27.csv
data/nba_scores_2025-10-28.csv
data/nba_scores_2025-10-29.csv
data/nba_scores_2025-10-30.csv


---

## 🗂️ New Folder Structure (Target Tree)
The repo should evolve into this structure:

NBA-model/
│
├── data/
│ ├── raw/ # Daily exports from Google Sheets
│ ├── novig-odds/ # Daily odds data from Novig API
│ ├── yesterdays_scores/ # Final scores from ESPN
│ ├── processed/ # Merged and cleaned datasets
│ └── NBA Training Set 25-26.csv # Ongoing master file
│
├── src/
│ ├── novig_nba_odds.py
│ ├── nba_scores_yesterday.py
│ ├── merge_nba_scores.py
│ ├── update_nba_data.py # (Will orchestrate all merges + pushes)
│ ├── utils/
│ │ ├── team_name_map.py
│ │ ├── merge_helpers.py
│ │ └── data_cleaning.py
│
├── .github/
│ └── workflows/
│ ├── daily-update.yml # Automates Novig → Scores → Merge daily
│ └── sheet-upload.yml # (Optional) handles Google upload verification
│
└── README.md or COPILOT_FRAMEWORK.md


---

## ⚙️ Next Automation Steps

### Phase 1 — Cleanup & Refactor
- Delete unused Python scripts listed above.
- Move historical raw/score data into proper subfolders.
- Update imports and paths in scripts to reflect new structure.

### Phase 2 — Merge Automation
- Modify `update_nba_data.py` to:
  1. Detect new `NBA_Training_Set_YYYY-MM-DD.csv` in `/data/raw`
  2. Load yesterday’s scores + Novig odds
  3. Merge and update master dataset
  4. Commit back to GitHub with message:
     ```
     🏀 Daily Update: Merged data for YYYY-MM-DD
     ```

### Phase 3 — Continuous Integration
- Set GitHub Action trigger to run when:
  - A new file is added to `/data/raw/`
  - Or daily at 11:59PM PST

### Phase 4 — Enhancements
- Normalize team names across APIs using `team_name_map.py`
- Ensure consistent `YYYY-MM-DD` date formatting
- Handle missing data gracefully (log unmatched games)
- (Optional) push merged dataset to an analytics tool (Tableau / Streamlit)

---

## 🧠 Instructions for Copilot
When editing or refactoring:
- Always use the **new folder structure**.
- Assume Google Sheets data already uploads automatically to GitHub (no Sheets extraction needed).
- Focus automation on **combining Novig odds + ESPN scores** into the training set.
- Maintain daily snapshots of all source data.
- Never overwrite raw data; always write merged outputs to `/data/processed/` and append to `NBA Training Set 25-26.csv`.

---

## ✅ Example Daily Run Summary

| Step | Script | Input | Output |
|------|--------|--------|--------|
| 1 | GoogleSheetsCopyAndExport.gs | Google Sheet | data/raw/NBA_Training_Set_2025-10-31.csv |
| 2 | novig_nba_odds.py | Novig API | data/novig-odds/novig_nba_spreads_2025-10-31.csv |
| 3 | nba_scores_yesterday.py | ESPN API | data/yesterdays_scores/nba_scores_2025-10-30.csv |
| 4 | merge_nba_scores.py | All above | data/processed/NBA_Training_Set_Processed_2025-10-31.csv |
| 5 | update_nba_data.py | All above | data/NBA Training Set 25-26.csv (updated master) |

---

## 🚀 Summary
- Google Sheets → GitHub is **handled by Apps Script**
- Python scripts handle **odds**, **scores**, and **merging**
- GitHub Actions will eventually handle **automation + commits**
- Clean, modular repo = faster debugging, better reproducibility
