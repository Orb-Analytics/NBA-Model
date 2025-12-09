"""
Model Picks History Tracking
Author: Orb Analytics (Liam Chaitin)
Purpose: Track W/L/P results for each model's picks and compute season records
"""

import pandas as pd
import os
from typing import Dict, List, Any
from datetime import datetime


HISTORY_FILE = 'data/model_results/model_picks_history.csv'

HISTORY_COLUMNS = [
    'date',
    'game_id',
    'home_team',
    'away_team',
    'favorite_team',
    'underdog_team',
    'spread',
    'model_name',
    'pick_side',
    'pick_team',
    'pick_line',
    'result'
]


def initialize_history_file():
    """
    Create the model picks history CSV if it doesn't exist.
    """
    os.makedirs('data/model_results', exist_ok=True)
    
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=HISTORY_COLUMNS)
        df.to_csv(HISTORY_FILE, index=False)
        print(f"✅ Created new history file: {HISTORY_FILE}")
    else:
        print(f"✅ History file already exists: {HISTORY_FILE}")


def generate_game_id(date: str, favorite: str, underdog: str) -> str:
    """
    Generate unique game ID.
    
    Example: "2025-11-02_SanAntonioSpurs_NewOrleansPelicans"
    """
    fav_clean = favorite.replace(" ", "")
    dog_clean = underdog.replace(" ", "")
    return f"{date}_{fav_clean}_{dog_clean}"


def record_predictions(predictions: List[Dict[str, Any]]):
    """
    Save today's predictions to history file with result='PENDING'.
    
    Args:
        predictions: List of prediction record dicts from build_prediction_record()
    """
    initialize_history_file()
    
    # Load existing history
    history_df = pd.read_csv(HISTORY_FILE)
    
    new_rows = []
    
    for pred in predictions:
        game_id = generate_game_id(
            pred['date'],
            pred['favorite_team'],
            pred['underdog_team']
        )
        
        # Add a row for each model
        for model_name, model_data in pred['models'].items():
            # Skip if this prediction already exists
            existing = history_df[
                (history_df['game_id'] == game_id) &
                (history_df['model_name'] == model_name)
            ]
            
            if len(existing) > 0:
                print(f"⚠️ Prediction already exists: {game_id} - {model_name}")
                continue
            
            row = {
                'date': pred['date'],
                'game_id': game_id,
                'home_team': pred['home_team'],
                'away_team': pred['away_team'],
                'favorite_team': pred['favorite_team'],
                'underdog_team': pred['underdog_team'],
                'spread': pred['spread'],
                'model_name': model_name,
                'pick_side': model_data['pick_side'],
                'pick_team': model_data['pick_team'] if model_data['pick_team'] else '',
                'pick_line': model_data['pick_line'] if model_data['pick_line'] is not None else '',
                'result': 'PENDING'
            }
            
            new_rows.append(row)
    
    if new_rows:
        # Append to history
        new_df = pd.DataFrame(new_rows)
        updated_df = pd.concat([history_df, new_df], ignore_index=True)
        updated_df.to_csv(HISTORY_FILE, index=False)
        print(f"✅ Recorded {len(new_rows)} new predictions to history")
    else:
        print("⚠️ No new predictions to record")


def update_results(date: str, master_df: pd.DataFrame):
    """
    Update results in history file for a specific date based on actual outcomes.
    
    Args:
        date: Date string (YYYY-MM-DD)
        master_df: DataFrame with master dataset including 'Favorite Cover?' column
    """
    initialize_history_file()
    
    history_df = pd.read_csv(HISTORY_FILE)
    
    # Filter to this date and pending results
    date_predictions = history_df[
        (history_df['date'] == date) &
        (history_df['result'] == 'PENDING')
    ]
    
    if len(date_predictions) == 0:
        print(f"⚠️ No pending predictions found for {date}")
        return
    
    updates_made = 0
    
    for idx, pred_row in date_predictions.iterrows():
        # Find the actual game result
        game_actual = master_df[
            (master_df['Date'] == date) &
            (master_df['Favorite'] == pred_row['favorite_team']) &
            (master_df['Underdog'] == pred_row['underdog_team'])
        ]
        
        if game_actual.empty:
            print(f"⚠️ Game not found in master dataset: {pred_row['game_id']}")
            continue
        
        actual_cover = game_actual.iloc[0]['Favorite Cover?']
        
        if pd.isna(actual_cover):
            print(f"⚠️ Game result not available yet: {pred_row['game_id']}")
            continue
        
        actual_cover = int(actual_cover)
        
        # Determine result based on pick
        if pred_row['pick_side'] == 'NO BET':
            result = 'NO BET'
        else:
            # Check if the pick won
            pick_line = float(pred_row['pick_line'])
            
            # Get actual scores
            fav_score = game_actual.iloc[0].get('Favorite Score', None)
            dog_score = game_actual.iloc[0].get('Underdog Score', None)
            
            if pd.notna(fav_score) and pd.notna(dog_score):
                fav_score = float(fav_score)
                dog_score = float(dog_score)
                score_diff = fav_score - dog_score  # Positive means fav won by more
                
                if pred_row['pick_side'] == 'FAVORITE':
                    # Picked favorite with negative spread (e.g., -9.5)
                    # Favorite needs to win by more than abs(spread)
                    margin_needed = abs(pick_line)
                    
                    if score_diff > margin_needed:
                        result = 'WIN'
                    elif score_diff == margin_needed:
                        result = 'PUSH'
                    else:
                        result = 'LOSS'
                        
                else:  # UNDERDOG
                    # Picked underdog with positive spread (e.g., +9.5)
                    # Underdog needs to lose by less than spread (or win)
                    margin_allowed = pick_line  # Positive number
                    
                    if score_diff < margin_allowed:
                        result = 'WIN'
                    elif score_diff == margin_allowed:
                        result = 'PUSH'
                    else:
                        result = 'LOSS'
            else:
                # Fallback to Favorite Cover? if scores not available
                if pred_row['pick_side'] == 'FAVORITE':
                    result = 'WIN' if actual_cover == 1 else 'LOSS'
                else:
                    result = 'WIN' if actual_cover == 0 else 'LOSS'
        
        # Update the history
        history_df.at[idx, 'result'] = result
        updates_made += 1
    
    if updates_made > 0:
        history_df.to_csv(HISTORY_FILE, index=False)
        print(f"✅ Updated {updates_made} results for {date}")
    else:
        print(f"⚠️ No results updated for {date}")


def get_season_records(end_date: str = None) -> Dict[str, Dict[str, int]]:
    """
    Compute W-L-P records for each model from history file.
    
    Args:
        end_date: Optional cutoff date (YYYY-MM-DD). If None, includes all results.
    
    Returns:
        Dict with model names as keys, values are dicts with 'wins', 'losses', 'pushes'
    """
    initialize_history_file()
    
    history_df = pd.read_csv(HISTORY_FILE)
    
    # Filter out PENDING and NO BET
    history_df = history_df[
        (history_df['result'] != 'PENDING') &
        (history_df['result'] != 'NO BET')
    ]
    
    if end_date:
        history_df = history_df[history_df['date'] < end_date]
    
    records = {}
    
    for model_name in ['Logistic', 'Linear', 'Random Forest', 'Decision Tree']:
        model_df = history_df[history_df['model_name'] == model_name]
        
        wins = (model_df['result'] == 'WIN').sum()
        losses = (model_df['result'] == 'LOSS').sum()
        pushes = (model_df['result'] == 'PUSH').sum()
        
        records[model_name] = {
            'wins': int(wins),
            'losses': int(losses),
            'pushes': int(pushes)
        }
    
    return records


# Example usage and testing
if __name__ == "__main__":
    print("Testing model_history.py functions...")
    
    # Test initialize
    initialize_history_file()
    
    # Test game_id generation
    game_id = generate_game_id("2025-11-02", "San Antonio Spurs", "New Orleans Pelicans")
    print(f"✅ Game ID: {game_id}")
    assert game_id == "2025-11-02_SanAntonioSpurs_NewOrleansPelicans"
    
    # Test get_season_records (should work even with empty file)
    records = get_season_records()
    print(f"✅ Season records: {records}")
    
    print("\n✅ All model_history.py tests passed!")
