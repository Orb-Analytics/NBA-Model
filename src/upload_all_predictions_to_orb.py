#!/usr/bin/env python3
"""
Upload ALL NBA predictions history to Orb Analytics platform.
This is a one-time bulk upload script for testing and initial data load.
"""

import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime


def load_all_predictions():
    """
    Load ALL predictions from the history CSV file.
    
    Returns:
        DataFrame with all predictions (excluding NO BET)
    """
    history_path = 'data/averaged_model_predictions_history.csv'
    
    if not Path(history_path).exists():
        raise FileNotFoundError(
            f"Predictions history file not found: {history_path}"
        )
    
    # Load full history
    df = pd.read_csv(history_path)
    print(f"✓ Loaded {len(df)} total predictions from history")
    
    # Only include games where we made a pick (not NO BET)
    picks_only = df[df['pick_side'] != 'NO BET'].copy()
    print(f"✓ {len(picks_only)} picks to upload (excluding {len(df) - len(picks_only)} NO BET games)")
    
    # Show date range
    picks_only['date'] = pd.to_datetime(picks_only['date']).dt.strftime('%Y-%m-%d')
    date_min = picks_only['date'].min()
    date_max = picks_only['date'].max()
    print(f"✓ Date range: {date_min} to {date_max}")
    
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
    
    for idx, row in df.iterrows():
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
        
        # Get result if available
        result = None
        if pd.notna(row.get('result')) and row['result'] in ['WIN', 'LOSS']:
            result = row['result']
        
        prediction = {
            'game_id': game_id,
            'date': row['date'],
            'home_team': home_team,
            'away_team': away_team,
            'pick': pick_team,
            'spread': float(row['spread']),
            'ml_probability': float(row['averaged_fav_prob']),
            'implied_probability': float(row['standardized_fav']),
            'edge': edge,
            'confidence': confidence
        }
        
        # Add result if available
        if result:
            prediction['result'] = result
        
        predictions.append(prediction)
    
    print(f"✓ Transformed {len(predictions)} predictions to API format")
    return predictions


def map_confidence_level(edge):
    """Map edge percentage to confidence level."""
    if edge >= 5.0:
        return 'high'
    elif edge >= 3.0:
        return 'medium'
    else:
        return 'low'


def post_predictions_to_api(predictions, batch_size=50):
    """
    POST predictions to Orb Analytics API in batches.
    
    Args:
        predictions: List of prediction dictionaries
        batch_size: Number of predictions per batch
    
    Returns:
        dict: Summary of upload results
    """
    api_url = os.environ.get('ORB_PLATFORM_URL')
    api_key = os.environ.get('ORB_PLATFORM_KEY')
    
    if not api_url:
        raise ValueError("Missing ORB_PLATFORM_URL environment variable")
    
    if not api_key:
        raise ValueError("Missing ORB_PLATFORM_KEY environment variable")
    
    # Use the URL as-is (should include full path to edge function)
    # e.g., https://project.supabase.co/functions/v1/make-server-xxx/predictions
    endpoint = api_url.rstrip('/')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Split into batches
    total = len(predictions)
    batches = [predictions[i:i + batch_size] for i in range(0, total, batch_size)]
    
    print(f"\n📤 Uploading {total} predictions in {len(batches)} batches of {batch_size}")
    
    results = {
        'total': total,
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    for batch_num, batch in enumerate(batches, 1):
        print(f"\n   Batch {batch_num}/{len(batches)}: {len(batch)} predictions...", end=' ')
        
        # API expects array directly, not wrapped in object
        payload = batch
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✓ Success")
                results['successful'] += len(batch)
            else:
                print(f"✗ Failed (Status {response.status_code})")
                results['failed'] += len(batch)
                results['errors'].append({
                    'batch': batch_num,
                    'status': response.status_code,
                    'response': response.text[:200]
                })
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error: {e}")
            results['failed'] += len(batch)
            results['errors'].append({
                'batch': batch_num,
                'error': str(e)
            })
    
    return results


def main():
    """Main execution."""
    print("=" * 70)
    print("🏀 Orb Analytics - Bulk Upload ALL Predictions History")
    print("=" * 70)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Upload all predictions to Orb Analytics')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be uploaded without uploading')
    parser.add_argument('--batch-size', type=int, default=50, help='Number of predictions per batch (default: 50)')
    parser.add_argument('--limit', type=int, help='Limit number of predictions to upload (for testing)')
    args = parser.parse_args()
    
    try:
        # Load all predictions
        df = load_all_predictions()
        
        if len(df) == 0:
            print("\n⚠️  No picks to upload")
            print("=" * 70)
            sys.exit(0)
        
        # Apply limit if specified
        if args.limit:
            print(f"\n⚠️  Limiting upload to first {args.limit} predictions (--limit flag)")
            df = df.head(args.limit)
        
        # Transform to API format
        predictions = transform_predictions_for_api(df)
        
        if args.dry_run:
            print("\n🔍 DRY RUN - Would upload:")
            print(f"   Total predictions: {len(predictions)}")
            print(f"   First prediction:")
            print(json.dumps(predictions[0], indent=2))
            print(f"\n   Last prediction:")
            print(json.dumps(predictions[-1], indent=2))
            print("\n✓ Dry run complete - no data uploaded")
        else:
            # Confirm before uploading
            print(f"\n⚠️  About to upload {len(predictions)} predictions to Orb Analytics")
            response = input("   Continue? (yes/no): ")
            
            if response.lower() != 'yes':
                print("\n❌ Upload cancelled")
                sys.exit(0)
            
            # Post to API
            results = post_predictions_to_api(predictions, batch_size=args.batch_size)
            
            print("\n" + "=" * 70)
            print("📊 UPLOAD RESULTS")
            print("=" * 70)
            print(f"Total predictions: {results['total']}")
            print(f"✓ Successful: {results['successful']}")
            print(f"✗ Failed: {results['failed']}")
            
            if results['errors']:
                print(f"\n⚠️  Errors encountered:")
                for error in results['errors']:
                    print(f"   Batch {error.get('batch', 'N/A')}: {error}")
            
            if results['successful'] > 0:
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
