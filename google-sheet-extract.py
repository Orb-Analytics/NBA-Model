import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime

# --- Google Sheet details ---
SPREADSHEET_ID = "11L6GRPLvBqZU0TxuYaUuSH8T74elONg_qKWASThF7vI"
SHEET_NAME = "Training Set"   # exact case
RANGE_NAME = f"'{SHEET_NAME}'!B3:HW17"   # start at row 3 to skip headers

# --- Authenticate with Service Account ---
creds = service_account.Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

# --- Connect to Sheets API ---
service = build("sheets", "v4", credentials=creds)
result = (
    service.spreadsheets()
    .values()
    .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
    .execute()
)
values = result.get("values", [])

# --- File paths ---
data_path = Path("data") / "NBA Training Set 25-26.csv"
data_path.parent.mkdir(exist_ok=True)

# --- If nothing found ---
if not values:
    print("⚠️ No new data found in the Google Sheet range.")
    exit()

# --- Convert to DataFrame ---
new_data = pd.DataFrame(values)

# --- Load existing master file (if it exists) ---
if data_path.exists():
    existing = pd.read_csv(data_path)
    combined = pd.concat([existing, new_data], ignore_index=True)
    print(f"📈 Existing rows: {len(existing)}, Adding: {len(new_data)} → New total: {len(combined)}")
else:
    combined = new_data
    print(f"🆕 Creating new master file with {len(new_data)} rows.")

# --- Save combined file ---
combined.to_csv(data_path, index=False)
print(f"✅ Updated master training set saved to: {data_path}")

# --- Optional timestamp for logging ---
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"🕒 Run completed at {timestamp}")
