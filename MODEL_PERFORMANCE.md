# NBA Spread Prediction Model - Rolling Daily Predictions

## Overview
This logistic regression model predicts NBA games against the spread using a **rolling time-series approach**. The model trains on historical data and makes predictions for each day, with features selected dynamically based on the training data available at that time.

## Key Features

### 🎯 Rolling Daily Predictions
- Trains only on games **before** the prediction date (no look-ahead bias)
- Selects top 15 features dynamically each day using L1 regularization
- Separate models for **Home Favorite** vs **Away Favorite** scenarios
- Predictions made for dates: **2025-10-21 through 2025-11-05**

### 📊 Performance Summary

**Overall Statistics:**
- Total Predictions: 87 games
- Completed: 75 games  
- Accuracy: **54.67%** (41/75)
- Pending: 12 games (2025-11-05)

**By Model Type:**
- 🏠 **Home Favorite**: 41.94% accuracy (31 games)
- ✈️ **Away Favorite**: 63.64% accuracy (44 games)

**By Confidence Level:**
- Very High (>80% or <20%): 50.00% accuracy (24 games)
- High (60-80% or 20-40%): **61.76% accuracy** (34 games) ⭐
- Medium (50-60% or 40-50%): 47.06% accuracy (17 games)

### 💰 Betting Simulation Results

**Flat Betting ($100 per game):**
- Total Profit: **+$360.00**
- ROI: **4.36%**

**High Confidence Only (>70% or <30%):**
- 40 games, 55% accuracy
- Total Profit: **+$220.00**
- ROI: **5.00%**

**Kelly Criterion (proportional betting):**
- Total Risked: $3,222.02
- Total Profit: **+$115.08**
- ROI: **3.57%**

### 🏆 Best Performance Days
1. **2025-10-27**: 100.0% accuracy (10/10 correct) 🎉
2. **2025-10-30**: 75.0% accuracy (3/4 correct)
3. **2025-11-02**: 75.0% accuracy (6/8 correct)

## Files

### Core Model
- **`src/ensemble_spread_models.py`** - Ensemble model combining Logistic, Linear, and Random Forest predictors with HOME/AWAY feature sets
- **`src/predict_and_email_averaged.py`** - Main prediction script with email notifications

### Analysis
- **`src/backtest_averaged_simple.py`** - Performance analysis and backtesting
- **`src/regenerate_unified_results.py`** - Regenerate all model predictions

### Data
- **`data/NBA Training Set 25-26.csv`** - Master training dataset (1,110 games)
- **`data/daily_predictions_results.csv`** - Prediction results with outcomes
- **`data/selected_features.txt`** - Top 15 features for each scenario

## Usage

### 1. Run Daily Predictions
```bash
python src/predict_and_email_averaged.py --date 2026-02-09 --no-email
```

This will:
- Load ensemble model with HOME/AWAY specific features
- Train on historical data with Logistic, Linear, and Random Forest models
- Generate probability predictions for today's games
- Apply 3% edge threshold for picks
- Save results to `data/averaged_model_predictions_history.csv`

### 2. Backtest Model
```bash
python src/backtest_averaged_simple.py
```

Provides:
- Overall accuracy statistics (167-146, 53.4%)
- Performance by confidence level
- Betting simulation results (+$1,438 profit, +4.59% ROI)
- Kelly Criterion analysis

### 3. Use as Library
```python
from src.ensemble_spread_models import EnsembleSpreadPredictor, HOME_PREDICTORS, AWAY_PREDICTORS

# Initialize
predictor = EnsembleSpreadPredictor('data/NBA Training Set 25-26.csv')

# Run predictions with ensemble
predictor.run_daily_predictions(
    start_date='2025-10-21',
    end_date='2025-11-05'
)

# Access results
for day_result in predictor.daily_results:
    print(f"Date: {day_result['date']}")
    for pred in day_result['predictions']:
        print(f"  {pred['favorite']} vs {pred['underdog']}: {pred['predicted_cover']}")
```

## Methodology

### Feature Selection Process
For each prediction date:
1. Split data into training (before date) and prediction (on date)
2. Separate by Home Favorite vs Away Favorite
3. Use L1 regularization (Lasso) to select top 15 features
4. Train logistic regression on selected features
5. Make predictions with confidence scores

### Feature Pools
- **Home Favorite**: 172 potential features (home/away splits favor home team)
- **Away Favorite**: 172 potential features (home/away splits favor away team)

Feature categories include:
- Points per game (overall, L3, L1, home/away)
- Offensive/Defensive efficiency
- Rebounds (offensive, defensive, total rebound %)
- 3-pointers, blocks, steals, assists, turnovers
- Effective possession ratio
- Close game performance

### Model Training
- Algorithm: Logistic Regression (C=1.0)
- Feature Scaling: StandardScaler
- Validation: Time-series split (no look-ahead)
- Output: Binary classification (Cover=1, No Cover=0) + probability

## Key Insights

### ✅ What Works
1. **Away Favorite model** significantly outperforms (63.64% vs 41.94%)
2. **High confidence bets** (60-80% range) show best accuracy (61.76%)
3. Consistent positive ROI across betting strategies
4. Very strong days (Oct 27: 10/10) show model can be highly accurate

### ⚠️ Areas for Improvement
1. Home Favorite model underperforms (41.94%)
2. Very high confidence (>80%) not as reliable as expected (50%)
3. High variance across days (0% to 100%)
4. Some days show poor performance (Oct 29: 2/10)

### 💡 Recommendations
1. **Focus on Away Favorite bets** - More consistent performance
2. **Target 60-80% confidence range** - Best risk/reward
3. **Avoid very low confidence** (<40%) - No edge demonstrated
4. **Consider ensemble approach** - Combine multiple models
5. **Track feature importance** - Monitor which stats matter most

## Future Enhancements

1. **Feature Engineering**
   - Momentum indicators (3-game, 5-game trends)
   - Rest days between games
   - Travel distance for away teams
   - Head-to-head historical matchups

2. **Model Improvements**
   - Ensemble methods (Random Forest, XGBoost)
   - Neural networks for non-linear relationships
   - Separate models for different spread ranges

3. **Risk Management**
   - Bankroll management strategies
   - Loss limits and profit targets
   - Correlation analysis between games

4. **Real-time Integration**
   - Automated data updates
   - Live odds scraping
   - Injury/lineup adjustments

## Dependencies

```python
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

## Author
Orb Analytics (Liam Chaitin)

## License
Proprietary - All Rights Reserved
