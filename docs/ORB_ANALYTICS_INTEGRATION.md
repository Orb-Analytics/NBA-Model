# 🌐 Orb Analytics Integration

This document explains how NBA model predictions are automatically uploaded to the Orb Analytics web platform.

## Overview

Every time the daily prediction workflow runs, predictions are automatically POSTed to the Orb Analytics Supabase API, making them instantly available on the web platform.

**IMPORTANT:** This integration uses a **completely separate GitHub Actions workflow** that runs AFTER all existing workflows complete. Your current automation is not modified in any way.

## Data Flow

```
GitHub Actions: Update Training Set
        ↓
GitHub Actions: Email NBA Dataset
        ↓
GitHub Actions: Generate & Email Daily Predictions
        ↓ (saves to averaged_model_predictions_history.csv)
        ↓
        ✅ ALL EXISTING WORKFLOWS COMPLETE
        ↓
GitHub Actions: Upload to Orb Analytics (NEW SEPARATE WORKFLOW)
        ↓ (reads CSV, POSTs to API)
        ↓
Predictions appear on Orb Analytics website
```

**Key Points:**
- ✅ New workflow runs AFTER existing workflows succeed
- ✅ Zero modifications to existing workflows
- ✅ If upload fails, existing workflows are unaffected
- ✅ Can be disabled without breaking anything

## Upload Script

**File:** `src/upload_predictions_to_orb.py`

### Features
- ✅ Reads from `data/averaged_model_predictions_history.csv`
- ✅ Filters to current day's picks only
- ✅ Excludes "NO BET" games
- ✅ Transforms data to match Orb Analytics API format
- ✅ Maps edge percentages to confidence levels
- ✅ Handles home/away team determination
- ✅ Includes dry-run mode for testing

### Usage

**Dry Run (test without uploading):**
```bash
python src/upload_predictions_to_orb.py --dry-run
```

**Upload specific date:**
```bash
python src/upload_predictions_to_orb.py --date 2026-02-01
```

**Upload today's predictions:**
```bash
python src/upload_predictions_to_orb.py
```

## Data Mapping

Your model's columns → Orb Analytics API format:

| Model Column | API Field | Notes |
|-------------|-----------|-------|
| `date` | `date` | YYYY-MM-DD format |
| `favorite` + `underdog` + `fav_upload_to_orb_analytics.yml` (NEW SEPARATE FILE)

This is a **completely independent workflow** that:
- Triggers AFTER "🎯 Generate & Email Daily Predictions" completes successfully
- Does NOT modify any existing workflows
- Reads predictions from the CSV file that's already been saved
- If it fails, your existing automation continues working normally

```yaml
name: 🌐 Upload Predictions to Orb Analytics

on:
  workflow_run:
    workflows: ["🎯 Generate & Email Daily Predictions"]
    types:
      - completed

jobs:
  upload-to-orb:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    
    steps:
      - name: 🌐 Upload Predictions to Orb Analytics Platform
        env:
          ORB_PLATFORM_URL: ${{ secrets.ORB_PLATFORM_URL }}
          ORB_PLATFORM_KEY: ${{ secrets.ORB_PLATFORM_KEY }}
        run: |
      **Workflow:** `.github/workflows/daily_predictions.yml`

The upload step runs automatically after predictions are generated:

```yaml
- name: 🌐 Upload Predictions to Orb Analytics
  env:
    ORB_PLATFORM_URL: ${{ secrets.ORB_PLATFORM_URL }}
    ORB_PLATFORM_KEY: ${{ secrets.ORB_PLATFORM_KEY }}
  run: |
    python src/upload_predictions_to_orb.py --date "$PRED_DATE"
```

## Required GitHub Secrets

These secrets must be configured in your repository settings:

- `ORB_PLATFORM_URL` - Your Supabase API endpoint
- `ORB_PLATFORM_KEY` - Your API authentication key

**To add secrets:** Repository Settings → Secrets and variables → Actions → New repository secret

## API Endpoint

**POST** `{ORB_PLATFORM_URL}/predictions/batch`

**Headers:**
```
Authorization: Bearer {ORB_PLATFORM_KEY}
Content-Type: application/json
```

**Payload:**
```json
{
  "predictions": [
    {
      "game_id": "unique_identifier",
      "date": "YYYY-MM-DD",
      "home_team": "Team Name",
      "away_team": "Team Name",
      "pick": "Team Name",
      "spread": -3.5,
      "ml_probability": 0.58,
      "implied_probability": 0.54,
      "edge": 4.2,
      "confidence": "high"
    }
  ]
}
```

## Testing

### Local Testing (Dry Run)
```bash
# Test with recent date that has predictions
python src/upload_predictions_to_orb.py --dry-run --date 2026-01-31
```

### Manual Workflow Trigger
You can manually trigger the workflow from GitHub Actions tab:
1. Go to Actions → "🎯 Generate & Email Daily Predictions"
2. Click "Run workflow"
3. Optionally specify a date
4. Check logs to verify upload

## Troubleshooting

**"No predictions found for date"**
- Check that predictions exist in `data/averaged_model_predictions_history.csv` for that date
- Verify the date format is YYYY-MM-DD

**"Missing ORB_PLATFORM_URL/KEY"**
- Verify secrets are set in GitHub repository settings
- Make sure secret names match exactly

**"Upload failed" / API errors**
- Check the response status code and message in logs
- Verify API endpoint URL is correct
- Confirm API key has proper permissions

## Model Context

This integration is part of the **NBA Averaged Model System** which:
- Combines 3 ML models (Logistic, Linear, Random Forest)
- Applies 35% model weight + 65% implied odds weight
- Requires 3% minimum edge threshold for picks
- Currently running at **163-144 (53.1%)** through January 31, 2026

For more details, see:
- [README.md](../README.md) - Main documentation
- [MODEL_PERFORMANCE.md](../MODEL_PERFORMANCE.md) - Performance details
- [FILE_STRUCTURE.md](../FILE_STRUCTURE.md) - Repository structure
