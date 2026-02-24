#!/usr/bin/env python3
"""
Generate Supabase CSV with predictions merged with actual scores.
Creates a new CSV file specifically for Supabase sync without modifying existing files.
"""

import pandas as pd
import glob
import os
from pathlib import Path

# Paths
PREDICTIONS_FILE = 'data/averaged_model_backtest.csv'
SCORES_DIR = 'data/yesterdays_scores/'
TRAINING_SET_FILE = 'data/NBA Training Set 25-26.csv'
OUTPUT_FILE = 'data/supabase_predictions.csv'

def load_all_scores():
    """Load all score files and combine them from multiple sources."""
    all_scores = []
    
    # Source 1: yesterdays_scores directory
    score_files = glob.glob(os.path.join(SCORES_DIR, 'nba_scores_*.csv'))
    
    for file in score_files:
        try:
            df = pd.read_csv(file)
            df = df.rename(columns={
                'Date': 'date',
                'Home': 'home_team',
                'Away': 'away_team',
                'Home Score': 'home_score',
                'Away Score': 'away_score'
            })
            all_scores.append(df[['date', 'home_team', 'away_team', 'home_score', 'away_score']])
        except Exception as e:
            print(f"⚠️  Error reading {file}: {e}")
            continue
    
    # Source 2: NBA Training Set (has scores for earlier games)
    if Path(TRAINING_SET_FILE).exists():
        try:
            training_df = pd.read_csv(TRAINING_SET_FILE)
            
            # Extract home/away and scores from training set
            # The training set has "Fav. At Home?", "Home", "Away", "Home Score", "Away Score"
            training_scores = pd.DataFrame({
                'date': training_df['Date'],
                'home_team': training_df['Home'],
                'away_team': training_df['Away'],
                'home_score': training_df['Home Score'],
                'away_score': training_df['Away Score']
            })
            
            all_scores.append(training_scores)
            print(f"✓ Loaded {len(training_scores)} scores from training set")
        except Exception as e:
            print(f"⚠️  Error reading training set: {e}")
    
    if not all_scores:
        print("❌ No score files found")
        return pd.DataFrame()
    
    scores_df = pd.concat(all_scores, ignore_index=True)
    
    # Convert date to datetime
    scores_df['date'] = pd.to_datetime(scores_df['date']).dt.date
    
    # Normalize team names BEFORE removing duplicates (so matching works correctly)
    def normalize_for_scores(name):
        team_map = {
            'LA Clippers': 'La Clippers',
            'L.A. Clippers': 'La Clippers',
            'Golden State': 'Golden St',
            'Oklahoma City': 'Okla City',
        }
        name = str(name).strip()
        return team_map.get(name, name)
    
    scores_df['home_team'] = scores_df['home_team'].apply(normalize_for_scores)
    scores_df['away_team'] = scores_df['away_team'].apply(normalize_for_scores)
    
    # Remove duplicates (prefer later entries)
    scores_df = scores_df.drop_duplicates(subset=['date', 'home_team', 'away_team'], keep='last')
    
    return scores_df

def normalize_team_name(name):
    """Normalize team names to match between datasets."""
    # Map from score file names to prediction file names
    team_map = {
        'LA Clippers': 'La Clippers',
        'L.A. Clippers': 'La Clippers',
        'Golden State': 'Golden St',
        'Oklahoma City': 'Okla City',
    }
    
    name = str(name).strip()
    return team_map.get(name, name)

def merge_predictions_with_scores():
    """Merge predictions with actual game scores."""
    print("=" * 70)
    print("🏀 GENERATING SUPABASE CSV WITH SCORES")
    print("=" * 70)
    
    # Load predictions
    print(f"\n📊 Loading predictions from {PREDICTIONS_FILE}...")
    predictions = pd.read_csv(PREDICTIONS_FILE)
    print(f"✓ Loaded {len(predictions)} predictions")
    
    # Load scores
    print(f"\n📋 Loading scores from {SCORES_DIR}...")
    scores = load_all_scores()
    print(f"✓ Loaded {len(scores)} game scores")
    
    if scores.empty:
        print("❌ No scores available, cannot continue")
        return False
    
    # Scores are already normalized in load_all_scores()
    # Normalize predictions to match (backtest file uses abbreviated names like "Golden St")
    # This is a no-op for most teams but ensures consistency
    predictions['favorite'] = predictions['favorite'].apply(normalize_team_name)
    predictions['underdog'] = predictions['underdog'].apply(normalize_team_name)
    
    # Convert predictions date to date type
    predictions['date'] = pd.to_datetime(predictions['date']).dt.date
    
    # Create a lookup dictionary from scores for fast matching
    scores_lookup = {}
    for _, row in scores.iterrows():
        key = (row['date'], row['home_team'], row['away_team'])
        scores_lookup[key] = (row['home_score'], row['away_score'], row['home_team'], row['away_team'])
    
    # Add home/away and scores to predictions
    def add_scores(row):
        date = row['date']
        fav = row['favorite']
        dog = row['underdog']
        
        # Try favorite at home
        key1 = (date, fav, dog)
        if key1 in scores_lookup:
            score_data = scores_lookup[key1]
            return pd.Series({
                'home_team': score_data[2],
                'away_team': score_data[3],
                'home_score': score_data[0],
                'away_score': score_data[1]
            })
        
        # Try underdog at home
        key2 = (date, dog, fav)
        if key2 in scores_lookup:
            score_data = scores_lookup[key2]
            return pd.Series({
                'home_team': score_data[2],
                'away_team': score_data[3],
                'home_score': score_data[0],
                'away_score': score_data[1]
            })
        
        # No match found
        return pd.Series({
            'home_team': None,
            'away_team': None,
            'home_score': None,
            'away_score': None
        })
    
    # Apply the function to add scores
    score_columns = predictions.apply(add_scores, axis=1)
    merged = pd.concat([predictions, score_columns], axis=1)
    
    # Count matches
    matched = merged['home_score'].notna().sum()
    unmatched = merged['home_score'].isna().sum()
    
    print(f"\n✅ Matched {matched} games with scores")
    if unmatched > 0:
        print(f"⚠️  {unmatched} games without scores")
    
    # Save to new CSV
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"✓ Saved {len(merged)} records")
    
    print("\n" + "=" * 70)
    print("✅ SUPABASE CSV GENERATED SUCCESSFULLY")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    merge_predictions_with_scores()
