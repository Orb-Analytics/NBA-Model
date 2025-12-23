# 🎯 Daily NBA Predictions Workflow

## Overview
This workflow automatically generates NBA spread predictions for today's games and emails them after the daily dataset update completes.

## Workflow Chain

```
┌─────────────────────────────────────────────────────────┐
│ 1. Update Training Set from Google Sheets              │
│    (Runs daily at scheduled time)                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 📧 Email NBA Dataset                                 │
│    (Sends updated training set CSV)                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 🎯 Generate & Email Daily Predictions                │
│    (Predicts today's games and emails results)          │
└─────────────────────────────────────────────────────────┘
```

## Files

### Workflow File
- `.github/workflows/daily_predictions.yml` - GitHub Actions workflow

### Python Scripts
- `src/predict_today.py` - Generates predictions for today's games
- `src/daily_spread_predictions.py` - Core prediction model (imported)

## How It Works

1. **Triggered After Dataset Email**: Runs automatically when the dataset email workflow completes successfully

2. **Generates Predictions**:
   - Trains on ALL historical data before today
   - Dynamically selects top 15 features
   - Uses separate models for Home/Away favorites
   - Handles missing data with median imputation
   - Sorts predictions by confidence level

3. **Formats Email**:
   - High confidence bets marked with 💪
   - Medium confidence marked with ⚖️
   - Shows prediction, confidence %, and model used
   - Includes confidence breakdown and betting recommendations

4. **Sends Email**:
   - To: lpchaitin@gmail.com, eborsook@gmail.com
   - Subject: "🏀 NBA Spread Predictions - YYYY-MM-DD"
   - Body: Formatted predictions with emojis
   - Saves predictions as GitHub artifact

## Email Format Example

```
🏀 NBA SPREAD PREDICTIONS - 2025-11-05
======================================================================

📈 SEASON RECORD
   45-32 (58.4%)
   💰 Units: +8.45

📈 PERFORMANCE SPLITS

**By Pick Type:**
- Picking Favorites: 28-18 (60.9%) | +5.82 units
- Picking Underdogs: 17-14 (54.8%) | +2.63 units

**By Home/Away (All Games):**
- Favorite at Home: 32-20 (61.5%) | +7.23 units
- Favorite Away: 13-12 (52.0%) | +1.22 units

**By Pick + Location:**
- Picking Favorite at Home: 18-10 (64.3%) | +4.91 units
- Picking Favorite Away: 10-8 (55.6%) | +0.91 units
- Picking Underdog Away: 9-7 (56.3%) | +1.55 units
- Picking Underdog at Home: 8-7 (53.3%) | +1.08 units

======================================================================

📅 YESTERDAY'S RESULTS
======================================================================

✅ Houston -7.5
   Houston vs Memphis
   Edge: 8.2% | Units: +0.91

❌ Indiana +2.5
   Okla City vs Indiana
   Edge: 4.5% | Units: -1.00

Record: 1-2 | Units: -1.09
======================================================================

🎯 TODAY'S PICKS
======================================================================

💪 Houston vs Memphis (Spread: -7.5)
   Prediction: Favorite will COVER
   Confidence: 87.4%
   Model: Away Favorite

💪 La Lakers vs San Antonio (Spread: -2.5)
   Prediction: Favorite will NO COVER
   Confidence: 12.8%
   Model: Away Favorite

⚖️ Indiana vs Brooklyn (Spread: -6.5)
   Prediction: Favorite will COVER
   Confidence: 69.8%
   Model: Home Favorite

⚖️ Dallas vs New Orleans (Spread: 7.5)
   Prediction: Favorite will COVER
   Confidence: 65.9%
   Model: Home Favorite

======================================================================

📊 CONFIDENCE BREAKDOWN:
💪 High Confidence (>70% or <30%): 4 games
⚖️  Medium Confidence (55-70% or 30-45%): 6 games
⚠️  Low Confidence (45-55%): 1 games

======================================================================

🎲 BETTING RECOMMENDATIONS:
💪 High Confidence bets are recommended
⚖️  Medium Confidence bets are optional
⚠️  Low Confidence bets should be avoided
```

## Manual Trigger

You can manually trigger predictions for any date:

1. Go to Actions tab in GitHub
2. Select "🎯 Generate & Email Daily Predictions"
3. Click "Run workflow"
4. Enter date (YYYY-MM-DD) or leave blank for today
5. Click "Run workflow"

## Testing Locally

```bash
# Predict today's games
python src/predict_today.py

# Predict specific date
python src/predict_today.py 2025-11-05
```

## Prediction Confidence Levels

| Emoji | Confidence Range | Recommendation |
|-------|-----------------|----------------|
| 💪 | >70% or <30% | **Strong Bet** - High confidence recommendations |
| ⚖️ | 55-70% or 30-45% | **Optional** - Medium confidence, bet cautiously |
| ⚠️ | 45-55% | **Avoid** - Too close to call, no edge |

## Model Details

- **Training Data**: All games before prediction date (no look-ahead bias)
- **Feature Selection**: Dynamic top 15 features per model per day
- **Models**: Separate for Home Favorite vs Away Favorite scenarios
- **Algorithm**: Logistic Regression with L1 regularization
- **Missing Data**: Median imputation strategy
- **Scaling**: StandardScaler normalization

## Required Secrets

The workflow requires these GitHub secrets to be set:
- `SMTP_SERVER` - Email server address
- `SMTP_PORT` - Email server port
- `SMTP_USERNAME` - Email username
- `SMTP_PASSWORD` - Email password

## Output Files

- **Email**: Sent to configured recipients
- **Artifact**: Saved as `predictions-YYYY-MM-DD` in GitHub Actions
- **Local File**: `data/predictions_YYYY_MM_DD.txt` (when run locally)

## Troubleshooting

### No predictions generated
- Check if there are games scheduled for that date
- Verify the training dataset has sufficient historical data

### Workflow fails
- Check GitHub Actions logs for error details
- Verify all required secrets are configured
- Ensure dependencies are installed correctly

### Wrong predictions date
- Workflow uses UTC time by default
- Adjust timezone in workflow if needed

## Future Enhancements

- [ ] Add actual results comparison the next day
- [ ] Track prediction accuracy over time
- [x] Include betting unit recommendations and tracking
- [ ] Add injured player adjustments
- [ ] Include line movement analysis
- [ ] Send SMS notifications for high confidence bets

## Unit Tracking

The system now tracks betting units for all predictions:
- **1 unit per bet**: Each pick risks 1 unit
- **Wins pay based on odds**: 
  - Favorites (negative odds like -110): Win amount = 100 / |odds|
  - Underdogs (positive odds like +150): Win amount = odds / 100
- **Losses lose 1 unit**: Standard flat betting approach
- **Displayed everywhere**: Season totals, splits, and daily P&L all show units won/lost
- **Format**: "+2.45 units" for wins, "-1.00 units" for losses
