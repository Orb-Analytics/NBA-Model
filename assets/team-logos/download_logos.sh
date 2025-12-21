#!/bin/bash
# Download all 30 NBA team logos from ESPN CDN

teams=(
    "atl" "bos" "bkn" "cha" "chi" "cle" "dal" "den" "det" "gs"
    "hou" "ind" "lac" "lal" "mem" "mia" "mil" "min" "no" "ny"
    "okc" "orl" "phi" "phx" "por" "sac" "sa" "tor" "uta" "wsh"
)

for team in "${teams[@]}"; do
    echo "Downloading $team..."
    curl -s "https://a.espncdn.com/i/teamlogos/nba/500/$team.png" -o "$team.png"
done

echo "✅ Downloaded ${#teams[@]} team logos"
