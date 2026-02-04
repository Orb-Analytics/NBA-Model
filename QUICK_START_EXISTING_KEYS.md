# ✅ READY TO GO - Using Your Existing Keys

## 🎯 Perfect! We're Using Your Existing GitHub Secrets

You already have:
- ✅ `ORB_PLATFORM_URL`
- ✅ `ORB_PLATFORM_KEY`

**No new secrets needed!** The upload script now uses these existing credentials.

---

## 📋 Your Quick Setup (10 Minutes)

### 1️⃣ Copy Upload Script to Your Repo (2 min)

```bash
# Copy the script from this project to your NBA-model repo
cp upload_to_supabase.py /path/to/NBA-model/

# Navigate to your repo
cd /path/to/NBA-model/

# Commit and push
git add upload_to_supabase.py
git commit -m "Add Supabase upload integration"
git push
```

### 2️⃣ Update Your GitHub Actions Workflow (5 min)

Find your workflow file (probably `.github/workflows/daily_predictions.yml`)

Add this step **after** your model runs:

```yaml
      # Your existing model step...
      - name: Run prediction model
        run: python your_model_script.py
      
      # ADD THIS NEW STEP:
      - name: Upload predictions to Supabase
        run: python upload_to_supabase.py predictions.json
        env:
          ORB_PLATFORM_URL: ${{ secrets.ORB_PLATFORM_URL }}
          ORB_PLATFORM_KEY: ${{ secrets.ORB_PLATFORM_KEY }}
      
      # Your existing Twitter/email steps...
```

Commit and push:
```bash
git add .github/workflows/your_workflow.yml
git commit -m "Add Supabase upload step"
git push
```

### 3️⃣ Test It! (3 min)

**Option A: Manual Trigger in GitHub**
1. Go to: https://github.com/Lpchaitin/NBA-model/actions
2. Select your workflow
3. Click "Run workflow"
4. Watch for: `✅ Success! Uploaded X predictions`

**Option B: Test Locally First**
```bash
# Set environment variables
export ORB_PLATFORM_URL="skfraijnuefuquyxnced"
export ORB_PLATFORM_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Run your model
python your_model_script.py

# Test upload
python upload_to_supabase.py predictions.json
```

### 4️⃣ Verify on Your Website (1 min)

Visit: Your web app → Today's Picks page
Should see your live predictions! 🎉

---

## 🔧 Script Features

The updated `upload_to_supabase.py` now:

✅ Uses your existing `ORB_PLATFORM_URL` 
✅ Uses your existing `ORB_PLATFORM_KEY`
✅ Handles both URL formats:
   - Full URL: `https://skfraijnuefuquyxnced.supabase.co`
   - Project ID only: `skfraijnuefuquyxnced`
✅ Reads your JSON format: `{"picks": [...]}`
✅ Validates all data before upload
✅ Shows detailed error messages
✅ Production-ready!

---

## 📁 What the Script Expects

Your model should output: `predictions.json`

Format:
```json
{
  "picks": [
    {
      "game_id": "Brooklyn_at_Washington_20260201",
      "date": "2026-02-01",
      "home_team": "Washington",
      "away_team": "Brooklyn",
      "pick": "Washington",
      "spread": 2.5,
      "ml_probability": 0.623,
      "implied_probability": 0.562,
      "edge": 4.01,
      "confidence": "medium"
    }
  ]
}
```

✅ **This matches your existing format!**

---

## 🎬 What Happens When It Runs

```
GitHub Actions triggers
    ↓
Python model generates predictions
    ↓
Saves to predictions.json
    ↓
upload_to_supabase.py reads file
    ↓
Validates data
    ↓
POSTs to Supabase API
    ↓
Supabase stores in database:
  - prediction:2026-02-01:Brooklyn_at_Washington_20260201
  - prediction:2026-02-01:Miami_at_Boston_20260201
  - etc.
    ↓
✅ Success! Predictions visible on website
    ↓
Continue with Twitter/email (your existing workflow)
```

---

## 🔍 How to Verify Your Secrets

Check if you have the right values in GitHub:

1. Go to: https://github.com/Lpchaitin/NBA-model/settings/secrets/actions
2. You should see:
   - `ORB_PLATFORM_URL`
   - `ORB_PLATFORM_KEY`

**Don't have them yet?** Add them:

**ORB_PLATFORM_URL:**
```
skfraijnuefuquyxnced
```
(Or full URL: `https://skfraijnuefuquyxnced.supabase.co`)

**ORB_PLATFORM_KEY:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrZnJhaWpudWVmdXF1eXhuY2VkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwMDE0NzYsImV4cCI6MjA4NTU3NzQ3Nn0.ianRE6Q_94Sa-NyEvd4LasHtncuIn4-Nrf9P6Q2FinE
```

---

## 🐛 Troubleshooting

### "File not found: predictions.json"
→ Your model might save with a different filename
→ Update command: `python upload_to_supabase.py your_file.json`

### "ORB_PLATFORM_URL not set"
→ Check GitHub Settings → Secrets → Actions
→ Verify secrets are added and spelled correctly

### "401 Unauthorized"
→ Wrong ORB_PLATFORM_KEY
→ Get it from Supabase dashboard → Settings → API

### "Connection error"
→ Check ORB_PLATFORM_URL is correct
→ Should be: `skfraijnuefuquyxnced` or full URL

---

## ✅ Success Checklist

After setup, you should see:

- [ ] `upload_to_supabase.py` in your GitHub repo
- [ ] Workflow updated with new upload step
- [ ] GitHub Action runs successfully
- [ ] Logs show: `✅ Success! Uploaded X predictions`
- [ ] Predictions visible on your website
- [ ] No more mock data - all live!

---

## 🚀 That's It!

You're now 10 minutes away from having:
- ✅ Automated daily uploads from GitHub
- ✅ Live predictions on your website
- ✅ No manual work required
- ✅ Everything integrated!

**Start with Step 1 above and you're good to go!** 🎉

---

## 📞 Questions?

Check the detailed docs:
- **GITHUB_WORKFLOW_SETUP.md** - Full setup guide
- **INTEGRATION_SUMMARY.md** - Complete overview
- **DATA_FLOW_DIAGRAM.md** - Visual diagrams

Or just ask me! I'm here to help. 💪
