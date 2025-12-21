# NBA Model File Structure

## Core Files (Keep)

### Data Pipeline
- `src/daily_update.py` - Main daily automation script
- `src/update_nba_data.py` - Update master dataset
- `src/update_results.py` - Update game results
- `src/novig_nba_odds.py` - Fetch odds data
- `src/merge_nba_scores.py` - Merge scores into dataset
- `src/merge_novig_odds.py` - Merge odds into dataset
- `src/merge_raw_data.py` - Merge raw data sources
- `src/backfill_from_sheets.py` - Backfill from Google Sheets
- `src/normalize_data.py` - Data normalization
- `src/fix_computed_columns.py` - Fix calculated columns
- `src/validate_data.py` - Data validation

### ML Models (4 models)
- `src/logistic_spread_model.py` - Logistic regression model
- `src/linear_spread_model.py` - Linear regression model
- `src/random_forest_spread_model.py` - Random forest model
- `src/decision_tree_spread_model.py` - Decision tree model
- `src/ensemble_spread_models.py` - Ensemble predictor combining all 4
- `src/prediction_core.py` - Core prediction utilities
- `src/daily_spread_predictions.py` - Feature definitions

### Averaged Model (Current Focus)
- `src/backtest_averaged_simple.py` - Backtest averaged model
- `src/predict_today_averaged.py` - Generate daily predictions
- `src/predict_and_email_averaged.py` - Send prediction emails
- `src/regenerate_unified_results.py` - Regenerate unified results

### Data Files
- `data/NBA Training Set 25-26.csv` - Master dataset (1.7M)
- `data/unified_model_results.csv` - All 4 model probabilities (203K)
- `data/averaged_model_backtest.csv` - Current backtest snapshot (99K)
- `data/averaged_model_predictions_history.csv` - Permanent archive (97K)
- `data/selected_features.txt` - Selected features for models
- `data/raw/` - Raw daily data
- `data/novig-odds/` - Daily odds data
- `data/yesterdays_scores/` - Score archives
- `data/model_results/` - Individual model outputs (archive)

## Files to Remove

### Obsolete Scripts
- `src/logistic_spread_model_old.py` - Old version
- `src/analyze_ensemble.py` - Not used anymore
- `src/analyze_market_regression.py` - Not used anymore
- `src/model_history.py` - Not used anymore
- `src/email_formatter.py` - Not used anymore
- `src/send_test_sms.py` - Testing only
- `src/send_free_notifications.py` - Not used

### Obsolete Data
- `data/model_results/` - Individual model result CSVs (archive)

