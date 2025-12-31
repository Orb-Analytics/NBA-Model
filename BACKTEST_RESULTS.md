# 🏀 NBA Model Performance Tracker

**Last Updated:** December 31, 2025

---

## 📊 Overall Performance

**Period:** October 23, 2025 - December 29, 2025  
**Record:** 129-113 (53.31%)  
**Total Games:** 457  
**Games Bet:** 242 (53.0%)  
**ROI:** +6.17%  
**Profit:** $+1642.61

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
| **November** | 66-57 | 53.7% | 123 |
| **December** | 41-36 | 53.2% | 77 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 45-48 | 48.4% |
| **Underdogs** | 84-65 | 56.4% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 49-50 | 49.5% | 99 |
| **5-8%** | 50-42 | 54.3% | 92 |
| **8-15%** | 30-21 | 58.8% | 51 |

**Key Insight:** Higher edge correlates with better performance (58.8% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $26,620
- Profit: $+1642.61
- ROI: +6.17%

**Risk-Adjusted Metrics:**
- Pick Rate: 53.0% (filtered 215 games below 3% edge)
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
- 47.0% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 56.4% win rate on dogs vs 48.4% on favorites
2. **Edge matters:** 58.8% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 52.4% to 53.7%
4. **Pick rate:** Model is selective, betting only 53.0% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (474 games through 2025-12-29)
- `data/averaged_model_backtest.csv` - Full backtest with picks (457 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: December 31, 2025*  
*Auto-updated daily by GitHub Actions*
