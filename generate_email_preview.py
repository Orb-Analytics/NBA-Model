#!/usr/bin/env python3
"""
Generate HTML Email Preview
"""

import sys
import os
import base64
sys.path.insert(0, 'src')

from predict_and_email_averaged import (
    format_email_html,
    get_yesterday_results,
    get_season_record,
    generate_averaged_predictions
)

# Use Jan 1 data for testing
date_str = '2026-01-01'
yesterday_str = '2025-12-31'

# Get data
yesterday_results, yesterday_units = get_yesterday_results(yesterday_date=yesterday_str)
season_record = get_season_record()
predictions = generate_averaged_predictions(date_str)

# Generate HTML
html_body = format_email_html(predictions, yesterday_results, season_record, date_str)

# Convert cid: references to base64 for preview
with open('Novig_logos/Novig_ad.png', 'rb') as f:
    novig_ad_data = base64.b64encode(f.read()).decode('utf-8')
    html_body = html_body.replace('cid:novig_ad', f'data:image/png;base64,{novig_ad_data}')

with open('Novig_logos/Orb_Novig.png', 'rb') as f:
    orb_novig_data = base64.b64encode(f.read()).decode('utf-8')
    html_body = html_body.replace('cid:orb_novig', f'data:image/png;base64,{orb_novig_data}')

# Save to file
with open('email_preview.html', 'w') as f:
    f.write(html_body)

print("✅ HTML email saved to email_preview.html")
print("   Open this file in a browser to see how it looks!")
print()
print("📧 Email includes:")
print(f"   • Season record: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)")
print(f"   • Yesterday's results: {len(yesterday_results)} picks")
print(f"   • Today's predictions: {len([p for p in predictions if p['pick_side'] != 'NO BET'])} picks")
print()
print("🎨 Features:")
print("   ✓ Team logos embedded inline (Detroit, New Orleans, San Antonio)")
print("   ✓ Color-coded results (green for wins, red for losses)")
print("   ✓ Professional styling with borders and spacing")
print("   ✓ Performance splits section")
print("   ✓ Novig ad section with clickable link")
print("   ✓ Mobile-friendly design")
