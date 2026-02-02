#!/usr/bin/env python3
"""
Upload NBA predictions to Orb Analytics platform.
Reads from averaged_model_predictions_history.csv and POSTs to Supabase API.
"""

import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime


def load_todays_predictions(date_str=None):
    """
    Load today's predictions from the history CSV file.
    
    Args:
        date_str: Date string in 'YYYY-MM-DD' format. If None, uses today's date.
    
    Returns:
        DataFrame with today's predictions
    """
    history_path = 'data/averaged_model_predictions_history.csv'
    
    if not Path(history_path).exists():
        raise FileNotFoundError(
            f"Predictions history file not found: {history_path}\n"
            "Make sure predictions have been generated first."
        )
    
    # Load full history
    df = pd.read_csv(history_path)
    print(f"✓ Loaded {len(df)} total predictions from history")
    
    # Determine target date
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Filter to today's date
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    todays_picks = df[df['date'] == date_str].copy()
    
    if len(todays_picks) == 0:
        print(f"⚠️  No predictions found for {date_str}")
        return pd.DataFrame()
    
    print(f"✓ Found {len(todays_picks)} predictions for {date_str}")
    
    # Only include games where we made a pick (not NO BET)
    picks_only = todays_picks[todays_picks['pick_side'] != 'NO BET'].copy()
    print(f"✓ {len(picks_only)} picks to upload (excluding NO BET games)")
    
    return picks_only


def transform_predictions_for_api(df):
    """
    Transform predictions DataFrame to Orb Analytics API format.
    
    Args:
        df: DataFrame with columns from averaged_model_predictions_history.csv
    
    Returns:
        List of prediction dictionaries in API format
    """
    predictions = []
    
    for _, row in df.iterrows():
        # Generate unique game ID
        date_str = str(row['date']).replace('-', '')
        away_team = str(row['underdog']).replace(' ', '_')
        home_team_str = 'home' if row['fav_at_home'] == 1 else 'away'
        game_id = f"{away_team}_at_{row['favorite'].replace(' ', '_')}_{date_str}"
        
        # Determine home/away teams
        if row['fav_at_home'] == 1:
            home_team = row['favorite']
            away_team = row['underdog']
        else:
            home_team = row['underdog']
            away_team = row['favorite']
        
        # Determine pick team
        pick_team = row['pick_team'] if pd.notna(row['pick_team']) else ''
        
        # Get the edge (already calculated in your data)
        edge = float(row['edge']) * 100  # Convert to percentage
        
        # Map confidence level based on edge
        confidence = map_confidence_level(edge)
        
        prediction = {
            'game_id': game_id,
            'date': row['date'],
            'home_team': home_team,
            'away_team': away_team,
            'pick': pick_team,
            'spread': float(row['spread']),
            'ml_probability': float(row['averaged_fav_prob']),  # Using averaged model prob
            'implied_probability': float(row['standardized_fav']),  # Using standardized prob
            'edge': edge,
            'confidence': confidence
        }
        
        predictions.append(prediction)
    
    print(f"✓ Transformed {len(predictions)} predictions to API format")
    return predictions


def map_confidence_level(edge):
    """
    Map edge percentage to confidence level.
    
    Args:
        edge: Edge as a percentage (e.g., 4.2 for 4.2%)
    
    Returns:
        Confidence level: 'high', 'medium', or 'low'
    """
    if edge >= 5.0:
        return 'high'
    elif edge >= 3.0:
        return 'medium'
    else:
        return 'low'


def post_predictions_to_api(predictions):
    """
    POST predictions to Orb Analytics API.
    
    Args:
        predictions: List of prediction dictionaries
    
    Returns:
        bool: True if successful, False otherwise
    """
    api_url = os.environ.get('ORB_PLATFORM_URL')
    api_key = os.environ.get('ORB_PLATFORM_KEY')
    
    if not api_url:
        raise ValueError(
            "Missing ORB_PLATFORM_URL environment variable.\n"
            "This should be set in your GitHub Secrets."
        )
    
    if not api_key:
        raise ValueError(
            "Missing ORB_PLATFORM_KEY environment variable.\n"
            "This should be set in your GitHub Secrets."
        )
    
    # Use the URL as-is (should include full path to edge function)
    # e.g., https://project.supabase.co/functions/v1/make-server-xxx/predictions
    endpoint = api_url.rstrip('/')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # API expects array directly, not wrapped in object
    payload = predictions
    
    print(f"\n📤 Posting {len(predictions)} predictions to Orb Analytics")
    print(f"   Endpoint: {endpoint}")
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            print(f"✓ Successfully uploaded {len(predictions)} predictions")
            return True
        else:
            print(f"✗ Error uploading predictions:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False


def main():
    """Main execution."""
    print("=" * 70)
    print("🏀 Orb Analytics - Upload NBA Predictions")
    print("=" * 70)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Upload predictions to Orb Analytics')
    parser.add_argument('--date', type=str, help='Date to upload (YYYY-MM-DD, default: today)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be uploaded without actually uploading')
    args = parser.parse_args()
    
    try:
        # Load today's predictions
        df = load_todays_predictions(args.date)
        
        if len(df) == 0:
            print("\n⚠️  No picks to upload for this date")
            print("=" * 70)
            sys.exit(0)
        
        # Transform to API format
        predictions = transform_predictions_for_api(df)
        
        if args.dry_run:
            print("\n🔍 DRY RUN - Would upload:")
            print(json.dumps(predictions, indent=2))
            print("\n✓ Dry run complete - no data uploaded")
        else:
            # Post to API
            success = post_predictions_to_api(predictions)
            
            if success:
                print("\n✅ Upload complete!")
                print("   Predictions are now live on Orb Analytics")
            else:
                print("\n❌ Upload failed!")
                sys.exit(1)
        
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
