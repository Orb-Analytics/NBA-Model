#!/usr/bin/env python3
"""
Regenerate unified_model_results.csv from the master training set
This extracts the model probabilities from model_picks_history and actual outcomes from master dataset
"""

import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')

from ensemble_spread_models import EnsembleSpreadPredictor
from prediction_core import american_to_prob

def regenerate_unified_results(
    master_path='data/NBA Training Set 25-26.csv',
    output_path='data/unified_model_results.csv',
    start_date='2025-10-22',
    end_date=None  # Auto-detect if None
):
    """
    Regenerate unified model results by running all 3 models through each date.
    If end_date is None, uses the latest date with complete game data.
    """
    print("="*100)
    print("🔄 REGENERATING UNIFIED MODEL RESULTS")
    print("="*100)
    
    # Load predictor
    print("📂 Loading ensemble predictor...")
    predictor = EnsembleSpreadPredictor(master_path)
    predictor.load_data(verbose=False)
    master_df = predictor.df.copy()
    master_df['Date'] = pd.to_datetime(master_df['Date'])
    
    # Auto-detect end date if not provided (use latest date with results)
    if end_date is None:
        # Get latest date that has actual results (Favorite Cover? is not null)
        dates_with_results = master_df[master_df['Favorite Cover?'].notna()]['Date']
        if len(dates_with_results) > 0:
            end_date = dates_with_results.max().strftime('%Y-%m-%d')
            print(f"🔍 Auto-detected end date: {end_date}")
        else:
            print("⚠️  No games with results found")
            return None
    
    print(f"📅 Date range: {start_date} to {end_date}")
    print()
    
    # Get all dates in range
    all_dates = master_df[
        (master_df['Date'] >= pd.to_datetime(start_date)) &
        (master_df['Date'] <= pd.to_datetime(end_date))
    ]['Date'].dt.strftime('%Y-%m-%d').unique()
    all_dates = sorted(all_dates)
    
    print(f"🎯 Found {len(all_dates)} dates to process\n")
    
    all_results = []
    
    for i, date_str in enumerate(all_dates, 1):
        print(f"[{i}/{len(all_dates)}] {date_str}...", end=" ")
        
        # Train models on data before this date
        success = predictor.train_models(date_str, verbose=False)
        if not success:
            print("insufficient training data")
            continue
        
        # Get games for this date
        games_today = master_df[master_df['Date'] == pd.to_datetime(date_str)].copy()
        
        if len(games_today) == 0:
            print("no games")
            continue
        
        print(f"{len(games_today)} games")
        
        # Process each game
        for idx, game_row in games_today.iterrows():
            # Get prediction from predictor
            pred = predictor.predict_game(game_row)
            
            if pred is None:
                continue
            
            # Extract data
            favorite = game_row['Favorite']
            underdog = game_row['Underdog']
            spread = game_row['Spread']
            fav_odds = game_row.get('Fav. Odds', -110)
            dog_odds = game_row.get('Dog Odds', -110)
            
            # Get actual outcome
            actual_cover = game_row.get('Favorite Cover?', np.nan)
            
            # Get implied probabilities
            fav_implied = american_to_prob(fav_odds)
            dog_implied = american_to_prob(dog_odds)
            
            # Extract model probabilities (3 models only)
            logistic_fav_prob = pred.get('logistic_probability', np.nan)
            linear_fav_prob = pred.get('linear_probability', np.nan)
            rf_fav_prob = pred.get('random_forest_probability', np.nan)
            
            # Calculate dog probabilities
            logistic_dog_prob = 1 - logistic_fav_prob if not pd.isna(logistic_fav_prob) else np.nan
            linear_dog_prob = 1 - linear_fav_prob if not pd.isna(linear_fav_prob) else np.nan
            rf_dog_prob = 1 - rf_fav_prob if not pd.isna(rf_fav_prob) else np.nan
            
            # Calculate edges
            logistic_fav_edge = logistic_fav_prob - fav_implied if not pd.isna(logistic_fav_prob) else np.nan
            logistic_dog_edge = logistic_dog_prob - dog_implied if not pd.isna(logistic_dog_prob) else np.nan
            linear_fav_edge = linear_fav_prob - fav_implied if not pd.isna(linear_fav_prob) else np.nan
            linear_dog_edge = linear_dog_prob - dog_implied if not pd.isna(linear_dog_prob) else np.nan
            rf_fav_edge = rf_fav_prob - fav_implied if not pd.isna(rf_fav_prob) else np.nan
            rf_dog_edge = rf_dog_prob - dog_implied if not pd.isna(rf_dog_prob) else np.nan
            
            # Determine best edge for each model (pick side with HIGHER edge, not higher absolute value)
            logistic_best_edge = max(abs(logistic_fav_edge), abs(logistic_dog_edge)) if not pd.isna(logistic_fav_edge) else np.nan
            logistic_best_side = 'FAVORITE' if logistic_fav_edge > logistic_dog_edge else 'UNDERDOG'
            logistic_predicted_cover = 1 if logistic_fav_prob > 0.5 else 0
            logistic_correct = logistic_predicted_cover == actual_cover if not pd.isna(actual_cover) else np.nan
            
            linear_best_edge = max(abs(linear_fav_edge), abs(linear_dog_edge)) if not pd.isna(linear_fav_edge) else np.nan
            linear_best_side = 'FAVORITE' if linear_fav_edge > linear_dog_edge else 'UNDERDOG'
            linear_predicted_cover = 1 if linear_fav_prob > 0.5 else 0
            linear_correct = linear_predicted_cover == actual_cover if not pd.isna(actual_cover) else np.nan
            
            rf_best_edge = max(abs(rf_fav_edge), abs(rf_dog_edge)) if not pd.isna(rf_fav_edge) else np.nan
            rf_best_side = 'FAVORITE' if rf_fav_edge > rf_dog_edge else 'UNDERDOG'
            rf_predicted_cover = 1 if rf_fav_prob > 0.5 else 0
            rf_correct = rf_predicted_cover == actual_cover if not pd.isna(actual_cover) else np.nan
            
            # Store result
            result = {
                'date': date_str,
                'favorite': favorite,
                'underdog': underdog,
                'spread': spread,
                'fav_odds': fav_odds,
                'dog_odds': dog_odds,
                'fav_implied_prob': fav_implied,
                'dog_implied_prob': dog_implied,
                'actual_cover': actual_cover,
                'model_type': pred.get('model_type', 'unknown'),
                
                # Logistic
                'logistic_fav_prob': logistic_fav_prob,
                'logistic_dog_prob': logistic_dog_prob,
                'logistic_fav_edge': logistic_fav_edge,
                'logistic_dog_edge': logistic_dog_edge,
                'logistic_best_edge': logistic_best_edge,
                'logistic_best_side': logistic_best_side,
                'logistic_predicted_cover': logistic_predicted_cover,
                'logistic_correct': logistic_correct,
                
                # Linear
                'linear_fav_prob': linear_fav_prob,
                'linear_dog_prob': linear_dog_prob,
                'linear_fav_edge': linear_fav_edge,
                'linear_dog_edge': linear_dog_edge,
                'linear_best_edge': linear_best_edge,
                'linear_best_side': linear_best_side,
                'linear_predicted_cover': linear_predicted_cover,
                'linear_correct': linear_correct,
                
                # Random Forest
                'rf_fav_prob': rf_fav_prob,
                'rf_dog_prob': rf_dog_prob,
                'rf_fav_edge': rf_fav_edge,
                'rf_dog_edge': rf_dog_edge,
                'rf_best_edge': rf_best_edge,
                'rf_best_side': rf_best_side,
                'rf_predicted_cover': rf_predicted_cover,
                'rf_correct': rf_correct,
            }
            
            all_results.append(result)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(all_results)
    
    # Save
    print(f"\n💾 Saving {len(results_df)} game predictions...")
    results_df.to_csv(output_path, index=False)
    print(f"✅ Saved to {output_path}")
    print()
    
    # Show summary
    print("📊 SUMMARY")
    print(f"   Total games: {len(results_df)}")
    print(f"   Date range: {results_df['date'].min()} to {results_df['date'].max()}")
    print(f"   Games with outcomes: {results_df['actual_cover'].notna().sum()}")
    print("="*100)


if __name__ == "__main__":
    regenerate_unified_results()
