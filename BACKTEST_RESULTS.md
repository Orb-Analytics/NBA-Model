# 🏀 NBA Model Performance Tracker

**Last Updated:** January 17, 2026

---

## 📊 Overall Performance

**Period:** October 23, 2025 - January 16, 2026  
**Record:** 147-133 (52.50%)  
**Total Games:** 592  
**Games Bet:** 280 (47.3%)  
**ROI:** +3.17%  
**Profit:** $+886.22

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
| **January** | 23-26 | 46.9% | 49 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 47-54 | 46.5% |
| **Underdogs** | 100-79 | 55.9% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 67-65 | 50.8% | 132 |
| **5-8%** | 56-53 | 51.4% | 109 |
| **8-15%** | 24-15 | 61.5% | 39 |

**Key Insight:** Higher edge correlates with better performance (61.5% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $30,800
- Profit: $+886.22
- ROI: +3.17%

**Risk-Adjusted Metrics:**
- Pick Rate: 47.3% (filtered 312 games below 3% edge)
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
- 52.7% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 55.9% win rate on dogs vs 46.5% on favorites
2. **Edge matters:** 61.5% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 46.9% to 57.3%
4. **Pick rate:** Model is selective, betting only 47.3% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (604 games through 2026-01-16)
- `data/averaged_model_backtest.csv` - Full backtest with picks (592 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: January 17, 2026*  
*Auto-updated daily by GitHub Actions*
