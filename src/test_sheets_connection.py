#!/usr/bin/env python3
"""
Test Google Sheets Connection for Email Subscribers
Purpose: Verify we can read the email signup sheet
"""

import os
import sys
import json

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Google API libraries not installed")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


def test_sheets_connection():
    """Test connection to Google Sheets and read email data."""
    
    print("="*80)
    print("🧪 TESTING GOOGLE SHEETS CONNECTION")
    print("="*80)
    print()
    
    # Get credentials from service account JSON file
    service_account_file = 'service_account.json'
    
    if not os.path.exists(service_account_file):
        print(f"❌ Service account file not found: {service_account_file}")
        print()
        print("To test locally:")
        print("1. Go to GitHub Settings → Secrets → Actions")
        print("2. Copy the SERVICE_ACCOUNT_JSON secret value")
        print("3. Save it to a file named 'service_account.json' in this directory")
        print("   (This file is already in .gitignore)")
        sys.exit(1)
    
    # Get Sheet ID from environment or prompt
    sheet_id = os.environ.get('EMAIL_SUBSCRIBERS_SHEET_ID')
    
    if not sheet_id:
        print("⚠️  EMAIL_SUBSCRIBERS_SHEET_ID not set")
        print()
        sheet_id = input("Enter your Google Sheet ID (from URL): ").strip()
        if not sheet_id:
            print("❌ Sheet ID required")
            sys.exit(1)
    
    print(f"📋 Sheet ID: {sheet_id}")
    print()
    
    # Authenticate
    print("🔐 Authenticating with Google Sheets API...")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=credentials)
        print("   ✅ Authentication successful")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        sys.exit(1)
    print()
    
    # Test reading data
    print("📊 Reading data from sheet...")
    try:
        # Read all data from columns A and B
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='A:B'  # Read columns A (Timestamp) and B (Email)
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("   ⚠️  Sheet is empty or no data found")
            sys.exit(1)
        
        print(f"   ✅ Successfully read {len(values)} rows")
        print()
        
        # Display header row
        print("📋 SHEET STRUCTURE:")
        print("-" * 80)
        if values:
            headers = values[0]
            print(f"Column A: {headers[0] if len(headers) > 0 else '(empty)'}")
            print(f"Column B: {headers[1] if len(headers) > 1 else '(empty)'}")
        print()
        
        # Display first few data rows
        print("📧 SAMPLE DATA (first 5 rows):")
        print("-" * 80)
        
        data_rows = values[1:]  # Skip header
        
        if not data_rows:
            print("   No data rows found (only header)")
        else:
            for i, row in enumerate(data_rows[:5], 1):
                timestamp = row[0] if len(row) > 0 else '(empty)'
                email = row[1] if len(row) > 1 else '(empty)'
                print(f"{i}. Timestamp: {timestamp}")
                print(f"   Email: {email}")
                print()
        
        # Extract and validate emails
        print("="*80)
        print("📧 EMAIL VALIDATION:")
        print("-" * 80)
        
        valid_emails = []
        invalid_rows = []
        
        for i, row in enumerate(data_rows, 2):  # Start at row 2 (after header)
            if len(row) < 2:
                invalid_rows.append((i, "Row too short"))
                continue
            
            email = row[1].strip().lower()
            
            if not email:
                invalid_rows.append((i, "Empty email"))
            elif '@' not in email or '.' not in email:
                invalid_rows.append((i, f"Invalid format: {email}"))
            else:
                valid_emails.append(email)
        
        print(f"✅ Valid emails found: {len(valid_emails)}")
        
        if valid_emails:
            print()
            print("Valid email addresses:")
            for email in valid_emails:
                print(f"   • {email}")
        
        if invalid_rows:
            print()
            print(f"⚠️  Invalid/empty rows: {len(invalid_rows)}")
            for row_num, reason in invalid_rows[:5]:  # Show first 5
                print(f"   Row {row_num}: {reason}")
        
        print()
        print("="*80)
        print("✅ CONNECTION TEST SUCCESSFUL")
        print("="*80)
        print()
        print(f"Summary:")
        print(f"  • Total rows: {len(values)}")
        print(f"  • Data rows: {len(data_rows)}")
        print(f"  • Valid emails: {len(valid_emails)}")
        print(f"  • Issues: {len(invalid_rows)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to read sheet: {e}")
        print()
        print("Common issues:")
        print("  • Sheet not shared with service account email")
        print("  • Wrong Sheet ID")
        print("  • Sheet doesn't exist or is deleted")
        sys.exit(1)


if __name__ == "__main__":
    test_sheets_connection()
