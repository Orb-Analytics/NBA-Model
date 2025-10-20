import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime

# --- Google Sheet details ---
SPREADSHEET_ID = "11L6GRPLvBqZU0TxuYaUuSH8T74elONg_qKWASThF7vI"
SHEET_NAME = "training set"
RANGE_NAME = f"'{SHEET_NAME}'!B2:HW17"   # Header in row 2, data rows 3–17

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

# --- Process data ---
if not values or len(values) < 2:
    print("⚠️ No game data found in the specified range.")
else:
    headers = values[0]
    data_rows = values[1:]
    df = pd.DataFrame(data_rows, columns=headers)
    df = df.dropna(how="all").reset_index(drop=True)

    # --- Create timestamped output filenames ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    timestamped_path = out_dir / f"training_set_{timestamp}.csv"
    latest_path = out_dir / "training_set_latest.csv"

    # --- Save both versions ---
    df.to_csv(timestamped_path, index=False)
    df.to_csv(latest_path, index=False)

    print(f"✅ Saved {len(df)} games to {timestamped_path}")
    print(f"🆕 Latest version also saved to {latest_path}")
