# 🏀 NBA Spread Prediction Model

Advanced NBA spread prediction system using machine learning with automated daily predictions.

## 📊 Current Performance
**252-219 (53.5%)** through April 06, 2026

### 📈 Performance Splits

**By Pick Type:**
- Picking Favorites: 110-108 (50.5%)
- Picking Underdogs: 142-111 (56.1%)

**By Home/Away (All Games):**
- Favorite at Home: 125-118 (51.4%)
- Favorite Away: 127-101 (55.7%)

**By Pick + Location:**
- Picking Favorite at Home: 58-56 (50.9%)
- Picking Favorite Away: 52-52 (50.0%)
- Picking Underdog Away: 67-62 (51.9%)
- Picking Underdog at Home: 75-49 (60.5%)
## 🎯 System Overview

This repository implements an **averaged model system** that combines:
- 35% ML model predictions (3 models averaged: Logistic, Linear, Random Forest)
- 65% implied odds probabilities
- 3% minimum edge threshold for picks

### Model Architecture
- **Logistic Regression** - Binary classification
- **Linear Regression** - Continuous predictions
- **Random Forest** - Ensemble tree-based

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
