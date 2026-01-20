# 🏀 NBA Model Performance Tracker

**Last Updated:** January 20, 2026

---

## 📊 Overall Performance

**Period:** October 23, 2025 - January 19, 2026  
**Record:** 150-134 (52.82%)  
**Total Games:** 616  
**Games Bet:** 284 (46.1%)  
**ROI:** +3.81%  
**Profit:** $+1083.26

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
| **October** | 25-21 | 54.3% | 46 |
| **November** | 56-54 | 50.9% | 110 |
| **December** | 43-32 | 57.3% | 75 |
| **January** | 26-27 | 49.1% | 53 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 47-55 | 46.1% |
| **Underdogs** | 103-79 | 56.6% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 68-66 | 50.7% | 134 |
| **5-8%** | 58-53 | 52.3% | 111 |
| **8-15%** | 24-15 | 61.5% | 39 |

**Key Insight:** Higher edge correlates with better performance (61.5% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $31,240
- Profit: $+1083.26
- ROI: +3.81%

**Risk-Adjusted Metrics:**
- Pick Rate: 46.1% (filtered 332 games below 3% edge)
- Average Edge: 5.6%
- Max Edge: 12.8%
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
- 53.9% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 56.6% win rate on dogs vs 46.1% on favorites
2. **Edge matters:** 61.5% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 49.1% to 57.3%
4. **Pick rate:** Model is selective, betting only 46.1% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (628 games through 2026-01-19)
- `data/averaged_model_backtest.csv` - Full backtest with picks (616 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: January 20, 2026*  
*Auto-updated daily by GitHub Actions*
