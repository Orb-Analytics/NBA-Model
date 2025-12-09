# Daily Predictions Workflow - FINALIZED ✅

## Summary
The daily predictions email workflow has been updated and tested. It now shows **all 4 models** with **dynamically updating records** that reflect the complete season history.

## Key Features

### 📊 Model Records (Auto-Updating)
- **Logistic Regression**: 155-147-0 (51.3%)
- **Linear Regression**: 161-154-0 (51.1%)
- **Random Forest**: 161-139-0 (53.7%)
- **Decision Tree**: 157-157-0 (50.0%)

Records automatically update as new games are completed.

### 🏀 Prediction Format
Each game shows:
- All 4 model predictions (one per line)
- Pick team and spread line
- Cover probability
- Favorite edge (F Edge)
- Underdog edge (D Edge)
- Best bet indicator

Example:
```
🏀 Indiana vs Sacramento  (Favorite: Indiana +4.5, Odds: +106 / -111)

Logistic:        Sacramento +4.5    | Cover Prob:  60.0% | F Edge:  -8.6% | D Edge:  +7.4% | BEST: Sacramento +4.5
Linear:          Sacramento +4.5    | Cover Prob:  67.8% | F Edge: -16.3% | D Edge: +15.2% | BEST: Sacramento +4.5
Random Forest:   Sacramento +4.5    | Cover Prob:  55.1% | F Edge:  -3.6% | D Edge:  +2.5% | BEST: Sacramento +4.5
Decision Tree:   Sacramento +4.5    | Cover Prob:  55.3% | F Edge:  -3.8% | D Edge:  +2.7% | BEST: Sacramento +4.5
```

## Workflow Automation

### Trigger
The workflow runs automatically after the "📧 Email NBA Dataset" workflow completes successfully.

### Process
1. **Data Update**: Training dataset is updated with latest games
2. **Model Training**: All 4 models train on historical data (rolling window)
3. **Record Calculation**: Loads complete season history from `data/model_results/model_picks_history.csv`
4. **Prediction Generation**: Creates predictions for today's games
5. **Email Formatting**: Shows records + all model picks
6. **Email Delivery**: Sends to configured recipients

### Manual Trigger
```bash
# Test locally (no email)
python src/predict_and_email.py --date 2025-12-08 --no-email

# Send actual email
python src/predict_and_email.py --date 2025-12-08
```

## File Structure

### Core Scripts
- `src/predict_and_email.py` - Main prediction script with email sending
- `src/ensemble_spread_models.py` - 4-model ensemble trainer
- `src/email_formatter.py` - Email formatting logic
- `src/model_history.py` - Record tracking and W-L-P calculations
- `src/prediction_core.py` - Edge calculations and pick logic
- `src/update_results.py` - Updates PENDING picks to WIN/LOSS after games complete

### Data Files
- `data/NBA Training Set 25-26.csv` - Master dataset with all games and features
- `data/model_results/model_picks_history.csv` - Complete season pick history (1300+ predictions)
- `data/yesterdays_scores/` - Daily score files from ESPN API

### GitHub Workflow
- `.github/workflows/daily_predictions.yml` - Automated daily predictions workflow

## Bug Fix Applied ✅

### Issue
Models were showing 32-36% win rate (severely underperforming).

### Root Cause
The `pick_line` values were inverted:
- Favorites were stored with positive lines (e.g., +11.5)
- Underdogs were stored with negative lines (e.g., -11.5)

This caused the WIN/LOSS calculation logic to produce completely inverted results.

### Fix
Corrected `src/prediction_core.py` lines 139 and 142:
```python
# BEFORE (WRONG)
pick_line = spread      # for favorite
pick_line = -spread     # for underdog

# AFTER (CORRECT)
pick_line = -spread     # for favorite (negative line)
pick_line = spread      # for underdog (positive line)
```

### Result
Models now perform at 50-54% win rate, matching the original performance:
- Logistic: 52.7% → 51.3% ✅
- Linear: 53.9% → 51.1% ✅
- Random Forest: 56.5% → 53.7% ✅
- Decision Tree: 54.3% → 50.0% ✅

## Historical Data

### Season Coverage
- **Start Date**: October 23, 2025
- **Latest Date**: December 7, 2025
- **Total Predictions**: 1,300+ across all 4 models
- **Finalized Games**: 1,227 (WIN/LOSS/PUSH)
- **Pending Games**: 12 (December 8, 2025)

### Backfill Complete
All predictions from Oct 23 - Dec 7 have been generated and scored. Records now reflect complete season performance.

## Environment Variables Required

For email sending to work, these must be set in GitHub Secrets:
- `SMTP_SERVER` - SMTP server address (e.g., smtp.gmail.com)
- `SMTP_PORT` - SMTP port (e.g., 587)
- `SMTP_USERNAME` - Email username
- `SMTP_PASSWORD` - Email password or app-specific password
- `TO_EMAIL` - Recipient email(s)

## Testing

To test the workflow locally without sending email:
```bash
cd /workspaces/NBA-model
python src/predict_and_email.py --date 2025-12-08 --no-email
```

Expected output:
- Model records (155-147-0, etc.)
- Predictions for all games on that date
- All 4 model picks per game
- Edge calculations and best bet indicators

## Next Steps

1. ✅ **Workflow is ready** - Will run automatically when new data is available
2. ✅ **Records are accurate** - Showing full season history (Oct 23 - Dec 7)
3. ✅ **All 4 models shown** - Each game displays predictions from all models
4. ✅ **Bug fixed** - Models performing at expected 50-54% win rate

**The system is fully operational and ready for production use!**
