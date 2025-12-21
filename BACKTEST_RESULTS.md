# 🏀 NBA Model Performance Tracker

**Last Updated:** December 21, 2025

---

## 📊 Overall Performance

**Period:** October 23, 2025 - December 18, 2025  
**Record:** 109-96 (52.91%)  
**Total Games:** 375  
**Games Bet:** 206 (54.9%)  
**ROI:** +5.87%  
**Profit:** $+1330.81

---

## 🎯 System Configuration

**Formula:** `(35% × Averaged Models) + (65% × Implied Odds)`  
**Edge Threshold:** 3.0% minimum  
**Models Used:** Logistic, Linear, Random Forest, Decision Tree  
**Feature Selection:** Dynamic (15 features per scenario, re-selected daily)

---

## 📈 Monthly Breakdown

| Month | Record | Win Rate | Games |
|-------|--------|----------|-------|
| **October** | 22-20 | 52.4% | 42 |
| **November** | 67-57 | 54.0% | 124 |
| **December** | 20-19 | 50.0% | 40 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 41-43 | 48.8% |
| **Underdogs** | 68-53 | 55.7% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 35-39 | 46.7% | 75 |
| **5-8%** | 47-39 | 54.7% | 86 |
| **8-15%** | 27-18 | 60.0% | 45 |

**Key Insight:** Higher edge correlates with better performance (60.0% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $22,660
- Profit: $+1330.81
- ROI: +5.87%

**Risk-Adjusted Metrics:**
- Pick Rate: 54.9% (filtered 169 games below 3% edge)
- Average Edge: 6.3%
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
- 45.1% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 55.7% win rate on dogs vs 48.8% on favorites
2. **Edge matters:** 60.0% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 50.0% to 54.0%
4. **Pick rate:** Model is selective, betting only 54.9% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (392 games through 2025-12-19)
- `data/averaged_model_backtest.csv` - Full backtest with picks (375 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: December 21, 2025*  
*Auto-updated daily by GitHub Actions*
