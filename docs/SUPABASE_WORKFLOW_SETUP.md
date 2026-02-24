# 🔄 Adding Supabase Sync to GitHub Workflows

## Option 1: Add to Existing Daily Predictions Workflow

Add this step to `.github/workflows/daily_predictions.yml` after the "Post Predictions to X" step:

```yaml
      - name: 🔗 Sync to Supabase
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          echo "📤 Syncing latest data to Supabase..."
          python src/sync_to_supabase.py --mode all
```

**Location**: Insert after line ~100 (after X posting step)

## Option 2: Create Separate Workflow

Create `.github/workflows/sync_supabase.yml`:

```yaml
name: 🔗 Sync to Supabase

on:
  # Run after daily predictions complete
  workflow_run:
    workflows: ["🎯 Generate & Email Daily Predictions"]
    types:
      - completed
  
  # Allow manual trigger
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}

    steps:
      - name: 📂 Checkout repo
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 📦 Install dependencies
        run: |
          pip install requests pandas

      - name: 🔗 Sync to Supabase
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          echo "📤 Syncing all data to Supabase..."
          python src/sync_to_supabase.py --mode all
          echo "✅ Sync complete!"
```

## Required GitHub Secrets

Add these to your repository secrets (Settings → Secrets and variables → Actions):

1. **SUPABASE_URL**: `https://skfraijnuefuquyxnced.supabase.co`
2. **SUPABASE_KEY**: Your service_role key (already in your `.env`)

## Testing

Test the sync manually:
```bash
# Set secrets as environment variables
export SUPABASE_URL="https://skfraijnuefuquyxnced.supabase.co"
export SUPABASE_KEY="your-service-role-key"

# Run sync
python src/sync_to_supabase.py --mode all
```

## What Gets Synced

- **Daily predictions** - Today's picks
- **Historical results** - All completed games
- **Season stats** - Current record, units, ROI

Data updates automatically after each prediction run!
