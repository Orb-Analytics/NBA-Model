"""
Generate nba_predictions.json and nba_predictions_history.json
"""
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

REPO_ROOT    = Path(__file__).resolve().parent
BACKTEST     = REPO_ROOT / "data" / "averaged_model_backtest.csv"
RESULTS      = REPO_ROOT / "nba_model_results.csv"
TRAINING     = REPO_ROOT / "data" / "NBA Training Set 25-26.csv"
TODAY_OUT    = REPO_ROOT / "nba_predictions.json"
HISTORY_OUT  = REPO_ROOT / "nba_predictions_history.json"

today     = datetime.now(ZoneInfo("America/New_York")).date()
today_fmt = str(today)
now_utc   = datetime.now(ZoneInfo("UTC")).isoformat()

print(f"Date: {today_fmt}")

# Load and merge
df = pd.read_csv(BACKTEST)
training = pd.read_csv(TRAINING, usecols=['Date','Favorite','Underdog','Fav. At Home?'])
training.columns = ['date','favorite','underdog','fav_at_home']
training['date'] = pd.to_datetime(training['date']).dt.strftime('%Y-%m-%d')
df = df.merge(training[['date','favorite','underdog','fav_at_home']], on=['date','favorite','underdog'], how='left')

def get_home_away(row):
    if pd.notna(row.get('fav_at_home')) and row['fav_at_home'] == 1:
        return row['favorite'], row['underdog']
    else:
        return row['underdog'], row['favorite']

# TODAY'S PICKS
df_today = df[
    (df['date'] == today_fmt) &
    (df['pick_side'] != 'NO BET') &
    (df['result'] == 'PENDING')
].copy()

print(f"Today's picks: {len(df_today)}")

picks_today = []
for _, row in df_today.iterrows():
    is_fav    = row['pick_side'] == 'FAVORITE'
    pick_odds = int(row['fav_odds']) if is_fav else int(row['dog_odds'])
    conf      = float(row['averaged_fav_prob']) if is_fav else float(row['averaged_dog_prob'])
    home, away = get_home_away(row)
    picks_today.append({
        "home_team":  home,
        "away_team":  away,
        "pick":       str(row['pick_team']),
        "has_pick":   True,
        "confidence": round(conf, 4) if pd.notna(conf) else None,
        "home_odds":  int(row['fav_odds']) if row.get('fav_at_home') == 1 else int(row['dog_odds']),
        "away_odds":  int(row['dog_odds']) if row.get('fav_at_home') == 1 else int(row['fav_odds']),
        "line":       pick_odds,
        "edge":       round(float(row['edge']), 4),
        "spread":     float(row['spread']),
        "notes":      f"Averaged model edge: +{round(float(row['edge'])*100, 2)}%"
    })

if picks_today:
    with open(TODAY_OUT, 'w') as f:
        json.dump({"model":"NBA","generated_at":now_utc,"version":"v1.0","picks":picks_today}, f, indent=2)
    print(f"✅ nba_predictions.json — {len(picks_today)} picks")
else:
    print("⚠️ No picks today — nba_predictions.json not overwritten")

# HISTORY
df_hist = pd.read_csv(RESULTS, encoding='utf-8-sig')
df_hist['date'] = pd.to_datetime(df_hist['date'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_hist['pick_team'] = df_hist.apply(
    lambda row: row['favorite'] if row['Pick Favorite?'] == 1 else row['underdog'],
    axis=1
)
df_hist['result'] = df_hist['Win?'].map({1: 'WIN', 0: 'LOSS'})
df_hist['pick_side'] = df_hist['Pick Favorite?'].map({1: 'FAVORITE', 0: 'UNDERDOG'})
df_hist['averaged_fav_prob'] = df_hist[
    ['logistic_prob', 'linear_prob', 'rf_prob']
].mean(axis=1)
df_hist['averaged_dog_prob'] = 1 - df_hist['averaged_fav_prob']
df_hist['fav_implied'] = df_hist['fav_odds'].apply(
    lambda odds: 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)
)
df_hist['dog_implied'] = df_hist['dog_odds'].apply(
    lambda odds: 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)
)
df_hist['edge'] = df_hist.apply(
    lambda row: (
        0.35 * row['averaged_fav_prob'] + 0.65 * row['fav_implied'] - row['fav_implied']
        if row['pick_side'] == 'FAVORITE' else
        0.35 * row['averaged_dog_prob'] + 0.65 * row['dog_implied'] - row['dog_implied']
    ),
    axis=1
)
df_hist = df_hist.sort_values('date', ascending=False)

wins   = int((df_hist['result'] == 'WIN').sum())
losses = int((df_hist['result'] == 'LOSS').sum())
total  = wins + losses
win_rate = round(wins / total * 100, 1) if total else 0

def calc_units(row):
    is_fav = row['pick_side'] == 'FAVORITE'
    odds   = row['fav_odds'] if is_fav else row['dog_odds']
    if row['result'] == 'WIN':
        return round((100 / abs(odds)) if odds < 0 else (odds / 100), 2)
    return -1.0

df_hist['units'] = df_hist.apply(calc_units, axis=1)
total_units = round(float(df_hist['units'].sum()), 2)

history_picks = []
for _, row in df_hist.iterrows():
    is_fav    = row['pick_side'] == 'FAVORITE'
    pick_odds = int(row['fav_odds']) if is_fav else int(row['dog_odds'])
    conf      = float(row['averaged_fav_prob']) if is_fav else float(row['averaged_dog_prob'])
    home = row['favorite'] if row['home_favorite'] == 1 else row['underdog']
    away = row['underdog'] if row['home_favorite'] == 1 else row['favorite']
    history_picks.append({
        "date":       row['date'],
        "home_team":  home,
        "away_team":  away,
        "pick":       str(row['pick_team']),
        "confidence": round(conf, 4) if pd.notna(conf) else None,
        "line":       pick_odds,
        "edge":       round(float(row['edge']), 4),
        "spread":     float(row['spread']),
        "result":     row['result'].capitalize(),
        "units":      float(row['units']),
    })

with open(HISTORY_OUT, 'w') as f:
    json.dump({
        "model": "NBA",
        "generated_at": now_utc,
        "version": "v1.0",
        "summary": {
            "wins": wins, "losses": losses,
            "win_rate": win_rate,
            "total_units": total_units,
            "total_picks": total
        },
        "picks": history_picks
    }, f, indent=2)

print(f"✅ nba_predictions_history.json — {total} picks ({wins}W-{losses}L, {win_rate}% win rate, {total_units:+.2f}u)")