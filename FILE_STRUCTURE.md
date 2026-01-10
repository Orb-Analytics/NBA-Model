# 📁 NBA Model - Repository Structure

## Overview
Clean, organized structure for the NBA spread prediction model with averaged predictions system.

---

## 📂 Directory Tree

```
NBA-model/
├── 📁 data/                              # All data files
│   ├── 📊 NBA Training Set 25-26.csv              # Master dataset (1.7M)
│   ├── 📊 unified_model_results.csv               # All 4 model probabilities (203K)
│   ├── 📊 averaged_model_backtest.csv             # Backtest snapshot (99K)
│   ├── 📊 averaged_model_predictions_history.csv  # Permanent archive (97K)
│   ├── 📄 selected_features.txt                   # Feature lists
│   ├── 📁 novig-odds/                            # Novig odds data
│   ├── 📁 raw/                                   # Raw training set backups
│   └── 📁 yesterdays_scores/                     # Daily score updates
│
├── 📁 src/                               # Python source code (22 scripts)
│   │
│   ├── 🔄 Data Pipeline (11 scripts)
│   │   ├── daily_update.py              # Main automation
│   │   ├── update_nba_data.py           # Update master dataset
│   │   ├── update_results.py            # Update game results
│   │   ├── novig_nba_odds.py           # Fetch odds
│   │   ├── merge_nba_scores.py         # Merge scores
│   │   ├── merge_novig_odds.py         # Merge odds
│   │   ├── merge_raw_data.py           # Merge raw data
│   │   ├── backfill_from_sheets.py     # Google Sheets backfill
│   │   ├── normalize_data.py           # Data normalization
│   │   ├── fix_computed_columns.py     # Fix calculations
│   │   └── validate_data.py            # Data validation
│   │
│   ├── 🤖 ML Models (6 scripts)
│   │   ├── logistic_spread_model.py    # Logistic regression
│   │   ├── linear_spread_model.py      # Linear regression
│   │   ├── random_forest_spread_model.py  # Random forest
│   │   ├── ensemble_spread_models.py   # Ensemble predictor
│   │   ├── prediction_core.py          # Core utilities
│   │   └── daily_spread_predictions.py # Feature definitions
│   │
│   └── 🎯 Averaged Model (4 scripts)
│       ├── backtest_averaged_simple.py        # Backtest with 3% threshold
│       ├── predict_today_averaged.py          # Generate daily predictions
│       ├── predict_and_email_averaged.py      # Send email notifications
│       └── regenerate_unified_results.py      # Regenerate all probabilities
│
├── 📁 tests/                             # Test suite
│   ├── test_pipeline.py
│   └── test_spread_model.py
│
├── 📁 docs/                              # Documentation
│   ├── COPILOT_FRAMEWORK.md
│   └── README_PREDICTIONS.md
│
├── 📁 .github/workflows/                 # GitHub Actions
│   ├── ⚙️ update_training_set.yml       # Daily 10:30 AM PT data update
│   ├── 📧 email_nba_dataset.yml         # Dataset email notification
│   └── 🎯 daily_predictions.yml         # Generate & email predictions
│
├── 📄 README.md                          # Main documentation
├── 📄 MODEL_PERFORMANCE.md               # Performance tracking
├── 📄 FILE_STRUCTURE.md                  # This file
├── 📄 requirements.txt                   # Python dependencies
└── 📄 .gitignore                         # Git ignore rules

```

---

## 🔑 Key Components

### Averaged Model System
**Formula:** `standardized_prob = (35% × averaged_model_prob) + (65% × implied_odds_prob)`
- **Edge Threshold:** 3% minimum to make picks
- **Performance:** 106-92 (53.5%) through Dec 20, 2025

### Daily Workflow
1. **10:30 AM PT:** Update training set from Google Sheets
2. **After update:** Email dataset notification
3. **After email:** Generate predictions and send to subscribers

### Core Data Files
- `NBA Training Set 25-26.csv` - Complete game data with statistics
- `unified_model_results.csv` - Probabilities from all 4 models
- `averaged_model_backtest.csv` - Current backtest snapshot
- `averaged_model_predictions_history.csv` - Permanent prediction archive

---

## 📊 Statistics

- **Total Scripts:** 22 Python files
- **Core Data Files:** 4 CSV files
- **Documentation:** 3 markdown files
- **Active Workflows:** 3 GitHub Actions
- **Repository Size:** ~3.4M (primarily data)

