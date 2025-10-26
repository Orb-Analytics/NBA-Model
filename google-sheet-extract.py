import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime

# --- Google Sheet details ---
SPREADSHEET_ID = "11L6GRPLvBqZU0TxuYaUuSH8T74elONg_qKWASThF7vI"
SHEET_NAME = "Training Set"
RANGE_NAME = f"'{SHEET_NAME}'!B2:HW17"  # Header in row 2, data rows 3–17

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
    df_new = pd.DataFrame(data_rows, columns=headers)
    df_new = df_new.dropna(how="all").reset_index(drop=True)

    # --- Paths ---
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    master_path = out_dir / "NBA Training Set 25-26.csv"

    # --- Append to existing dataset if present ---
    if master_path.exists():
        df_master = pd.read_csv(master_path)
        print(f"📂 Loaded existing master dataset with {len(df_master)} rows.")
        combined_df = pd.concat([df_master, df_new], ignore_index=True)
        combined_df.drop_duplicates(inplace=True)
        print(f"🧩 Appended {len(df_new)} new rows (now {len(combined_df)} total).")
    else:
        combined_df = df_new
        print(f"🆕 Created new master dataset with {len(df_new)} rows.")

    # --- Save updated master file ---
    combined_df.to_csv(master_path, index=False)
    print(f"✅ Updated master dataset saved to {master_path}")

    # --- Also save timestamped & latest daily versions ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_path = out_dir / f"training_set_{timestamp}.csv"
    latest_path = out_dir / "training_set_latest.csv"

    df_new.to_csv(timestamped_path, index=False)
    df_new.to_csv(latest_path, index=False)

    print(f"✅ Saved {len(df_new)} new rows to {timestamped_path}")
    print(f"🆕 Latest version also saved to {latest_path}")
