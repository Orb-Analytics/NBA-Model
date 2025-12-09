"""
NBA Spread Prediction - Ensemble Consensus Predictions
Author: Orb Analytics (Liam Chaitin)
Purpose: Generate predictions using all 4 models and show consensus
"""

import pandas as pd
import numpy as np
from ensemble_spread_models import EnsembleSpreadPredictor
from datetime import datetime

def american_odds_to_probability(odds):
    """Convert American odds to implied probability."""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)

def predict_today_ensemble(date=None, verbose=True):
    """
    Generate ensemble predictions for today's games.
    Shows predictions from all 4 models + consensus.
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize predictor
    predictor = EnsembleSpreadPredictor('data/NBA Training Set 25-26.csv')
    predictor.load_data(verbose=False)
    
    # Train models on all data before today
    predictor.train_models(date, verbose=False)
    
    # Get today's games
    today_games = predictor.df[predictor.df['Date'] == date].copy()
    
    if len(today_games) == 0:
        print(f"No games scheduled for {date}")
        return
    
    print(f"\n{'='*100}")
    print(f"🏀 NBA SPREAD PREDICTIONS - {date}")
    print(f"{'='*100}\n")
    
    all_predictions = []
    
    for idx, game in today_games.iterrows():
        pred = predictor.predict_game(game)
        
        if not pred:
            continue
        
        # Get odds data for predictive edge
        fav_odds = game.get('Fav. Spread Odds', None)
        dog_odds = game.get('Dog. Spread Odds', None)
        
        # Calculate model probabilities for each model
        model_results = []
        for model_name in ['logistic', 'linear', 'random_forest', 'decision_tree']:
            prob = pred[f'{model_name}_probability']
            prediction = pred[f'{model_name}_prediction']
            
            # Calculate predictive edge if odds available
            if pd.notna(fav_odds):
                market_prob = american_odds_to_probability(fav_odds)
                fav_edge = prob - market_prob
                dog_edge = (1 - prob) - (1 - market_prob)
            else:
                fav_edge = None
                dog_edge = None
            
            model_results.append({
                'model': model_name,
                'probability': prob,
                'prediction': 'COVER' if prediction == 1 else 'NO COVER',
                'fav_edge': fav_edge,
                'dog_edge': dog_edge
            })
        
        # Calculate consensus
        avg_probability = np.mean([r['probability'] for r in model_results])
        votes_cover = sum([1 for r in model_results if r['prediction'] == 'COVER'])
        consensus = 'COVER' if votes_cover >= 3 else 'NO COVER'
        consensus_confidence = max(votes_cover, 4 - votes_cover) / 4
        
        # Print game header
        print(f"📋 {pred['favorite']} ({pred['spread']}) vs {pred['underdog']}")
        print(f"   {'Favorite at Home' if pred['fav_at_home'] == 1 else 'Favorite on Road'}")
        
        if pd.notna(fav_odds) and pd.notna(dog_odds):
            print(f"   Spread Odds: {pred['favorite']} ({fav_odds:+.0f}) | {pred['underdog']} ({dog_odds:+.0f})")
        
        print()
        
        # Print model predictions
        print(f"   {'MODEL':<20} {'PROBABILITY':<15} {'PREDICTION':<12} {'FAV EDGE':<12} {'DOG EDGE'}")
        print(f"   {'-'*80}")
        
        for result in model_results:
            model_display = result['model'].replace('_', ' ').title()
            prob_str = f"{result['probability']*100:.1f}%"
            
            if result['fav_edge'] is not None:
                fav_edge_str = f"{result['fav_edge']*100:+.1f}%" if result['fav_edge'] >= 0 else f"{result['fav_edge']*100:.1f}%"
                dog_edge_str = f"{result['dog_edge']*100:+.1f}%" if result['dog_edge'] >= 0 else f"{result['dog_edge']*100:.1f}%"
            else:
                fav_edge_str = "N/A"
                dog_edge_str = "N/A"
            
            print(f"   {model_display:<20} {prob_str:<15} {result['prediction']:<12} {fav_edge_str:<12} {dog_edge_str}")
        
        print(f"   {'-'*80}")
        print(f"   {'CONSENSUS':<20} {avg_probability*100:.1f}%{'':<8} {consensus:<12} ({votes_cover}/4 models)")
        print(f"   Confidence: {consensus_confidence*100:.0f}%")
        
        # Betting recommendation
        print()
        if pd.notna(fav_odds):
            avg_fav_edge = np.mean([r['fav_edge'] for r in model_results if r['fav_edge'] is not None])
            avg_dog_edge = np.mean([r['dog_edge'] for r in model_results if r['dog_edge'] is not None])
            
            if avg_fav_edge > 0.05 and votes_cover >= 3:
                print(f"   🎯 BEST BET: {pred['favorite']} to cover ({avg_fav_edge*100:+.1f}% edge, {votes_cover}/4 consensus)")
            elif avg_dog_edge > 0.05 and votes_cover <= 1:
                print(f"   🎯 BEST BET: {pred['underdog']} to cover ({avg_dog_edge*100:+.1f}% edge, {4-votes_cover}/4 consensus)")
            elif avg_fav_edge > 0 and avg_dog_edge > 0:
                print(f"   ⚠️  SPLIT: Models disagree, no strong edge")
            else:
                print(f"   ⛔ NO BET: Negative edge on both sides")
        
        print(f"\n{'='*100}\n")
        
        # Store for analysis
        all_predictions.append({
            'date': date,
            'favorite': pred['favorite'],
            'underdog': pred['underdog'],
            'spread': pred['spread'],
            'consensus': consensus,
            'consensus_votes': votes_cover,
            'avg_probability': avg_probability,
            'logistic_prob': model_results[0]['probability'],
            'linear_prob': model_results[1]['probability'],
            'rf_prob': model_results[2]['probability'],
            'tree_prob': model_results[3]['probability']
        })
    
    return all_predictions


def main():
    """Generate today's ensemble predictions."""
    import sys
    
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    predictions = predict_today_ensemble(date)
    
    if predictions:
        print(f"\n✅ Generated {len(predictions)} ensemble predictions for {date}")


if __name__ == "__main__":
    main()
