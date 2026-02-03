"""
Upload Restructured Data to Orb Analytics
==========================================
Uploads two properly structured tables:
1. game_outlook - Game data with stats (from NBA Training Set 25-26.csv)
2. model_predictions - Model predictions and outcomes

Usage:
    python src/upload_restructured_data_to_orb.py [--dry-run]
"""

import pandas as pd
import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
ORB_PLATFORM_URL = os.getenv("ORB_PLATFORM_URL")
ORB_PLATFORM_KEY = os.getenv("ORB_PLATFORM_KEY")
DRY_RUN = "--dry-run" in sys.argv

# Only require secrets if not in dry-run mode
if not DRY_RUN and (not ORB_PLATFORM_URL or not ORB_PLATFORM_KEY):
    print("❌ Error: Missing ORB_PLATFORM_URL or ORB_PLATFORM_KEY environment variables")
    sys.exit(1)

# API endpoint
API_URL = f"{ORB_PLATFORM_URL}/predictions"

# Columns to extract from master dataset
GAME_OUTLOOK_COLUMNS = [
    "Date",
    "Favorite",
    "Favorite Score",
    "Underdog",
    "Underdog Score",
    "Spread",
    "Fav. Odds",
    "Dog Odds",
    "Fav. At Home?",
    "Winner",
    "Favorite - Underdog (+/-)",
    "Favorite Cover?",
    "Favorite Win?",
    "Away",
    "Away Score",
    "Home",
    "Home Score",
    "Home/Away +/-"
]


def clean_float(value, default=None):
    """Convert value to float, handling NaN and Infinity."""
    if value is None or value == "" or pd.isna(value):
        return default
    try:
        import math
        f = float(value)
        if not math.isfinite(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def clean_int(value, default=None):
    """Convert value to int, handling NaN."""
    if value is None or value == "" or pd.isna(value):
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def load_game_outlook():
    """Load and prepare game_outlook data from master dataset."""
    print("\n📂 Loading game_outlook data from master dataset...")
    
    df = pd.read_csv("data/NBA Training Set 25-26.csv")
    
    # Filter to games from 2025-10-22 onwards
    df["Date"] = pd.to_datetime(df["Date"])
    cutoff = pd.to_datetime("2025-10-22")
    df = df[df["Date"] >= cutoff].copy()
    
    # Select only required columns
    missing_cols = [col for col in GAME_OUTLOOK_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"⚠️  Warning: Missing columns: {missing_cols}")
    
    available_cols = [col for col in GAME_OUTLOOK_COLUMNS if col in df.columns]
    df = df[available_cols]
    
    # Convert Date to string
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    
    print(f"✅ Loaded {len(df)} games from {df['Date'].min()} to {df['Date'].max()}")
    return df


def load_model_predictions():
    """Load model predictions history."""
    print("\n📂 Loading model_predictions data...")
    
    df = pd.read_csv("data/averaged_model_predictions_history.csv")
    print(f"✅ Loaded {len(df)} predictions")
    
    return df


def transform_game_outlook(df):
    """Transform game_outlook data for upload."""
    print("\n🔄 Transforming game_outlook data...")
    
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            value = row[col]
            
            # Clean numeric columns
            if col in ["Favorite Score", "Underdog Score", "Spread", "Home Score", "Away Score", "Favorite - Underdog (+/-)","Home/Away +/-"]:
                record[col] = clean_float(value)
            elif col in ["Fav. Odds", "Dog Odds"]:
                record[col] = clean_float(value, -110.0)
            elif col == "Fav. At Home?":
                record[col] = clean_int(value, 0)
            else:
                # String columns
                record[col] = str(value) if pd.notna(value) else None
        
        records.append(record)
    
    print(f"✅ Transformed {len(records)} records")
    return records


def transform_model_predictions(df):
    """Transform model predictions data for upload."""
    print("\n🔄 Transforming model_predictions data...")
    
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            value = row[col]
            
            # Handle float columns
            if col in ["spread", "fav_odds", "dog_odds", "logistic_prob", "linear_prob", 
                       "rf_prob", "averaged_fav_prob", "averaged_dog_prob", "standardized_fav",
                       "standardized_dog", "fav_edge", "dog_edge", "edge"]:
                record[col] = clean_float(value)
            elif col == "fav_at_home":
                record[col] = clean_int(value, 0)
            elif col == "num_models":
                record[col] = clean_int(value)
            else:
                # String/other columns
                record[col] = str(value) if pd.notna(value) else None
        
        records.append(record)
    
    print(f"✅ Transformed {len(records)} records")
    return records


def upload_table(table_name, records, dry_run=False):
    """Upload records to a table via API."""
    if not records:
        print(f"⚠️  No records to upload for {table_name}")
        return True
    
    print(f"\n📤 Uploading {table_name} ({len(records)} records)...")
    
    if dry_run:
        print(f"   [DRY RUN] Would upload {len(records)} records")
        print(f"   Sample record: {json.dumps(records[0], indent=2)}")
        return True
    
    # Send as POST request
    payload = {
        "table": table_name,
        "records": records
    }
    
    headers = {
        "Authorization": f"Bearer {ORB_PLATFORM_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Successfully uploaded {table_name}")
            return True
        else:
            print(f"❌ Upload failed ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading {table_name}: {e}")
        return False


def main():
    dry_run = "--dry-run" in sys.argv
    
    print("\n" + "="*60)
    print("🌐 Upload Restructured Data to Orb Analytics")
    print("="*60)
    
    if dry_run:
        print("\n[DRY RUN MODE] - No data will be uploaded")
    
    # Load data
    games_df = load_game_outlook()
    predictions_df = load_model_predictions()
    
    # Transform data
    games_records = transform_game_outlook(games_df)
    predictions_records = transform_model_predictions(predictions_df)
    
    # Upload tables
    games_success = upload_table("game_outlook", games_records, dry_run)
    predictions_success = upload_table("model_predictions", predictions_records, dry_run)
    
    # Summary
    print("\n" + "="*60)
    print("📊 UPLOAD SUMMARY")
    print("="*60)
    print(f"game_outlook: {'✅ Success' if games_success else '❌ Failed'} ({len(games_records)} records)")
    print(f"model_predictions: {'✅ Success' if predictions_success else '❌ Failed'} ({len(predictions_records)} records)")
    
    if not (games_success and predictions_success):
        sys.exit(1)
    
    print("\n✅ All uploads complete!")


if __name__ == "__main__":
    main()
