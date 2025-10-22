from pathlib import Path
import requests
import pandas as pd
from dateutil import parser
from datetime import datetime
import pytz
import re
import os
from collections import defaultdict

# === File System Setup ===
eastern = pytz.timezone('US/Eastern')
now_eastern = datetime.now(eastern)
today_str = now_eastern.date().isoformat()

# === File System Setup ===
# Output directory
output_folder = Path("data/novig-odds")
output_folder.mkdir(parents=True, exist_ok=True)
output_file = output_folder / f"novig_nba_spreads_{today_str}.csv"


# === GraphQL Setup ===
url = "https://gql.novig.us/v1/graphql"
query = """
query {
  event(where: {_and: [
      {_or: [
        {status: {_eq: "OPEN_PREGAME"}},
        {status: {_eq: "OPEN_INGAME"}}
      ]},
      {game: {league: {_eq: "NBA"}}}
    ]}) {
    id
    description
    game {
      scheduled_start
    }
    markets {
      description
      updated_at
      is_consensus
      outcomes(where: {_or: [{last: {_is_null: false}}, {available: {_is_null: false}}]}) {
        description
        available
        last
        updated_at
      }
    }
  }
}
"""

# === Helper Functions ===
def price_to_american(price):
    """Convert decimal price to American odds."""
    try:
        if price is None:
            return "N/A"
        price = float(price)
        if price == 0.5:
            return "+100"
        elif price < 0.5:
            odds = (1 / price - 1) * 100
            return f"+{int(round(odds))}"
        else:
            odds = -100 / (1 / price - 1)
            return f"{int(round(odds))}"
    except Exception:
        return "N/A"

def is_fav_home(fav_abbr, home_team_full):
    return fav_abbr.upper() in home_team_full.upper()

# === Data Fetching ===
response = requests.post(url, json={'query': query})
data = response.json()

now_est = now_eastern
today_est = now_eastern.date()
results = []

spread_regex = re.compile(r'([A-Z]{2,3}) ([+-]?\d+\.5)')
one_half_regex = re.compile(r'\b1H\b', re.IGNORECASE)  # identify first-half markets

for event in data['data']['event']:
    desc = event['description']
    if " @ " in desc:
        away_team, home_team = desc.split(" @ ")
    else:
        away_team, home_team = "", ""

    # Convert UTC to Eastern Time
    game_time_utc = parser.parse(event['game']['scheduled_start'])
    game_time_est = game_time_utc.astimezone(eastern)

    # Skip past or non-today games
    if game_time_est.date() != today_est or game_time_est < now_est:
        continue

    for market in event['markets']:
        if not market.get("is_consensus"):
            continue

        market_desc = market.get('description') or ""
        if one_half_regex.search(market_desc):
            continue  # skip 1H markets

        for outcome in market['outcomes']:
            out_desc = outcome.get('description') or ""

            # Skip 1H outcomes
            if one_half_regex.search(out_desc):
                continue

            match = spread_regex.match(out_desc)
            if not match:
                continue

            team = match.group(1)
            line = float(match.group(2))

            market_timestamp = outcome.get('updated_at') or market.get('updated_at') or "N/A"
            try:
                ts = parser.parse(market_timestamp)
            except Exception:
                ts = None

            results.append({
                "event_id": event["id"],
                "teams": desc,
                "away_team": away_team,
                "home_team": home_team,
                "team": team,
                "line": line,
                "spread_line": out_desc,
                "spread_price": outcome.get('available'),
                "game_time_est": game_time_est.isoformat(),
                "market_timestamp": market_timestamp,
                "timestamp_dt": ts,
                "market_desc": market_desc
            })

# === De-dup exact duplicates (keep newest) ===
best_by_key = {}
for r in results:
    key = (r['event_id'], r['team'], r['line'])
    prev = best_by_key.get(key)
    if prev is None:
        best_by_key[key] = r
    else:
        ts, prev_ts = r.get("timestamp_dt"), prev.get("timestamp_dt")
        if (ts and not prev_ts) or (ts and prev_ts and ts > prev_ts):
            best_by_key[key] = r

deduped_results = list(best_by_key.values())

# === Pair up spreads and format output ===
output_rows = []
output = defaultdict(dict)
for r in deduped_results:
    key = (r['teams'], abs(r['line']))
    output[key][r['line']] = r

for (teams, abs_line), spread_pair in output.items():
    fav = spread_pair.get(-abs_line)
    dog = spread_pair.get(abs_line)
    if not fav or not dog:
        continue

    fav_team = fav['team']
    fav_at_home = 1 if is_fav_home(fav_team, fav['home_team']) else 0

    output_rows.append({
        "fav_team": fav_team,
        "dog_team": dog['team'],
        "fav_line": fav['line'],
        "dog_line": dog['line'],
        "fav_price": fav['spread_price'],
        "dog_price": dog['spread_price'],
        "fav_price_american": price_to_american(fav['spread_price']),
        "dog_price_american": price_to_american(dog['spread_price']),
        "home_favorite": fav_at_home,
        "game_time_est": fav['game_time_est'],
        "market": fav['market_desc'],
        "market_timestamp": fav['market_timestamp']
    })

# === Save to CSV ===
df = pd.DataFrame(output_rows)
df.to_csv(output_file, index=False)
print(f"✅ Novig NBA spreads saved to {output_file}")
