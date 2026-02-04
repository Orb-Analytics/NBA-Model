# GitHub Actions Workflow Update Guide

## Step 1: Locate Your Workflow File

Your workflow file is likely at:
- `.github/workflows/daily_predictions.yml`
- OR `.github/workflows/main.yml`
- OR `.github/workflows/nba_model.yml`

## Step 2: Add Upload Step

Find the section where your model runs, and add the Supabase upload step **immediately after** it:

```yaml
name: Daily NBA Predictions

on:
  schedule:
    # Runs every day at 9 AM Pacific Time (5 PM UTC)
    - cron: '0 17 * * *'
  workflow_dispatch:  # Allows manual trigger

jobs:
  run-model:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install requests pandas numpy scikit-learn
          # Add any other packages your model needs
      
      # ========================================
      # YOUR EXISTING MODEL STEP (keep as-is)
      # ========================================
      - name: Run prediction model
        run: |
          python your_model_script.py
          # This should create predictions.json
        env:
          # Your existing environment variables
          NBA_API_KEY: ${{ secrets.NBA_API_KEY }}
      
      # ========================================
      # NEW STEP: Upload to Supabase
      # ========================================
      - name: Upload predictions to Supabase
        run: |
          python upload_to_supabase.py predictions.json
        env:
          ORB_PLATFORM_URL: ${{ secrets.ORB_PLATFORM_URL }}
          ORB_PLATFORM_KEY: ${{ secrets.ORB_PLATFORM_KEY }}
      
      # ========================================
      # YOUR EXISTING STEPS (keep as-is)
      # ========================================
      - name: Post to Twitter
        run: |
          python post_to_twitter.py
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
      
      - name: Send email to subscribers
        run: |
          python scripts/send_emails.py
        env:
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
```

## Step 3: Verify Secrets in GitHub

Go to your repository on GitHub:

1. Click **Settings** tab
2. Click **Secrets and variables** → **Actions**
3. Verify these secrets exist:

### Existing Secrets (You Should Already Have):

**ORB_PLATFORM_URL**
- Should contain either:
  - Full URL: `https://skfraijnuefuquyxnced.supabase.co`
  - OR just project ID: `skfraijnuefuquyxnced`
- The script handles both formats automatically!

**ORB_PLATFORM_KEY**
- Should contain your Supabase anon key
- Format: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

✅ **No new secrets needed!** We're using your existing ones.

## Step 4: Copy Upload Script to Your Repo

Copy the `upload_to_supabase.py` file to your GitHub repository's root directory.

```bash
# In your local repo
cp upload_to_supabase.py /path/to/your/NBA-model/
cd /path/to/your/NBA-model/
git add upload_to_supabase.py
git commit -m "Add Supabase upload integration"
git push
```

## Step 5: Test It!

### Option A: Manual Trigger
1. Go to: https://github.com/Lpchaitin/NBA-model/actions
2. Click on your workflow
3. Click **Run workflow** → **Run workflow**
4. Watch the logs for: `✅ Success! Uploaded X predictions`

### Option B: Local Test
```bash
# Set environment variables
export ORB_PLATFORM_URL="your-project-id"
export ORB_PLATFORM_KEY="your-anon-key"

# Run your model (creates predictions.json)
python your_model_script.py

# Test upload
python upload_to_supabase.py predictions.json

# Expected output:
# ✅ Success! Uploaded 3 predictions
```

## Troubleshooting

### Error: "File not found: predictions.json"
- Your model script might save to a different filename
- Update the command to match: `python upload_to_supabase.py your_filename.json`

### Error: "ORB_PLATFORM_URL not set"
- Make sure you added the secrets in GitHub Settings
- Secret names must match exactly (case-sensitive)

### Error: "401 Unauthorized"
- Check that ORB_PLATFORM_KEY is correct
- Get the key from Supabase dashboard → Settings → API

### Error: "Prediction missing required field"
- Your model's output format doesn't match expected format
- Check that your JSON has all required fields:
  - game_id, date, home_team, away_team, pick, spread, 
    ml_probability, implied_probability, edge, confidence

### Error: "Connection timeout"
- Check your internet connection
- Verify ORB_PLATFORM_URL is correct
- Try running manually to test

## Verification Checklist

After running the workflow:

- [ ] GitHub Action shows green checkmark ✅
- [ ] Logs show "✅ Success! Uploaded X predictions"
- [ ] Visit your web app at `/app/todays-picks`
- [ ] Predictions appear on the page
- [ ] Number of predictions matches what was uploaded

## What Happens Next?

Once this is working:

1. **Every day at 9 AM PT:**
   - GitHub Actions runs automatically
   - Model generates predictions
   - **Predictions upload to Supabase** ✅
   - Twitter post
   - Email subscribers

2. **Users visit your site:**
   - See today's picks immediately
   - Live data (not mock data!)
   - Professional presentation

3. **After games complete (optional future enhancement):**
   - Add second workflow to update results
   - Automatically mark predictions as WIN/LOSS
   - Update performance stats

---

## Quick Reference

**Workflow order:**
1. Run model → Creates predictions.json
2. Upload to Supabase → Stores in database
3. Post to Twitter → Social media
4. Send emails → Subscribers

**Files you need:**
- ✅ `upload_to_supabase.py` (create this)
- ✅ `.github/workflows/your_workflow.yml` (modify existing)

**Secrets needed:**
- ✅ `ORB_PLATFORM_URL`
- ✅ `ORB_PLATFORM_KEY`

**Time to implement:** 15 minutes

---

## Need Help?

**Common issues:**

1. **Can't find workflow file?**
   - Look in `.github/workflows/` directory
   - List files: `ls -la .github/workflows/`

2. **Don't know your model's output filename?**
   - Check your model script
   - Look for: `.to_json()` or `json.dump()` or `.to_csv()`

3. **Model outputs CSV not JSON?**
   - Let me know! I'll update the upload script to handle CSV

4. **Need to customize the script?**
   - The script is fully commented and easy to modify
   - Email me or open a GitHub issue

---

**🎯 Next Step:** Add these files to your GitHub repo and test with a manual workflow run!