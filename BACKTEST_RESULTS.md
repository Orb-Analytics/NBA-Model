# 🏀 NBA Model Performance Tracker

**Last Updated:** February 08, 2026

---

## 📊 Overall Performance

**Period:** October 23, 2025 - February 07, 2026  
**Record:** 173-153 (53.07%)  
**Total Games:** 743  
**Games Bet:** 327 (44.0%)  
**ROI:** +4.34%  
**Profit:** $+1416.39

---

## 🎯 System Configuration

**Formula:** `(35% × Averaged Models) + (65% × Implied Odds)`  
**Edge Threshold:** 3.0% minimum  
**Models Used:** Logistic Regression, Linear Regression, Random Forest  
**Feature Selection:** Dynamic (15 features per scenario, re-selected daily)

---

## 📈 Monthly Breakdown

| Month | Record | Win Rate | Games |
|-------|--------|----------|-------|
| **October** | 22-20 | 52.4% | 42 |
| **November** | 60-50 | 54.5% | 110 |
| **December** | 41-34 | 54.7% | 75 |
| **January** | 39-41 | 48.1% | 81 |
| **February** | 11-8 | 57.9% | 19 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 54-60 | 47.0% |
| **Underdogs** | 119-93 | 56.1% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 80-75 | 51.3% | 156 |
| **5-8%** | 61-61 | 50.0% | 122 |
| **8-15%** | 32-17 | 65.3% | 49 |

**Key Insight:** Higher edge correlates with better performance (65.3% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $35,970
- Profit: $+1416.39
- ROI: +4.34%

**Risk-Adjusted Metrics:**
- Pick Rate: 44.0% (filtered 416 games below 3% edge)
- Average Edge: 5.6%
- Max Edge: 12.7%
- Min Edge: 3.0% (by design)

---

## ✅ Validation

**No Lookahead Bias:**
- Features selected dynamically each day
- Only uses data before prediction date
- Models retrained daily on expanding dataset

**Conservative Approach:**
- 3% edge threshold filters weak picks
- 35/65 model/market split prevents overconfidence
- 56.0% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 56.1% win rate on dogs vs 47.0% on favorites
2. **Edge matters:** 65.3% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 48.1% to 57.9%
4. **Pick rate:** Model is selective, betting only 44.0% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (755 games through 2026-02-07)
- `data/averaged_model_backtest.csv` - Full backtest with picks (743 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: February 08, 2026*  
*Auto-updated daily by GitHub Actions*
