#!/usr/bin/env python3
"""
Sync Email Subscribers from Google Sheets
Purpose: Read emails from Google Form responses and maintain subscriber list
"""

import os
import sys
import json

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Google API libraries not installed")
    sys.exit(1)


SUBSCRIBERS_FILE = 'data/email_subscribers.txt'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_google_sheets_client():
    """Authenticate and return Google Sheets API client."""
    service_account_file = 'service_account.json'
    
    if not os.path.exists(service_account_file):
        raise Exception(f"Service account file not found: {service_account_file}")
    
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    return service


def get_emails_from_sheet(service, spreadsheet_id, range_name='A:B'):
    """Read emails from Google Sheet (column B)."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values or len(values) <= 1:
            print("⚠️  No data rows found in sheet")
            return []
        
        # Extract emails from column B (skip header row)
        emails = []
        for i, row in enumerate(values[1:], 2):  # Start at row 2
            if len(row) >= 2:
                email = row[1].strip().lower()
                if email and '@' in email:
                    emails.append(email)
        
        return emails
        
    except Exception as e:
        print(f"❌ Error reading from Google Sheets: {e}")
        raise


def load_existing_subscribers():
    """Load existing subscriber list from file."""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    
    with open(SUBSCRIBERS_FILE, 'r') as f:
        emails = {line.strip().lower() for line in f if line.strip() and '@' in line}
    
    return emails


def save_subscribers(emails):
    """Save subscriber list to file."""
    sorted_emails = sorted(emails)
    
    os.makedirs(os.path.dirname(SUBSCRIBERS_FILE), exist_ok=True)
    
    with open(SUBSCRIBERS_FILE, 'w') as f:
        for email in sorted_emails:
            f.write(f"{email}\n")
    
    print(f"✅ Saved {len(sorted_emails)} subscribers to {SUBSCRIBERS_FILE}")


def sync_subscribers(spreadsheet_id):
    """Main function to sync subscribers from Google Sheets."""
    print("="*80)
    print("📧 SYNCING EMAIL SUBSCRIBERS")
    print("="*80)
    print()
    
    # Load existing subscribers
    print("📂 Loading existing subscribers...")
    existing_emails = load_existing_subscribers()
    print(f"   Found {len(existing_emails)} existing subscribers")
    print()
    
    # Connect to Google Sheets
    print("🔗 Connecting to Google Sheets...")
    try:
        service = get_google_sheets_client()
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        sys.exit(1)
    print()
    
    # Fetch emails from sheet
    print(f"📊 Reading emails from sheet...")
    try:
        sheet_emails = get_emails_from_sheet(service, spreadsheet_id)
        print(f"   Found {len(sheet_emails)} emails in sheet")
    except Exception as e:
        print(f"   ❌ Failed to read sheet: {e}")
        sys.exit(1)
    print()
    
    # Merge and deduplicate
    print("🔄 Merging subscriber lists...")
    all_emails = existing_emails.union(set(sheet_emails))
    new_emails = set(sheet_emails) - existing_emails
    
    if new_emails:
        print(f"   ✨ {len(new_emails)} new subscriber(s):")
        for email in sorted(new_emails):
            print(f"      + {email}")
    else:
        print("   No new subscribers")
    
    print(f"   Total subscribers: {len(all_emails)}")
    print()
    
    # Save updated list
    print("💾 Saving updated subscriber list...")
    save_subscribers(all_emails)
    print()
    
    print("="*80)
    print("✅ SYNC COMPLETE")
    print("="*80)
    
    return len(new_emails), len(all_emails)


def main():
    sheet_id = os.environ.get('EMAIL_SUBSCRIBERS_SHEET_ID')
    
    if not sheet_id:
        print("❌ Error: EMAIL_SUBSCRIBERS_SHEET_ID environment variable not set")
        sys.exit(1)
    
    try:
        new_count, total_count = sync_subscribers(sheet_id)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
