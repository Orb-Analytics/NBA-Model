#!/usr/bin/env python3
"""
Sync NBA Model Data to Supabase for Web App
Syncs predictions, results, and performance stats to Supabase tables.
"""

import os
import sys
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta


def get_supabase_client():
    """Get Supabase connection details."""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_KEY environment variables.\n"
            "Add these to your GitHub Secrets."
        )
    
    # Ensure URL format
    if not url.startswith('http'):
        url = f'https://{url}.supabase.co'
    
    return url.rstrip('/'), key


def load_daily_predictions(date_str=None):
    """Load predictions for a specific date."""
    history_path = 'data/averaged_model_predictions_history.csv'
    
    if not Path(history_path).exists():
        raise FileNotFoundError(f"File not found: {history_path}")
    
    df = pd.read_csv(history_path)
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    todays = df[df['date'] == date_str].copy()
    
    # Only picks (not NO BET)
    picks = todays[todays['pick_side'] != 'NO BET'].copy()
    
    return picks


def load_historical_results():
    """Load all historical predictions with results and scores."""
    # Try to load from supabase_predictions.csv (includes scores)
    supabase_path = 'data/supabase_predictions.csv'
    backtest_path = 'data/averaged_model_backtest.csv'
    
    # Prefer supabase_predictions.csv if it exists (has scores)
    if Path(supabase_path).exists():
        df = pd.read_csv(supabase_path)
        print("✓ Using supabase_predictions.csv (includes scores)")
    elif Path(backtest_path).exists():
        df = pd.read_csv(backtest_path)
        print("⚠️  Using averaged_model_backtest.csv (no scores)")
    else:
        raise FileNotFoundError(f"Neither {supabase_path} nor {backtest_path} found")
    
    # Only completed games with results
    completed = df[
        (df['pick_side'] != 'NO BET') & 
        (df['result'].isin(['WIN', 'LOSS']))
    ].copy()
    
    return completed


def calculate_season_stats():
    """Calculate current season performance statistics."""
    backtest_path = 'data/averaged_model_backtest.csv'
    
    if not Path(backtest_path).exists():
        raise FileNotFoundError(f"File not found: {backtest_path}")
    
    df = pd.read_csv(backtest_path)
    picks = df[df['pick_side'] != 'NO BET'].copy()
    completed = picks[picks['result'].isin(['WIN', 'LOSS'])].copy()
    
    wins = len(completed[completed['result'] == 'WIN'])
    losses = len(completed[completed['result'] == 'LOSS'])
    total = wins + losses
    win_pct = (wins / total * 100) if total > 0 else 0
    
    # Calculate units
    total_units = 0.0
    for _, row in completed.iterrows():
        if row['pick_side'] == 'FAVORITE':
            odds = row.get('fav_odds', -110)
        else:
            odds = row.get('dog_odds', -110)
        
        if row['result'] == 'LOSS':
            total_units -= 1.0
        elif row['result'] == 'WIN':
            if odds < 0:
                total_units += 100 / abs(odds)
            else:
                total_units += odds / 100
    
    # Calculate ROI
    roi = (total_units / total * 100) if total > 0 else 0
    
    # Get date range
    completed['date'] = pd.to_datetime(completed['date'])
    start_date = completed['date'].min().strftime('%Y-%m-%d') if len(completed) > 0 else None
    end_date = completed['date'].max().strftime('%Y-%m-%d') if len(completed) > 0 else None
    
    return {
        'season': '2025-26',
        'wins': int(wins),
        'losses': int(losses),
        'total_games': int(total),
        'win_percentage': round(win_pct, 2),
        'units': round(total_units, 2),
        'roi': round(roi, 2),
        'start_date': start_date,
        'end_date': end_date,
        'last_updated': datetime.now().isoformat()
    }


def format_prediction_record(row, has_home_away=True):
    """Format a single prediction for Supabase (Figma app schema)."""
    # Use home_team and away_team from CSV if available (already matched with scores)
    if 'home_team' in row.index and pd.notna(row.get('home_team')):
        home_team = row['home_team']
        away_team = row['away_team']
    # Fallback: Determine home/away from fav_at_home if available
    elif has_home_away and 'fav_at_home' in row.index and pd.notna(row.get('fav_at_home')):
        if row['fav_at_home'] == 1:
            home_team = row['favorite']
            away_team = row['underdog']
        else:
            home_team = row['underdog']
            away_team = row['favorite']
    else:
        # Last resort: use favorite as home (arbitrary but consistent)
        home_team = row['favorite']
        away_team = row['underdog']
    
    # Get the pick team and spread
    pick_team = row.get('pick_team', '')
    spread_value = float(row['spread'])
    
    # Format pick as "Team ±Spread" (e.g., "Lakers -5.5" or "Warriors +5.5")
    if row['pick_side'] == 'FAVORITE':
        pick = f"{pick_team} {spread_value}"  # Negative spread
    else:
        pick = f"{pick_team} +{abs(spread_value)}"  # Positive spread
    
    # Calculate confidence from edge
    edge_pct = float(row['edge']) * 100
    if edge_pct >= 8.0:
        confidence = 'high'
    elif edge_pct >= 5.0:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    # Get odds for picked side (format as text like "-110")
    if row['pick_side'] == 'FAVORITE':
        odds_value = row.get('fav_odds', -110)
    else:
        odds_value = row.get('dog_odds', -110)
    
    # Format odds as text
    if odds_value < 0:
        odds = f"{int(odds_value)}"
    else:
        odds = f"+{int(odds_value)}"
    
    # Handle NaN values for probability fields
    model_prob = row.get('averaged_fav_prob')
    implied_prob = row.get('standardized_fav')
    
    # Get result (use None instead of 'PENDING' for null)
    result = row.get('result')
    if pd.notna(result) and result in ['WIN', 'LOSS', 'PUSH']:
        result = result.upper()
    else:
        result = None
    
    return {
        # Required columns
        'date': row['date'],
        'home_team': home_team,
        'away_team': away_team,
        'pick': pick,
        'spread': spread_value,
        'edge': round(edge_pct, 2),
        'confidence': confidence,
        'result': result,
        
        # Optional columns (scores)
        'home_score': int(row['home_score']) if pd.notna(row.get('home_score')) else None,
        'away_score': int(row['away_score']) if pd.notna(row.get('away_score')) else None,
        'sport': 'NBA',
        'odds': odds,
        'ml_probability': round(float(model_prob) * 100, 2) if pd.notna(model_prob) else None,
        'implied_probability': round(float(implied_prob) * 100, 2) if pd.notna(implied_prob) else None
    }


def upsert_to_supabase(table_name, records, url, key):
    """Upsert records to Supabase table using REST API."""
    endpoint = f"{url}/rest/v1/{table_name}"
    
    # Determine unique columns for upsert
    if table_name == 'predictions':
        on_conflict = 'date,home_team,away_team'
    elif table_name == 'season_stats':
        on_conflict = 'season'
    else:
        on_conflict = ''
    
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal'
    }
    
    print(f"\n📤 Upserting {len(records)} records to '{table_name}' table...")
    
    try:
        # Use upsert with on_conflict parameter
        upsert_url = f"{endpoint}?on_conflict={on_conflict}" if on_conflict else endpoint
        response = requests.post(upsert_url, headers=headers, json=records, timeout=30)
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ Successfully synced to '{table_name}'")
            return True
        else:
            print(f"❌ Error syncing to '{table_name}':")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False


def sync_daily_predictions(date_str=None, dry_run=False):
    """Sync today's predictions to Supabase."""
    print("\n" + "="*70)
    print("📊 SYNCING DAILY PREDICTIONS")
    print("="*70)
    
    df = load_daily_predictions(date_str)
    
    if len(df) == 0:
        print("⚠️  No picks found for this date")
        return True
    
    print(f"✓ Loaded {len(df)} picks")
    
    # Format records (predictions_history has fav_at_home)
    records = [format_prediction_record(row, has_home_away=True) for _, row in df.iterrows()]
    
    if dry_run:
        print("\n🔍 DRY RUN - Would sync:")
        print(json.dumps(records[:2], indent=2))
        print(f"... and {len(records)-2} more" if len(records) > 2 else "")
        return True
    
    # Sync to Supabase
    url, key = get_supabase_client()
    return upsert_to_supabase('predictions', records, url, key)


def sync_historical_results(limit=None, dry_run=False):
    """Sync historical predictions with results to Supabase."""
    print("\n" + "="*70)
    print("📜 SYNCING HISTORICAL RESULTS")
    print("="*70)
    
    df = load_historical_results()
    
    if limit:
        df = df.tail(limit)
    
    print(f"✓ Loaded {len(df)} completed games")
    
    # Filter to only games with scores (if home_team column exists in CSV)
    if 'home_team' in df.columns:
        initial_count = len(df)
        df = df[df['home_score'].notna() & df['away_score'].notna()]
        filtered_count = initial_count - len(df)
        if filtered_count > 0:
            print(f"⚠️  Filtered out {filtered_count} games without scores")
        print(f"✓ {len(df)} games with complete scores")
    
    # Format records (use has_home_away=True for supabase_predictions.csv)
    records = [format_prediction_record(row, has_home_away=True) for _, row in df.iterrows()]
    
    # Additional validation: remove any records with null scores
    records_with_scores = [r for r in records if r['home_score'] is not None and r['away_score'] is not None]
    if len(records_with_scores) < len(records):
        print(f"⚠️  Removed {len(records) - len(records_with_scores)} records with missing scores after formatting")
        records = records_with_scores
    
    if dry_run:
        print("\n🔍 DRY RUN - Would sync:")
        print(json.dumps(records[:2], indent=2))
        print(f"... and {len(records)-2} more" if len(records) > 2 else "")
        return True
    
    # Sync to Supabase
    url, key = get_supabase_client()
    return upsert_to_supabase('predictions', records, url, key)


def sync_season_stats(dry_run=False):
    """Sync season performance statistics to Supabase."""
    print("\n" + "="*70)
    print("📈 SYNCING SEASON STATS")
    print("="*70)
    
    stats = calculate_season_stats()
    
    print(f"✓ Record: {stats['wins']}-{stats['losses']} ({stats['win_percentage']}%)")
    print(f"✓ Units: {stats['units']:+.1f}u (ROI: {stats['roi']:+.1f}%)")
    
    if dry_run:
        print("\n🔍 DRY RUN - Would sync:")
        print(json.dumps(stats, indent=2))
        return True
    
    # Sync to Supabase
    url, key = get_supabase_client()
    return upsert_to_supabase('season_stats', [stats], url, key)


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync NBA data to Supabase')
    parser.add_argument('--mode', choices=['daily', 'historical', 'stats', 'all'], 
                       default='all', help='What to sync')
    parser.add_argument('--date', type=str, help='Date for daily sync (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, help='Limit historical records (for testing)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without syncing')
    args = parser.parse_args()
    
    print("="*70)
    print("🏀 SUPABASE SYNC - NBA PREDICTION MODEL")
    print("="*70)
    
    try:
        success = True
        
        if args.mode in ['daily', 'all']:
            if not sync_daily_predictions(args.date, args.dry_run):
                success = False
        
        if args.mode in ['historical', 'all']:
            if not sync_historical_results(args.limit, args.dry_run):
                success = False
        
        if args.mode in ['stats', 'all']:
            if not sync_season_stats(args.dry_run):
                success = False
        
        print("\n" + "="*70)
        if success:
            print("✅ SYNC COMPLETE")
        else:
            print("⚠️  SYNC COMPLETED WITH ERRORS")
        print("="*70)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
