# 🏀 NBA Model Performance Tracker

**Last Updated:** December 29, 2025

---

## 📊 Overall Performance

**Period:** October 23, 2025 - December 28, 2025  
**Record:** 127-110 (53.59%)  
**Total Games:** 446  
**Games Bet:** 237 (53.1%)  
**ROI:** +6.73%  
**Profit:** $+1754.43

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
| **December** | 39-33 | 54.2% | 72 |

---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | 45-48 | 48.4% |
| **Underdogs** | 82-62 | 56.9% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
| **3-5%** | 48-49 | 49.5% | 97 |
| **5-8%** | 50-42 | 54.3% | 92 |
| **8-15%** | 29-19 | 60.4% | 48 |

**Key Insight:** Higher edge correlates with better performance (60.4% at 8-15% edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: $26,070
- Profit: $+1754.43
- ROI: +6.73%

**Risk-Adjusted Metrics:**
- Pick Rate: 53.1% (filtered 209 games below 3% edge)
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
- 46.9% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** 56.9% win rate on dogs vs 48.4% on favorites
2. **Edge matters:** 60.4% win rate on highest-edge picks (8-15%)
3. **Consistency:** Monthly win rates range from 52.4% to 54.2%
4. **Pick rate:** Model is selective, betting only 53.1% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities (463 games through 2025-12-28)
- `data/averaged_model_backtest.csv` - Full backtest with picks (446 completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: December 29, 2025*  
*Auto-updated daily by GitHub Actions*
