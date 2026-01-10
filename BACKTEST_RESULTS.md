# 🏀 NBA Model Performance Tracker

**Last Updated:** December 31, 2025

---

## 📊 Overall Performance

**Period:** October 23, 2025 - December 29, 2025  
**Record:** 127-112 (53.14%)  
**Total Games:** 457  
**Games Bet:** 239 (52.3%)  
**ROI:** +5.84%  
**Profit:** $+1534.43

---

## 🎯 System Configuration

**Formula:** `(35% × Averaged Models) + (65% × Implied Odds)`  
**Edge Threshold:** 3.0% minimum  
**Models Used:** Logistic, Linear, Random Forest (3 models averaged)  
**Feature Selection:** Dynamic (15 features per scenario, re-selected daily)

---

## 📈 Monthly Breakdown

| Month | Record | Win Rate | Games |
|-------|--------|----------|-------|
| **October** | 22-20 | 52.4% | 42 |
| **November** | 67-54 | 55.4% | 121 |
| **December** | 38-38 | 50.0% | 76 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 47-48 | 49.5% |
| **Underdogs** | 80-64 | 55.6% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 50-53 | 48.5% | 103 |
| **5-8%** | 50-39 | 56.2% | 89 |
| **8-15%** | 27-20 | 57.4% | 47 |

**Key Insight:** Higher edge correlates with better performance (57.4% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $26,290
- Profit: $+1534.43
- ROI: +5.84%

**Risk-Adjusted Metrics:**
- Pick Rate: 52.3% (filtered 218 games below 3% edge)
- Average Edge: 6.1%
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
- 47.7% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 55.6% win rate on dogs vs 49.5% on favorites
2. **Edge matters:** 57.4% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 50.0% to 55.4%
4. **Pick rate:** Model is selective, betting only 52.3% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (474 games through 2025-12-29)
- `data/averaged_model_backtest.csv` - Full backtest with picks (457 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: December 31, 2025*  
*Auto-updated daily by GitHub Actions*
