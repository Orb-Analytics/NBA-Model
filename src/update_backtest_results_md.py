"""
Update BACKTEST_RESULTS.md with latest backtest statistics.
Run daily after backtest to keep the markdown file current.
"""

import pandas as pd
from datetime import datetime
import os

def update_backtest_results_md():
    """Update BACKTEST_RESULTS.md with current backtest data."""
    
    # Load backtest results
    backtest_file = 'data/averaged_model_backtest.csv'
    if not os.path.exists(backtest_file):
        print(f"❌ Error: {backtest_file} not found")
        return
    
    df = pd.read_csv(backtest_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate overall stats
    picks = df[df['pick_side'] != 'NO BET']
    total_games = len(df)
    total_picks = len(picks)
    no_bets = total_games - total_picks
    
    wins = (picks['result'] == 'WIN').sum()
    losses = (picks['result'] == 'LOSS').sum()
    win_rate = (wins / total_picks * 100) if total_picks > 0 else 0
    
    profit = wins * 109.09 - losses * 110  # Standard -110 odds
    roi = (profit / (total_picks * 110) * 100) if total_picks > 0 else 0
    
    start_date = df['date'].min().strftime('%B %d, %Y')
    end_date = df['date'].max().strftime('%B %d, %Y')
    
    # Calculate monthly breakdown
    df['month'] = df['date'].dt.to_period('M')
    monthly_stats = []
    
    for month in sorted(df['month'].unique()):
        month_df = df[df['month'] == month]
        month_picks = month_df[month_df['pick_side'] != 'NO BET']
        
        if len(month_picks) > 0:
            month_wins = (month_picks['result'] == 'WIN').sum()
            month_losses = (month_picks['result'] == 'LOSS').sum()
            month_wr = month_wins / len(month_picks) * 100
            monthly_stats.append({
                'month': month.strftime('%B'),
                'record': f"{month_wins}-{month_losses}",
                'win_rate': f"{month_wr:.1f}%",
                'games': len(month_picks)
            })
    
    # Performance by pick type
    fav_picks = picks[picks['pick_side'] == 'FAVORITE']
    dog_picks = picks[picks['pick_side'] == 'UNDERDOG']
    
    fav_wins = (fav_picks['result'] == 'WIN').sum()
    fav_losses = (fav_picks['result'] == 'LOSS').sum()
    fav_wr = (fav_wins / len(fav_picks) * 100) if len(fav_picks) > 0 else 0
    
    dog_wins = (dog_picks['result'] == 'WIN').sum()
    dog_losses = (dog_picks['result'] == 'LOSS').sum()
    dog_wr = (dog_wins / len(dog_picks) * 100) if len(dog_picks) > 0 else 0
    
    # Performance by edge
    edge_ranges = [
        (0.03, 0.05, '3-5%'),
        (0.05, 0.08, '5-8%'),
        (0.08, 0.15, '8-15%')
    ]
    
    edge_stats = []
    for min_edge, max_edge, label in edge_ranges:
        range_picks = picks[(picks['edge'] >= min_edge) & (picks['edge'] < max_edge)]
        if len(range_picks) > 0:
            range_wins = (range_picks['result'] == 'WIN').sum()
            range_losses = (range_picks['result'] == 'LOSS').sum()
            range_wr = range_wins / len(range_picks) * 100
            edge_stats.append({
                'range': label,
                'record': f"{range_wins}-{range_losses}",
                'win_rate': f"{range_wr:.1f}%",
                'games': len(range_picks)
            })
    
    # Build the markdown content
    today = datetime.now().strftime('%B %d, %Y')
    
    md_content = f"""# 🏀 NBA Model Performance Tracker

**Last Updated:** {today}

---

## 📊 Overall Performance

**Period:** {start_date} - {end_date}  
**Record:** {wins}-{losses} ({win_rate:.2f}%)  
**Total Games:** {total_games}  
**Games Bet:** {total_picks} ({total_picks/total_games*100:.1f}%)  
**ROI:** {roi:+.2f}%  
**Profit:** ${profit:+.2f}

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
"""
    
    for stat in monthly_stats:
        md_content += f"| **{stat['month']}** | {stat['record']} | {stat['win_rate']} | {stat['games']} |\n"
    
    md_content += f"""
---

## 🎲 Performance by Pick Type

| Pick Type | Record | Win Rate |
|-----------|--------|----------|
| **Favorites** | {fav_wins}-{fav_losses} | {fav_wr:.1f}% |
| **Underdogs** | {dog_wins}-{dog_losses} | {dog_wr:.1f}% |

---

## 📊 Performance by Edge Size

| Edge Range | Record | Win Rate | Games |
|------------|--------|----------|-------|
"""
    
    for stat in edge_stats:
        md_content += f"| **{stat['range']}** | {stat['record']} | {stat['win_rate']} | {stat['games']} |\n"
    
    max_edge = picks['edge'].max() * 100
    avg_edge = picks['edge'].mean() * 100
    
    md_content += f"""
**Key Insight:** Higher edge correlates with better performance ({edge_stats[-1]['win_rate']} at {edge_stats[-1]['range']} edge)

---

## 💰 Betting Performance

**Flat Betting ($100 per pick):**
- Total Wagered: ${total_picks * 110:,}
- Profit: ${profit:+.2f}
- ROI: {roi:+.2f}%

**Risk-Adjusted Metrics:**
- Pick Rate: {total_picks/total_games*100:.1f}% (filtered {no_bets} games below 3% edge)
- Average Edge: {avg_edge:.1f}%
- Max Edge: {max_edge:.1f}%
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
- {no_bets/total_games*100:.1f}% of games filtered as "NO BET"

---

## 🔍 Key Observations

1. **Underdog value:** {dog_wr:.1f}% win rate on dogs vs {fav_wr:.1f}% on favorites
2. **Edge matters:** {edge_stats[-1]['win_rate']} win rate on highest-edge picks ({edge_stats[-1]['range']})
3. **Consistency:** Monthly win rates range from {min([float(s['win_rate'][:-1]) for s in monthly_stats]):.1f}% to {max([float(s['win_rate'][:-1]) for s in monthly_stats]):.1f}%
4. **Pick rate:** Model is selective, betting only {total_picks/total_games*100:.1f}% of games

---

## 📁 Data Files

- `data/unified_model_results.csv` - All 4 model probabilities ({len(pd.read_csv('data/unified_model_results.csv'))} games through {pd.read_csv('data/unified_model_results.csv')['date'].max()})
- `data/averaged_model_backtest.csv` - Full backtest with picks ({total_games} completed games)
- `data/averaged_model_predictions_history.csv` - Permanent archive

---

*Last Generated: {today}*  
*Auto-updated daily by GitHub Actions*
"""
    
    # Write to file
    output_file = 'BACKTEST_RESULTS.md'
    with open(output_file, 'w') as f:
        f.write(md_content)
    
    print(f"✅ Updated {output_file}")
    print(f"   Record: {wins}-{losses} ({win_rate:.2f}%)")
    print(f"   ROI: {roi:+.2f}%")
    print(f"   Period: {start_date} - {end_date}")

if __name__ == '__main__':
    update_backtest_results_md()
