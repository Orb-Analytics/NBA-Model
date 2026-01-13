# 🏀 NBA Model Performance Tracker

**Last Updated:** January 13, 2026

---

## 📊 Overall Performance

**Period:** October 23, 2025 - January 12, 2026  
**Record:** 146-130 (52.90%)  
**Total Games:** 568  
**Games Bet:** 279 (49.1%)  
**ROI:** +5.36%  
**Profit:** $+1627.14

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
| **December** | 43-32 | 55.1% | 78 |
| **January** | 22-23 | 48.9% | 45 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 47-53 | 46.1% |
| **Underdogs** | 99-77 | 55.9% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 66-63 | 50.0% | 132 |
| **5-8%** | 56-52 | 51.9% | 108 |
| **8-15%** | 24-15 | 61.5% | 39 |

**Key Insight:** Higher edge correlates with better performance (61.5% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $30,690
- Profit: $+1627.14
- ROI: +5.36%

**Risk-Adjusted Metrics:**
- Pick Rate: 49.1% (filtered 289 games below 3% edge)
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
- 50.9% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 55.9% win rate on dogs vs 46.1% on favorites
2. **Edge matters:** 61.5% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 48.9% to 55.1%
4. **Pick rate:** Model is selective, betting only 49.1% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (580 games through 2026-01-12)
- `data/averaged_model_backtest.csv` - Full backtest with picks (568 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: January 13, 2026*  
*Auto-updated daily by GitHub Actions*
