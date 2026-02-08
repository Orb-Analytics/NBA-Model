# 🏀 NBA Spread Prediction Model

Advanced NBA spread prediction system using machine learning with automated daily predictions.

## 📊 Current Performance
**173-153 (53.1%)** through February 07, 2026

### 📈 Performance Splits

**By Pick Type:**
- Picking Favorites: 52-62 (45.6%)
- Picking Underdogs: 117-91 (56.2%)

**By Home/Away (All Games):**
- Favorite at Home: 59-68 (46.5%)
- Favorite Away: 110-85 (56.4%)

**By Pick + Location:**
- Picking Favorite at Home: 26-31 (45.6%)
- Picking Favorite Away: 26-31 (45.6%)
- Picking Underdog Away: 33-37 (47.1%)
- Picking Underdog at Home: 84-54 (60.9%)
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
