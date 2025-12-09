"""
Daily Results Update Script
Author: Orb Analytics (Liam Chaitin)
Purpose: Update model_picks_history.csv with actual results from completed games
"""

import pandas as pd
import argparse
from datetime import datetime, timedelta
from model_history import update_results


def main():
    """Update results for yesterday's predictions."""
    parser = argparse.ArgumentParser(description='Update model picks history with actual results')
    parser.add_argument('--date', type=str, help='Date to update (YYYY-MM-DD), defaults to yesterday')
    
    args = parser.parse_args()
    
    # Determine date (default to yesterday)
    if args.date:
        date = args.date
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date = yesterday.strftime('%Y-%m-%d')
    
    print("="*100)
    print(f"📊 Updating results for {date}")
    print("="*100)
    
    # Load master dataset
    master_path = 'data/NBA Training Set 25-26.csv'
    try:
        master_df = pd.read_csv(master_path)
        master_df['Date'] = pd.to_datetime(master_df['Date']).dt.strftime('%Y-%m-%d')
        print(f"✅ Loaded master dataset: {len(master_df)} games")
    except Exception as e:
        print(f"❌ Failed to load master dataset: {e}")
        return
    
    # Update results
    update_results(date, master_df)
    
    print("="*100)
    print("✅ Update complete!")


if __name__ == "__main__":
    main()
