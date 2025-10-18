import requests
import pandas as pd
from dateutil import parser
from datetime import datetime
import pytz
import os

# Setup
eastern = pytz.timezone('US/Eastern')
now_eastern = datetime.now(eastern)
today_str = now_eastern.date().isoformat()

output_folder = "/workspaces/NBA-model/data/novig-odds"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, f"novig_nba_ml_{today_str}.csv")

# GraphQL query for NBA
url = "https://gql.novig.us/v1/graphql"
query = """
query {
  event(where: {
    _and: [
      {game: {league: {_eq: "NBA"}}},
      {_or: [
        {status: {_eq: "OPEN_PREGAME"}},
        {status: {_eq: "OPEN_INGAME"}}
      ]}
    ]
  }) {
    id
    description
    game { scheduled_start }
    markets {
      description
      is_consensus
      outcomes {
        description
        available
        last
      }
    }
  }
}
"""

response = requests.post(url, json={"query": query})
data = response.json()

results = []
for ev in data.get("data", {}).get("event", []):
    desc = ev["description"]
    scheduled = parser.parse(ev["game"]["scheduled_start"]).astimezone(eastern).isoformat()
    for m in ev["markets"]:
        if not m.get("is_consensus") and all(o.get("available") is None for o in m.get("outcomes", [])):
            # skip markets with no available price and not consensus
            continue
        # Focus on moneyline style markets — e.g., description matches a team name
        if "@" in desc and m["description"].strip().split()[0] in desc.split(" @ "):
            for o in m["outcomes"]:
                results.append({
                    "event_id": ev["id"],
                    "teams": desc,
                    "market": m["description"],
                    "outcome": o["description"],
                    "available": o.get("available"),
                    "last": o.get("last"),
                    "scheduled_start": scheduled
                })

df = pd.DataFrame(results)
df.to_csv(output_file, index=False)
print(f"✅ Novig NBA moneyline (or available) markets saved to {output_file} — {len(df)} rows")
