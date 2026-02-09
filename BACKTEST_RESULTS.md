# 🏀 NBA Model Performance Tracker

**Last Updated:** February 09, 2026

---

## 📊 Overall Performance

**Period:** October 23, 2025 - February 08, 2026  
**Record:** 167-146 (53.35%)  
**Total Games:** 746  
**Games Bet:** 314 (42.1%)  
**ROI:** +4.59%  
**Profit:** $+1438.17

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
| **October** | 19-21 | 47.5% | 40 |
| **November** | 58-44 | 56.9% | 102 |
| **December** | 45-34 | 57.0% | 79 |
| **January** | 35-39 | 46.7% | 75 |
| **February** | 10-8 | 55.6% | 18 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 72-74 | 49.0% |
| **Underdogs** | 95-72 | 56.9% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 84-79 | 51.2% | 164 |
| **5-8%** | 55-50 | 52.4% | 105 |
| **8-15%** | 28-17 | 62.2% | 45 |

**Key Insight:** Higher edge correlates with better performance (62.2% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $34,540
- Profit: $+1438.17
- ROI: +4.59%

**Risk-Adjusted Metrics:**
- Pick Rate: 42.1% (filtered 432 games below 3% edge)
- Average Edge: 5.5%
- Max Edge: 13.8%
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
- 57.9% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 56.9% win rate on dogs vs 49.0% on favorites
2. **Edge matters:** 62.2% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 46.7% to 57.0%
4. **Pick rate:** Model is selective, betting only 42.1% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (758 games through 2026-02-08)
- `data/averaged_model_backtest.csv` - Full backtest with picks (746 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: February 09, 2026*  
*Auto-updated daily by GitHub Actions*
