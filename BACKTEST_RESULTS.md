# 🏀 NBA Model Performance Tracker

**Last Updated:** December 21, 2025

---

## 📊 Overall Performance

**Period:** October 23, 2025 - December 20, 2025  
**Record:** 115-99 (53.74%)  
**Total Games:** 390  
**Games Bet:** 214 (54.9%)  
**ROI:** +7.03%  
**Profit:** $+1655.35

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
| **December** | 26-22 | 54.2% | 48 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 42-43 | 49.4% |
| **Underdogs** | 73-56 | 56.6% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 40-41 | 49.4% | 81 |
| **5-8%** | 47-40 | 54.0% | 87 |
| **8-15%** | 28-18 | 60.9% | 46 |

**Key Insight:** Higher edge correlates with better performance (60.9% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $23,540
- Profit: $+1655.35
- ROI: +7.03%

**Risk-Adjusted Metrics:**
- Pick Rate: 54.9% (filtered 176 games below 3% edge)
- Average Edge: 6.2%
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

1. **Underdog value:** 56.6% win rate on dogs vs 49.4% on favorites
2. **Edge matters:** 60.9% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 52.4% to 54.2%
4. **Pick rate:** Model is selective, betting only 54.9% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (402 games through 2025-12-20)
- `data/averaged_model_backtest.csv` - Full backtest with picks (390 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: December 21, 2025*  
*Auto-updated daily by GitHub Actions*
