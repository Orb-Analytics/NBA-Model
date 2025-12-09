# New Prediction Framework - Implementation Guide

## Overview

This framework implements a complete NBA prediction system that:
- Shows predictions from all 4 models (Logistic, Linear, Random Forest, Decision Tree)
- Displays each model's pick with edge calculations
- Tracks W-L-P records dynamically from actual results
- Formats emails with one line per model per game
- Supports backfilling missing historical data

## New File Structure

```
src/
├── prediction_core.py          # Core data structures and edge calculations
├── email_formatter.py          # Email formatting functions
├── model_history.py            # W-L-P tracking system
├── predict_and_email.py        # Main prediction + email script (NEW)
├── update_results.py           # Daily results update script
├── backfill_from_sheets.py     # Google Sheets backfill tool
└── ensemble_spread_models.py   # Existing ensemble model trainer

data/
└── model_results/
    └── model_picks_history.csv # W-L-P tracking database (NEW)
```

## Module Descriptions

### 1. `prediction_core.py`
**Purpose**: Core functions for building prediction records and computing edges.

**Key Functions**:
- `american_to_prob(odds)` - Convert American odds to implied probability
- `compute_model_pick(prob_fav_cover, fav_odds, dog_odds, ...)` - Calculate edges and determine pick
- `build_prediction_record(game_row, model_predictions)` - Build standardized prediction dict

**Data Contract** - Prediction Record Structure:
```python
{
    "date": "2025-12-06",
    "home_team": "San Antonio Spurs",
    "away_team": "New Orleans Pelicans",
    "favorite_team": "San Antonio Spurs",
    "underdog_team": "New Orleans Pelicans",
    "spread": -9.5,              # Always favorite terms
    "fav_odds": -110,
    "dog_odds": -110,
    "fav_at_home": 1,
    "models": {
        "Logistic": {
            "prob_fav_cover": 0.65,      # Favorite-centric probability
            "prob_dog_cover": 0.35,
            "fav_edge": 0.126,           # Model prob - implied prob
            "dog_edge": -0.174,
            "pick_side": "FAVORITE",     # "FAVORITE" / "UNDERDOG" / "NO BET"
            "pick_team": "San Antonio Spurs",
            "pick_line": -9.5
        },
        "Linear": { ... },
        "Random Forest": { ... },
        "Decision Tree": { ... }
    }
}
```

### 2. `email_formatter.py`
**Purpose**: Format prediction records into readable email text.

**Key Functions**:
- `format_game_header(prediction)` - Format game header line
- `format_model_line(model_name, model_data)` - Format single model prediction line
- `format_game_predictions(prediction)` - Complete game with all models
- `format_model_records(records)` - Season W-L-P summary
- `format_predictions_for_email(predictions, records, date_str)` - Complete email body

**Example Output**:
```
🏀 San Antonio Spurs vs New Orleans Pelicans  (Favorite: San Antonio Spurs -9.5, Odds: -110 / -110)

Logistic:        New Orleans Pelicans +9.5      | Cover Prob:  74.9% | F Edge:  -27.5% | D Edge:  +22.7% | BEST: New Orleans Pelicans +9.5
Linear:          San Antonio Spurs -9.5         | Cover Prob:  61.0% | F Edge:   +6.5% | D Edge:   -9.1% | BEST: San Antonio Spurs -9.5
Random Forest:   NO BET                         | Cover Prob:  50.0% | F Edge:   -2.4% | D Edge:   -2.4% | BEST: No edge (pass)
Decision Tree:   San Antonio Spurs -9.5         | Cover Prob:  72.0% | F Edge:  +19.6% | D Edge:  -24.4% | BEST: San Antonio Spurs -9.5
```

### 3. `model_history.py`
**Purpose**: Track W-L-P results for each model and compute season records.

**Key Functions**:
- `initialize_history_file()` - Create history CSV if needed
- `record_predictions(predictions)` - Save predictions with PENDING status
- `update_results(date, master_df)` - Update PENDING → WIN/LOSS/PUSH
- `get_season_records(end_date)` - Compute W-L-P for each model

**History File Schema** (`data/model_results/model_picks_history.csv`):
```
date,game_id,home_team,away_team,favorite_team,underdog_team,spread,
model_name,pick_side,pick_team,pick_line,result
```

**Result Values**: `PENDING`, `WIN`, `LOSS`, `PUSH`, `NO BET`

### 4. `predict_and_email.py` (Main Script)
**Purpose**: Generate daily predictions and send via email.

**Usage**:
```bash
# Predict today's games and send email
python src/predict_and_email.py

# Predict specific date (no email)
python src/predict_and_email.py --date 2025-12-06 --no-email

# Save to file instead of email
python src/predict_and_email.py --date 2025-12-06 --save-to-file output.txt --no-email
```

**Workflow**:
1. Load master dataset
2. Train all 4 models on data before target date
3. Generate predictions for each game
4. Build standardized prediction records
5. Record predictions to history (PENDING)
6. Get current season W-L-P records
7. Format email with all models
8. Send email (if not disabled)

### 5. `update_results.py`
**Purpose**: Update history file with actual results after games complete.

**Usage**:
```bash
# Update yesterday's results (default)
python src/update_results.py

# Update specific date
python src/update_results.py --date 2025-12-06
```

**Workflow**:
1. Load master dataset with actual scores
2. Find PENDING predictions for date
3. Compare picks against actual outcomes
4. Update result field to WIN/LOSS/PUSH

**Should be run**: Daily after scores are finalized (part of morning routine).

### 6. `backfill_from_sheets.py`
**Purpose**: Pull historical Google Sheets exports for missing dates.

**Setup Required**:
1. Set environment variable: `GOOGLE_SERVICE_ACCOUNT_JSON` (JSON credentials)
2. Optionally set: `GOOGLE_DRIVE_FOLDER_ID` (target Drive folder)

**Usage**:
```bash
# Backfill Nov 27
python src/backfill_from_sheets.py --date 2025-11-27

# Download only (skip ETL)
python src/backfill_from_sheets.py --date 2025-11-27 --skip-etl
```

**Workflow**:
1. Search Google Drive for file: "NBA Statistics Export - Model Export YYYY-MM-DD"
2. Read "Training Set" sheet range B2:HW17
3. Filter out empty rows
4. Save to `data/raw/NBA_Training_Set_YYYY-MM-DD.csv`
5. Run ETL pipeline to merge into master (unless --skip-etl)

## Daily Workflow

### Morning Routine (After Games Complete)
```bash
# 1. Update yesterday's results
python src/update_results.py

# 2. Run standard data update (existing script)
python src/update_nba_data.py

# 3. Generate and email today's predictions
python src/predict_and_email.py
```

### GitHub Actions Workflow
Update `.github/workflows/daily_predictions.yml`:
```yaml
- name: Update Yesterday's Results
  run: python src/update_results.py

- name: Update NBA Data
  run: python src/update_nba_data.py

- name: Generate and Email Predictions
  run: python src/predict_and_email.py
```

## Testing

### Test Core Modules
```bash
# Test prediction core (edge calculations)
python src/prediction_core.py

# Test email formatter (see example output)
python src/email_formatter.py

# Test model history (initialize database)
python src/model_history.py
```

### Test Predictions
```bash
# Generate predictions for Dec 6 (save to file)
python src/predict_and_email.py --date 2025-12-06 --no-email --save-to-file test_output.txt

# Check the output
cat test_output.txt
```

### Test Backfill (if Google creds available)
```bash
# Try backfilling Nov 27
python src/backfill_from_sheets.py --date 2025-11-27 --skip-etl
```

## Migration from Old System

### Before
- `predict_today.py` - Only showed logistic model
- Static W-L record in code
- No tracking of individual model performance

### After
- `predict_and_email.py` - Shows all 4 models
- Dynamic W-L-P from `model_picks_history.csv`
- Full tracking of each model's picks and results

### Migration Steps
1. **Test new system** with historical dates (Dec 6, Dec 7)
2. **Backfill history** (optional): Run predictions for past dates to populate history
3. **Update workflows** to use new script
4. **Run first live day** with new system
5. **Monitor** email output and history tracking

## Example Outputs

### Prediction Email Header
```
====================================================================================================
🏀 NBA SPREAD PREDICTIONS - December 06, 2025
====================================================================================================

📈 Model Records (Season to Date)
- Logistic: 42-35-3
- Linear: 39-38-3
- Random Forest: 44-33-3
- Decision Tree: 37-40-3

====================================================================================================
```

### Game Prediction (All 4 Models)
```
🏀 Brooklyn vs New Orleans  (Favorite: Brooklyn +3.5, Odds: -110 / -110)

Logistic:        Brooklyn +3.5                  | Cover Prob:  64.2% | F Edge:  +11.8% | D Edge:  -16.6% | BEST: Brooklyn +3.5
Linear:          Brooklyn +3.5                  | Cover Prob:  73.2% | F Edge:  +20.8% | D Edge:  -25.6% | BEST: Brooklyn +3.5
Random Forest:   Brooklyn +3.5                  | Cover Prob:  57.9% | F Edge:   +5.5% | D Edge:  -10.2% | BEST: Brooklyn +3.5
Decision Tree:   Brooklyn +3.5                  | Cover Prob:  70.5% | F Edge:  +18.1% | D Edge:  -22.8% | BEST: Brooklyn +3.5
```

## Troubleshooting

### History file not updating
- Check that `update_results.py` is running daily
- Verify master dataset has actual scores in "Favorite Cover?" column
- Check history CSV for PENDING → WIN/LOSS transitions

### Backfill not finding sheets
- Verify `GOOGLE_SERVICE_ACCOUNT_JSON` is set correctly
- Check sheet naming: "NBA Statistics Export - Model Export YYYY-MM-DD"
- Try without `GOOGLE_DRIVE_FOLDER_ID` to search all folders

### Email not sending
- Verify SMTP environment variables: `SMTP_SERVER`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- Test with `--no-email --save-to-file` first
- Check firewall/network settings

### Models showing NO BET for everything
- Check that odds data exists in master dataset
- Verify edge calculations: edges may be legitimately negative
- Examine model probabilities: may be too close to 50%

## Framework Compliance

This implementation follows the framework guidelines:
- ✅ All probabilities stored as `prob_fav_cover` (favorite-centric)
- ✅ Pick logic uses max(fav_edge, dog_edge) with NO BET for ≤0
- ✅ Game header shows favorite, spread, and odds clearly
- ✅ One line per model with all relevant info
- ✅ Season records update daily from history file
- ✅ History tracking with W/L/P results
- ✅ Backfill mechanism for missing dates

## Next Steps

1. ✅ **Review example outputs** - Check Dec 6 predictions in `data/test_predictions_2025-12-06.txt`
2. ⚠️ **Test with live data** - Run for today (Dec 9) before committing
3. ⚠️ **Backfill historical data** - Run backfill for Nov 27 and Dec 4 if Google creds available
4. ⚠️ **Update GitHub Actions** - Modify workflow to use new scripts
5. ⚠️ **Monitor first live run** - Ensure email sends correctly and history tracks properly

---

**Author**: Orb Analytics (Liam Chaitin)  
**Date**: December 2025  
**Framework Version**: 2.0
