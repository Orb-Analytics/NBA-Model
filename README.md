# 🏀 NBA Spread Prediction Model

Advanced NBA spread prediction system using machine learning with automated daily predictions.

## 📊 Current Performance
**131-115 (53.3%)** through January 02, 2026

### 📈 Performance Splits

**By Pick Type:**
- Picking Favorites: 49-49 (50.0%)
- Picking Underdogs: 82-66 (55.4%)

**By Home/Away (All Games):**
- Favorite at Home: 52-58 (47.3%)
- Favorite Away: 79-57 (58.1%)

**By Pick + Location:**
- Picking Favorite at Home: 28-28 (50.0%)
- Picking Favorite Away: 21-21 (50.0%)
- Picking Underdog Away: 24-30 (44.4%)
- Picking Underdog at Home: 58-36 (61.7%)
## 🎯 System Overview

This repository implements an **averaged model system** that combines:
- 35% ML model predictions (4 models averaged)
- 65% implied odds probabilities
- 3% minimum edge threshold for picks

### Model Architecture
- **Logistic Regression** - Binary classification
- **Linear Regression** - Continuous predictions
- **Random Forest** - Ensemble tree-based
- **Decision Tree** - Single tree classifier

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run Daily Predictions
```bash
python src/predict_today_averaged.py
```

### Backtest Performance
```bash
python src/backtest_averaged_simple.py --start-date 2025-10-23
```

### Email Predictions
```bash
python src/predict_and_email_averaged.py
```

## 📁 Repository Structure

```
NBA-model/
├── data/          # Training data, predictions, backtest results
├── src/           # 22 Python scripts (pipeline + models)
├── docs/          # Documentation
├── tests/         # Test suite
└── .github/       # Automated workflows
```

See [FILE_STRUCTURE.md](FILE_STRUCTURE.md) for detailed organization.

## 🤖 Automated Workflows

Daily automation via GitHub Actions:
1. **10:30 AM PT** - Update training data from Google Sheets
2. **After update** - Generate predictions
3. **Send email** - Distribute picks to subscribers

##  Documentation

- [FILE_STRUCTURE.md](FILE_STRUCTURE.md) - Repository organization
- [MODEL_PERFORMANCE.md](MODEL_PERFORMANCE.md) - Performance metrics
- [docs/COPILOT_FRAMEWORK.md](docs/COPILOT_FRAMEWORK.md) - Development framework
- [docs/README_PREDICTIONS.md](docs/README_PREDICTIONS.md) - Prediction system details

## 🔧 Development

### Data Pipeline
```bash
python src/daily_update.py      # Update all data
python src/validate_data.py     # Validate dataset
```

### Model Training
```bash
python src/regenerate_unified_results.py  # Regenerate all predictions
```

### Testing
```bash
python -m pytest tests/
```

## 📊 Data Sources

- Google Sheets - Daily game data and statistics
- Novig API - Live betting odds
- Custom feature engineering - 200+ calculated statistics

## ⚙️ Configuration

Set environment variables:
- `SMTP_SERVER`, `SMTP_USERNAME`, `SMTP_PASSWORD` - Email configuration
- `GOOGLE_SHEETS_CREDENTIALS` - Data source access

## 📝 License

Private repository - All rights reserved
