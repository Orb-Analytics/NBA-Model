# Score Mismatch Bug - Investigation & Fix

## Issue Summary
**Date Discovered:** January 17, 2026  
**Affected Game:** Milwaukee Bucks @ San Antonio Spurs (January 15, 2026)  
**Impact:** Incorrect WIN recorded when it should have been a LOSS

### What Happened
1. **The Bet:** Milwaukee +7.5 (underdog)
2. **Actual Result:** San Antonio won 119-101 (San Antonio covered -7.5)
3. **Expected Outcome:** LOSS (we picked Milwaukee +7.5, they lost by 18)
4. **Recorded Outcome:** WIN ❌ (incorrect)

### Root Cause
The dataset had **swapped home/away designations** for this game:
- **Stored incorrectly:** San Antonio (away) 101 @ Milwaukee (home) 119
- **Actual game:** Milwaukee (away) 101 @ San Antonio (home) 119

When the home/away teams were corrected, the **Favorite Score** and **Underdog Score** columns were not updated to match the new home/away assignments, causing the model to incorrectly think Milwaukee (101) beat San Antonio (119).

### Data Structure
The dataset has multiple representations of the same game:
- `Away` / `Away Score` - Geographic home/away
- `Home` / `Home Score` - Geographic home/away  
- `Favorite` / `Favorite Score` - Betting designation
- `Underdog` / `Underdog Score` - Betting designation
- `Fav. At Home?` - Links the two (1 = favorite is home, 0 = favorite is away)

**Critical Rule:** When `Away`/`Home` are swapped, the corresponding scores must also be updated, AND the `Favorite Score`/`Underdog Score` must be recalculated based on which team is which.

## Investigation Timeline

1. **Verified with ESPN API:** San Antonio won 119-101 at home ✓
2. **Checked dataset:** Found swapped home/away teams ✓
3. **Ran fix_home_away_errors.py:** Corrected home/away teams ✓
4. **Discovered:** Favorite/Underdog scores still wrong ❌
5. **Manual fix:** Corrected the scores for Jan 15 game ✓
6. **Verification scan:** Found 21 total games with score mismatches! ⚠️
7. **Created automated fix:** Fixed all 21 games ✓
8. **Regenerated backtest:** Record updated from 149-131 to 147-133 ✓

## Impact Assessment

### Updated Record (After Fixes)
- **Before:** 149-131 (53.2%)
- **After:** 147-133 (52.5%)
- **Change:** -2 wins, +2 losses
- **ROI:** 3.99% → 3.17%

### Games Affected
- **Jan 15, 2026:** Milwaukee +7.5 (WIN → LOSS)
- **20 historical games** from November-December 2024/2025

The historical games had issues with team name typos (e.g., "Sacremento", "Pheonix", "Okla City") where the wrong team was labeled as favorite/underdog, causing score assignment errors.

## Prevention Measures Implemented

### 1. Score Verification Script
**File:** `src/verify_scores_match_home_away.py`
- Checks that Favorite/Underdog scores match their Home/Away scores
- Runs automatically in daily pipeline
- Returns non-zero exit code if mismatches found

### 2. Automated Fix Script  
**File:** `src/fix_all_score_mismatches.py`
- Automatically corrects any score mismatches
- Recalculates `Favorite Cover?` after fixing
- Logs all changes for review

### 3. Enhanced Home/Away Fix Script
**File:** `src/fix_home_away_errors.py` (updated)
- Now swaps both teams AND scores
- Recalculates all derived columns (Favorite Cover?, margins, etc.)
- Shows score details in output for verification

### 4. Daily Pipeline Integration
**File:** `src/daily_update.py` (updated)
- Step 8 now runs score verification automatically
- If mismatches detected, auto-runs fix script
- Prevents bad data from reaching backtest/predictions

## Usage

### Check for Score Issues
```bash
python src/verify_scores_match_home_away.py
```

### Fix Score Issues
```bash
python src/fix_all_score_mismatches.py
```

### After Any Home/Away Fix
```bash
# 1. Fix home/away designations
python src/fix_home_away_errors.py

# 2. Verify scores are correct
python src/verify_scores_match_home_away.py

# 3. If issues found, auto-fix
python src/fix_all_score_mismatches.py

# 4. Regenerate backtest
python src/daily_backtest_update.py
```

## Key Learnings

1. **Multiple sources of truth are dangerous:** Having both Home/Away AND Favorite/Underdog representations creates sync issues
2. **Computed columns need recalculation:** When fixing data, ALL derived columns must be updated
3. **Verification is essential:** Automated checks prevent silent data corruption
4. **ESPN is the source of truth:** Always verify against external APIs

## Testing Checklist

When making data corrections:
- [ ] Verify with ESPN API or other external source
- [ ] Check home/away assignments
- [ ] Verify scores match home/away correctly
- [ ] Recalculate Favorite Cover? column
- [ ] Run verification script
- [ ] Regenerate backtest
- [ ] Check that win/loss counts make sense
- [ ] Review changed results for reasonableness

## Files Modified

1. `src/fix_home_away_errors.py` - Enhanced to fix scores too
2. `src/verify_scores_match_home_away.py` - New verification tool
3. `src/fix_all_score_mismatches.py` - New automated fix tool
4. `src/daily_update.py` - Added verification step
5. `data/NBA Training Set 25-26.csv` - Fixed 21 games
6. `data/averaged_model_backtest.csv` - Regenerated with correct results
7. `BACKTEST_RESULTS.md` - Updated with correct record

---

**Status:** ✅ RESOLVED  
**Last Verified:** January 17, 2026  
**All Scores Verified Consistent:** ✅
