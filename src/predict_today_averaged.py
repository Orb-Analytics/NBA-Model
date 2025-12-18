#!/usr/bin/env python3
"""
Generate standardized & averaged model predictions for today's games
"""

import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')

from ensemble_spread_models import EnsembleSpreadPredictor
from prediction_core import american_to_prob
from datetime import datetime


def predict_today(date_str=None, min_edge=0.03):
    """
    Generate predictions for a specific date using standardized & averaged approach.
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    print("="*100)
    print(f"🏀 STANDARDIZED & AVERAGED MODEL PREDICTIONS - {date_str}")
    print("="*100)
    print(f"📊 Formula: (35% Averaged Models) + (65% Implied Odds)")
    print(f"📈 Minimum Edge: {min_edge*100:.1f}%")
    print("="*100)
    print()
    
    # Load predictor
    predictor = EnsembleSpreadPredictor('../data/NBA Training Set 25-26.csv')
    predictor.load_data(verbose=False)
    master_df = predictor.df.copy()
    master_df['Date'] = pd.to_datetime(master_df['Date'])
    
    # Train models on all data before today
    print(f"🤖 Training models on data before {date_str}...")
    success = predictor.train_models(date_str, verbose=False)
    
    if not success:
        print(f"❌ Insufficient training data for {date_str}")
        return []
    
    # Get today's games
    games_today = master_df[master_df['Date'] == pd.to_datetime(date_str)].copy()
    
    if len(games_today) == 0:
        print(f"📭 No games scheduled for {date_str}")
        return []
    
    print(f"📊 Found {len(games_today)} games\n")
    print("="*100)
    
    predictions = []
    picks_count = 0
    
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
        
        # Get implied probabilities
        fav_implied = american_to_prob(fav_odds)
        dog_implied = american_to_prob(dog_odds)
        
        # Extract model probabilities
        logistic_prob = pred.get('logistic_probability', np.nan)
        linear_prob = pred.get('linear_probability', np.nan)
        rf_prob = pred.get('random_forest_probability', np.nan)
        tree_prob = pred.get('decision_tree_probability', np.nan)
        
        # Count valid models
        probs = [logistic_prob, linear_prob, rf_prob, tree_prob]
        valid_probs = [p for p in probs if not pd.isna(p)]
        
        if len(valid_probs) == 0:
            continue
        
        # Average model probabilities
        averaged_fav_prob = np.mean(valid_probs)
        averaged_dog_prob = 1 - averaged_fav_prob
        
        # Apply standardization formula
        standardized_fav = (0.35 * averaged_fav_prob) + (0.65 * fav_implied)
        standardized_dog = (0.35 * averaged_dog_prob) + (0.65 * dog_implied)
        
        # Calculate edges
        fav_edge = standardized_fav - fav_implied
        dog_edge = standardized_dog - dog_implied
        
        # Determine pick
        if fav_edge >= min_edge and fav_edge > dog_edge:
            pick_side = "FAVORITE"
            pick_team = favorite
            pick_line = -spread
            edge = fav_edge
            cover_prob = standardized_fav
            has_pick = True
        elif dog_edge >= min_edge and dog_edge > fav_edge:
            pick_side = "UNDERDOG"
            pick_team = underdog
            pick_line = spread
            edge = dog_edge
            cover_prob = standardized_dog
            has_pick = True
        else:
            pick_side = "NO BET"
            pick_team = None
            pick_line = None
            edge = max(fav_edge, dog_edge)
            cover_prob = None
            has_pick = False
        
        prediction = {
            'favorite': favorite,
            'underdog': underdog,
            'spread': spread,
            'fav_odds': fav_odds,
            'dog_odds': dog_odds,
            'fav_implied': fav_implied,
            'dog_implied': dog_implied,
            'averaged_fav_prob': averaged_fav_prob,
            'standardized_fav': standardized_fav,
            'standardized_dog': standardized_dog,
            'fav_edge': fav_edge,
            'dog_edge': dog_edge,
            'pick_side': pick_side,
            'pick_team': pick_team,
            'pick_line': pick_line,
            'edge': edge,
            'cover_prob': cover_prob,
            'num_models': len(valid_probs)
        }
        
        predictions.append(prediction)
        
        # Display
        print(f"\n🏀 {favorite} vs {underdog}")
        print(f"   Spread: {favorite} {spread:+.1f} | Odds: {fav_odds:+.0f} / {dog_odds:+.0f}")
        print(f"   Implied: Fav {fav_implied:.1%} | Dog {dog_implied:.1%}")
        print()
        print(f"   Averaged Model Prob: {averaged_fav_prob:.1%} (fav) | {averaged_dog_prob:.1%} (dog)")
        print(f"   Standardized Prob:   {standardized_fav:.1%} (fav) | {standardized_dog:.1%} (dog)")
        print(f"   Edges:               {fav_edge:+.1%} (fav) | {dog_edge:+.1%} (dog)")
        print()
        
        if has_pick:
            picks_count += 1
            print(f"   ✅ PICK: {pick_team} {pick_line:+.1f}")
            print(f"   📊 Cover Probability: {cover_prob:.1%}")
            print(f"   💰 Edge: {edge:.1%}")
        else:
            print(f"   ⚪ NO BET - Edge below {min_edge*100:.1f}% threshold")
            print(f"      Best edge: {edge:.1%}")
        
        print("-" * 100)
    
    print()
    print("="*100)
    print(f"📊 SUMMARY")
    print(f"   Total Games: {len(predictions)}")
    print(f"   Picks Made: {picks_count}")
    print(f"   No Bets: {len(predictions) - picks_count}")
    print("="*100)
    
    return predictions


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate averaged model predictions for today')
    parser.add_argument('--date', type=str, default=None,
                       help='Date to predict (YYYY-MM-DD, default: today)')
    parser.add_argument('--min-edge', type=float, default=0.03,
                       help='Minimum edge threshold (default: 0.03 = 3%%)')
    
    args = parser.parse_args()
    
    predictions = predict_today(date_str=args.date, min_edge=args.min_edge)
