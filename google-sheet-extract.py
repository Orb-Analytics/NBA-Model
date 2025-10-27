import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime

# --- Google Sheet details ---
SPREADSHEET_ID = "11L6GRPLvBqZU0TxuYaUuSH8T74elONg_qKWASThF7vI"
SHEET_NAME = "Training Set"
RANGE_NAME = f"'{SHEET_NAME}'!B2:HW"  # Start from header row (row 2)

# --- Authenticate with Service Account ---
creds = service_account.Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

# --- Connect to Google Sheets API ---
service = build("sheets", "v4", credentials=creds)
result = (
    service.spreadsheets()
    .values()
    .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
    .execute()
)

values = result.get("values", [])

if not values:
    print("⚠️ No data found in Google Sheet.")
    exit()

# --- Convert to DataFrame ---
headers = values[0]
rows = [
    r for r in values[1:]
    if any(cell.strip() for cell in r if isinstance(cell, str))  # filter out completely blank rows
]

df_new = pd.DataFrame(rows, columns=headers)
df_new = df_new.dropna(how="all").reset_index(drop=True)

# --- Only keep rows with valid Date values ---
if "Date" in df_new.columns:
    df_new = df_new[df_new["Date"].astype(str).str.strip() != ""]
else:
    print("⚠️ No 'Date' column found in sheet.")
    exit()

# --- Path to local master dataset ---
data_path = Path("data") / "NBA Training Set 25-26.csv"
data_path.parent.mkdir(exist_ok=True)

if data_path.exists():
    df_existing = pd.read_csv(data_path, low_memory=False)
else:
    df_existing = pd.DataFrame(columns=df_new.columns)

# --- Align columns between Sheet and existing CSV ---
common_cols = [c for c in df_new.columns if c in df_existing.columns]
if not df_existing.empty:
    df_existing = df_existing[common_cols]
df_new = df_new[common_cols]

# --- Append & deduplicate by Date + Favorite + Underdog ---
combined = pd.concat([df_existing, df_new], ignore_index=True)
before = len(combined)
combined = combined.drop_duplicates(subset=["Date", "Favorite", "Underdog"], keep="first")
after = len(combined)

added_rows = after - len(df_existing)
print(f"📊 Existing: {len(df_existing)} | Added: {added_rows} | Total: {after}")

# --- Save final version ---
combined.to_csv(data_path, index=False)
print(f"✅ Updated master file saved to: {data_path}")
print(f"🕒 Run completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
