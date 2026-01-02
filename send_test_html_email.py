#!/usr/bin/env python3
"""
Test HTML Email with Team Logos
"""

import sys
import os
sys.path.insert(0, 'src')

from predict_and_email_averaged import (
    format_email_html,
    send_email_html,
    get_yesterday_results,
    get_season_record,
    generate_averaged_predictions
)
from datetime import datetime

# Use Jan 1 data for testing (has 1 pick + yesterday's results)
date_str = '2026-01-01'
yesterday_str = '2025-12-31'

print("="*80)
print("🧪 TESTING HTML EMAIL WITH TEAM LOGOS")
print("="*80)
print()

# Get data
print("📊 Loading data...")
yesterday_results, yesterday_units = get_yesterday_results(yesterday_date=yesterday_str)
season_record = get_season_record()
predictions = generate_averaged_predictions(date_str)

print(f"✓ Yesterday results: {len(yesterday_results)} picks")
print(f"✓ Today predictions: {len(predictions)} games")
print(f"✓ Season record: {season_record['wins']}-{season_record['losses']}")
print()

# Generate HTML
print("📝 Generating HTML email...")
html_body = format_email_html(predictions, yesterday_results, season_record, date_str)
print(f"✓ HTML generated ({len(html_body)} chars)")
print()

# Preview first 1000 chars of HTML
print("HTML Preview (first 1000 chars):")
print("-" * 80)
print(html_body[:1000])
print("-" * 80)
print()

# Send test email
print("📧 Sending test HTML email...")
subject = f"🧪 TEST: NBA Predictions HTML - {date_str}"
success = send_email_html(subject, html_body, predictions, yesterday_results)

if success:
    print()
    print("="*80)
    print("✅ SUCCESS! Check your email for the HTML formatted predictions")
    print("   with embedded team logos!")
    print("="*80)
else:
    print()
    print("❌ Failed to send email - check SMTP credentials")
