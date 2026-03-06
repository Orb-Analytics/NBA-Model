#!/usr/bin/env python3
"""
Generate HTML preview of today's email without sending it.
"""

import sys
import os
sys.path.insert(0, '/workspaces/NBA-model/src')

from predict_and_email_averaged import (
    generate_averaged_predictions,
    get_yesterday_results,
    format_email_html,
    get_season_record
)
from datetime import datetime, timedelta

def main():
    # Get dates
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    print(f"Generating email preview for {today_str}...")
    
    # Load predictions for today
    predictions = generate_averaged_predictions(today_str)
    if predictions is None or len(predictions) == 0:
        print(f"⚠️  No predictions found for {today_str}")
        predictions = []
    
    # Load yesterday's results
    yesterday_results, yesterday_units = get_yesterday_results(yesterday_date=yesterday_str)
    if yesterday_results is None:
        yesterday_results = []
    
    # Calculate season record
    season_record = get_season_record()
    
    # Generate HTML
    html_body = format_email_html(predictions, yesterday_results, season_record, today_str)
    
    # For preview: use relative paths for local images (Substack now uses external CDN)
    html_body = html_body.replace('cid:orb_logo', 'Novig_logos/Orb_logo.png')
    html_body = html_body.replace('cid:novig_ad', 'Novig_logos/novig-5for50-ORB.png')
    
    # Save to file
    output_file = 'email_preview.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_body)
    
    print(f"✅ Preview saved to {output_file}")
    print(f"   - Predictions: {len(predictions)}")
    print(f"   - Yesterday's Results: {len(yesterday_results)}")
    print(f"   - Season Record: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)")
    
    return output_file

if __name__ == "__main__":
    main()
