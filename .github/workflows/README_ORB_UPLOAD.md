# 🌐 Orb Analytics Upload Workflow

## What This Is

A **completely separate** GitHub Actions workflow that uploads your NBA predictions to the Orb Analytics web platform.

## Important Notes

### ✅ What This Does
- Runs AFTER all your existing workflows complete successfully
- Reads predictions from `data/averaged_model_predictions_history.csv` (already saved by your prediction workflow)
- POSTs predictions to Orb Analytics Supabase API
- Makes predictions appear live on your website

### ✅ What This Does NOT Do
- **Does NOT modify** any existing workflows
- **Does NOT change** how predictions are generated
- **Does NOT interfere** with email sending
- **Does NOT affect** X/Twitter posting
- **Does NOT touch** any of your current automation

## Workflow Trigger

This workflow triggers automatically when:
```yaml
workflow_run:
  workflows: ["🎯 Generate & Email Daily Predictions"]
  types:
    - completed
```

**Translation:** After your daily prediction workflow finishes successfully, this runs.

## Workflow File

**Location:** `.github/workflows/upload_to_orb_analytics.yml`

**Actions:**
1. Checks out the repo
2. Sets up Python
3. Installs dependencies (pandas, requests)
4. Runs `python src/upload_predictions_to_orb.py`

## Testing

### Manual Trigger
You can manually run this workflow without waiting for the automatic trigger:

1. Go to GitHub → Actions tab
2. Click "🌐 Upload Predictions to Orb Analytics"
3. Click "Run workflow"
4. Enter a date (e.g., 2026-01-31) or leave blank for today
5. Click "Run workflow"

### Local Testing (Dry Run)
Test without actually uploading:
```bash
python src/upload_predictions_to_orb.py --dry-run --date 2026-01-31
```

## Required Secrets

Add these to your GitHub repository secrets:
- `ORB_PLATFORM_URL` - Your Supabase API endpoint
- `ORB_PLATFORM_KEY` - Your API authentication key

**Path:** Repository → Settings → Secrets and variables → Actions → New repository secret

## Disabling This Workflow

If you need to disable this integration temporarily:

1. Rename the workflow file:
   ```bash
   mv .github/workflows/upload_to_orb_analytics.yml .github/workflows/upload_to_orb_analytics.yml.disabled
   ```

2. Or delete the file entirely - your existing workflows will continue working normally

## Status Checking

After the workflow runs, check:
- GitHub Actions → "🌐 Upload Predictions to Orb Analytics" → View logs
- Orb Analytics website to verify predictions appear
- Look for "✅ Upload complete" in the logs

## Troubleshooting

**Workflow doesn't run:**
- Check that "🎯 Generate & Email Daily Predictions" completed successfully
- Verify the workflow file is in `.github/workflows/`

**Upload fails:**
- Check that GitHub secrets are set correctly
- Verify the API endpoint URL is correct
- Check the workflow logs for specific error messages

**No predictions found:**
- Verify predictions exist in `averaged_model_predictions_history.csv` for that date
- Check that the date format is YYYY-MM-DD

## More Documentation

- **Full Integration Guide:** `docs/ORB_ANALYTICS_INTEGRATION.md`
- **Setup Summary:** `ORB_INTEGRATION_SUMMARY.md`
- **Upload Script:** `src/upload_predictions_to_orb.py`

---

**Remember:** This is a completely optional add-on. Your existing prediction system works independently and will continue running normally whether this workflow succeeds or fails.
