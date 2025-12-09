"""
Backfill Missing Days from Google Sheets Copies
Author: Orb Analytics (Liam Chaitin)
Purpose: Pull historical Google Sheets exports and run through ETL pipeline
"""

import os
import sys
import json
import argparse
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd


# Google API settings
SCOPES = ['https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/spreadsheets.readonly']

# Expected folder ID where Apps Script saves copies
# TODO: Replace with your actual Google Drive folder ID
DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '')

# Sheet name and range from framework
SHEET_NAME = 'Training Set'
SHEET_RANGE = 'Training Set!B2:HW17'


def get_google_credentials():
    """
    Get Google API credentials from environment variable.
    
    Returns:
        service_account.Credentials object
    """
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if not service_account_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
    
    # Parse JSON from environment
    creds_dict = json.loads(service_account_json)
    
    # Create credentials
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )
    
    return credentials


def find_sheet_for_date(date_str: str):
    """
    Find the Google Sheets copy for a specific date.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
    
    Returns:
        Spreadsheet ID if found, None otherwise
    """
    credentials = get_google_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Build expected file name
    expected_name = f"NBA Statistics Export - Model Export {date_str}"
    
    print(f"🔍 Searching for: {expected_name}")
    
    # Search in the specific folder
    query = f"name='{expected_name}'"
    if DRIVE_FOLDER_ID:
        query += f" and '{DRIVE_FOLDER_ID}' in parents"
    query += " and mimeType='application/vnd.google-apps.spreadsheet'"
    
    try:
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=10
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print(f"❌ No file found with name: {expected_name}")
            return None
        
        if len(files) > 1:
            print(f"⚠️ Multiple files found, using first match")
        
        spreadsheet_id = files[0]['id']
        print(f"✅ Found spreadsheet: {files[0]['name']} (ID: {spreadsheet_id})")
        
        return spreadsheet_id
        
    except Exception as e:
        print(f"❌ Error searching Drive: {e}")
        return None


def read_sheet_data(spreadsheet_id: str):
    """
    Read data from the Training Set sheet.
    
    Args:
        spreadsheet_id: Google Sheets ID
    
    Returns:
        pandas DataFrame with game data
    """
    credentials = get_google_credentials()
    sheets_service = build('sheets', 'v4', credentials=credentials)
    
    print(f"📖 Reading range: {SHEET_RANGE}")
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=SHEET_RANGE
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ No data found in range")
            return None
        
        # First row is headers
        headers = values[0]
        data_rows = values[1:]
        
        # Filter out empty rows (where first few columns are all empty)
        filtered_rows = []
        for row in data_rows:
            # Pad row to match header length
            while len(row) < len(headers):
                row.append('')
            
            # Check if row has data (first 3 columns not all empty)
            if any(row[i].strip() for i in range(min(3, len(row)))):
                filtered_rows.append(row)
        
        print(f"✅ Read {len(filtered_rows)} games from sheet")
        
        # Create DataFrame
        df = pd.DataFrame(filtered_rows, columns=headers)
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")
        return None


def save_raw_csv(df: pd.DataFrame, date_str: str):
    """
    Save data to raw CSV file.
    
    Args:
        df: DataFrame with game data
        date_str: Date string (YYYY-MM-DD)
    
    Returns:
        Path to saved file
    """
    os.makedirs('data/raw', exist_ok=True)
    
    output_path = f"data/raw/NBA_Training_Set_{date_str}.csv"
    
    # Check if file already exists
    if os.path.exists(output_path):
        backup_path = f"{output_path}.backup"
        print(f"⚠️ File exists, creating backup: {backup_path}")
        os.rename(output_path, backup_path)
    
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to: {output_path}")
    
    return output_path


def run_etl_pipeline(date_str: str):
    """
    Run the ETL pipeline to merge raw data into master dataset.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
    """
    print(f"\n🔄 Running ETL pipeline for {date_str}...")
    
    # Import the existing merge functions
    try:
        # These should be the existing scripts that merge data
        from merge_raw_data import merge_raw_data
        from merge_novig_odds import merge_novig_odds
        
        print("📊 Step 1: Merge raw data into master...")
        merge_raw_data(date_str)
        
        print("📊 Step 2: Merge Novig odds...")
        merge_novig_odds(date_str)
        
        print("✅ ETL pipeline complete!")
        
    except ImportError as e:
        print(f"⚠️ Could not import ETL functions: {e}")
        print("⚠️ You may need to manually run the merge scripts:")
        print(f"   python src/merge_raw_data.py --date {date_str}")
        print(f"   python src/merge_novig_odds.py --date {date_str}")


def backfill_date(date_str: str, skip_etl: bool = False):
    """
    Backfill data for a specific date.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        skip_etl: If True, only download sheet without running ETL
    
    Returns:
        True if successful, False otherwise
    """
    print("="*100)
    print(f"📅 BACKFILLING DATA FOR {date_str}")
    print("="*100)
    
    # Validate date format
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"❌ Invalid date format: {date_str} (expected YYYY-MM-DD)")
        return False
    
    # Step 1: Find the sheet
    spreadsheet_id = find_sheet_for_date(date_str)
    if not spreadsheet_id:
        return False
    
    # Step 2: Read data
    df = read_sheet_data(spreadsheet_id)
    if df is None or df.empty:
        return False
    
    # Step 3: Save to raw CSV
    raw_path = save_raw_csv(df, date_str)
    
    # Step 4: Run ETL pipeline (unless skipped)
    if not skip_etl:
        run_etl_pipeline(date_str)
    else:
        print("⚠️ Skipping ETL pipeline (--skip-etl flag)")
    
    print("="*100)
    print(f"✅ BACKFILL COMPLETE FOR {date_str}")
    print("="*100)
    
    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Backfill missing days from Google Sheets copies'
    )
    parser.add_argument('--date', type=str, required=True,
                       help='Date to backfill (YYYY-MM-DD)')
    parser.add_argument('--skip-etl', action='store_true',
                       help='Only download sheet, skip ETL pipeline')
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'):
        print("❌ Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable")
        print("   Set this to your Google service account JSON credentials")
        sys.exit(1)
    
    if not DRIVE_FOLDER_ID and not os.environ.get('GOOGLE_DRIVE_FOLDER_ID'):
        print("⚠️ GOOGLE_DRIVE_FOLDER_ID not set")
        print("   Will search all Drive folders (may be slower)")
    
    # Run backfill
    success = backfill_date(args.date, skip_etl=args.skip_etl)
    
    if success:
        print("\n💡 Next steps:")
        print(f"   1. Verify data in data/raw/NBA_Training_Set_{args.date}.csv")
        print(f"   2. Check master dataset: data/NBA Training Set 25-26.csv")
        print(f"   3. Optionally re-run predictions:")
        print(f"      python src/predict_and_email.py --date {args.date} --no-email")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
