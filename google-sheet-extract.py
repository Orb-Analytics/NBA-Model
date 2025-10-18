#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import date

# --- Google Sheet details ---
SPREADSHEET_ID = "11L6GRPLvBqZU0TxuYaUuSH8T74elONg_qKWASThF7vI"
SHEET_NAME = "training set"
RANGE_NAME = f"'{SHEET_NAME}'!B2:HW17"   # Header in row 2, max data rows 3-17

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
    headers = values[0]           # Row 2 in the sheet
    data_rows = values[1:]        # Rows 3–17 (may be fewer)
    df = pd.DataFrame(data_rows, columns=headers)

    # Optional: drop empty rows (in case there are fewer than 15 games)
    df = df.dropna(how="all").reset_index(drop=True)

    # Save to /data folder
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "training_set.csv"
    df.to_csv(out_path, index=False)

    print(f"✅ Saved {len(df)} games to {out_path}")


# In[1]:


import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path

# --- Google Sheet details ---
SPREADSHEET_ID = "11L6GRPLvBqZU0TxuYaUuSH8T74elONg_qKWASThF7vI"
SHEET_NAME = "training set"   # exact sheet tab name
RANGE_NAME = f"'{SHEET_NAME}'!B2:HW17"  # header row = 2, data rows = 3–17

# --- Authenticate with Service Account ---
creds = service_account.Credentials.from_service_account_file(
    "service_account.json",  # make sure this file is in your working directory
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

# --- Connect to Google Sheets API ---
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get("values", [])

# --- Convert to DataFrame and clean ---
if not values or len(values) < 2:
    print("⚠️ No data found in range B2:HW17.")
else:
    headers = values[0]      # row 2 = header row
    data_rows = values[1:]   # rows 3–17 = data rows
    df = pd.DataFrame(data_rows, columns=headers)
    df = df.dropna(how="all").reset_index(drop=True)

    # --- Save locally ---
    out_dir = Path("/workspaces/NBA-model/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "training_set.csv"
    df.to_csv(out_path, index=False)

    print(f"✅ Extracted {len(df)} rows and saved to {out_path}")

