"""
Calculate Predictive Edge for NBA Spread Predictions
Author: Orb Analytics (Liam Chaitin)
Purpose: Calculate predictive edge by comparing model probabilities to implied odds probabilities
         Predictive Edge = Model Probability - Implied Probability from Odds
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys

def american_odds_to_probability(odds):
    """
    Convert American odds to implied probability.
    
    For negative odds (e.g., -110): probability = |odds| / (|odds| + 100)
    For positive odds (e.g., +110): probability = 100 / (odds + 100)
    """
    if pd.isna(odds):
        return None
    
    odds = float(odds)
    
    if odds < 0:
        # Negative odds (favorite)
        return abs(odds) / (abs(odds) + 100)
    else:
        # Positive odds (underdog)
        return 100 / (odds + 100)

def calculate_predictive_edges(training_file='data/NBA Training Set 25-26.csv', 
                               predictions_file='data/daily_predictions_results.csv',
                               output_file='data/predictive_edges.csv',
                               season_start='2025-10-22'):
    """
    Calculate predictive edges for completed games this season.
    """
    
    # Load data
    print("📂 Loading data...")
    df_training = pd.read_csv(training_file)
    df_predictions = pd.read_csv(predictions_file)
    
    # Filter for current season
    df_training['Date'] = pd.to_datetime(df_training['Date'])
    season_start_dt = pd.to_datetime(season_start)
    df_season = df_training[df_training['Date'] >= season_start_dt].copy()
    
    # Filter for completed games (have scores)
    df_completed = df_season.dropna(subset=['Favorite Score', 'Underdog Score']).copy()
    print(f"✅ Found {len(df_completed)} completed games this season (since {season_start})")
    
    # Convert predictions date to datetime for matching
    df_predictions['date'] = pd.to_datetime(df_predictions['date'])
    
    # Merge predictions with training data
    print("🔗 Matching predictions with games...")
    results = []
    
    for idx, game in df_completed.iterrows():
        game_date = game['Date']
        favorite = game['Favorite']
        underdog = game['Underdog']
        spread = game['Spread']
        fav_odds = game['Fav. Odds']
        dog_odds = game['Dog Odds']
        fav_cover = game['Favorite Cover?']
        
        # Find matching prediction
        pred_match = df_predictions[
            (df_predictions['date'] == game_date) &
            (df_predictions['favorite'] == favorite) &
            (df_predictions['underdog'] == underdog)
        ]
        
        if pred_match.empty:
            # No prediction found, skip
            continue
        
        pred = pred_match.iloc[0]
        model_fav_probability = pred['cover_probability']  # Probability favorite covers
        model_dog_probability = 1 - model_fav_probability  # Probability underdog covers
        predicted_cover = pred['predicted_cover']
        
        # Convert odds to implied probabilities
        fav_implied_prob = american_odds_to_probability(fav_odds)
        dog_implied_prob = american_odds_to_probability(dog_odds)
        
        # Calculate predictive edges for BOTH sides
        # Fav Edge = Model's probability that favorite covers - Implied probability from fav odds
        # Dog Edge = Model's probability that underdog covers - Implied probability from dog odds
        fav_predictive_edge = None
        dog_predictive_edge = None
        
        if fav_implied_prob is not None:
            fav_predictive_edge = model_fav_probability - fav_implied_prob
        
        if dog_implied_prob is not None:
            dog_predictive_edge = model_dog_probability - dog_implied_prob
        
        # Determine best edge and which side to bet
        best_edge = None
        best_side = None
        if fav_predictive_edge is not None and dog_predictive_edge is not None:
            if fav_predictive_edge > dog_predictive_edge:
                best_edge = fav_predictive_edge
                best_side = 'favorite'
            else:
                best_edge = dog_predictive_edge
                best_side = 'underdog'
        
        # If we predicted favorite to cover (predicted_cover=1), did they?
        bet_won = None
        if predicted_cover == 1 and fav_cover == 1:
            bet_won = True
        elif predicted_cover == 1 and fav_cover == 0:
            bet_won = False
        elif predicted_cover == 0 and fav_cover == 0:
            bet_won = True
        elif predicted_cover == 0 and fav_cover == 1:
            bet_won = False
            
        results.append({
            'date': game_date.strftime('%Y-%m-%d'),
            'favorite': favorite,
            'underdog': underdog,
            'spread': spread,
            'fav_odds': fav_odds,
            'dog_odds': dog_odds,
            'fav_implied_prob': fav_implied_prob,
            'dog_implied_prob': dog_implied_prob,
            'model_fav_probability': model_fav_probability,
            'model_dog_probability': model_dog_probability,
            'fav_predictive_edge': fav_predictive_edge,
            'dog_predictive_edge': dog_predictive_edge,
            'best_edge': best_edge,
            'best_side': best_side,
            'predicted_cover': predicted_cover,
            'actual_cover': fav_cover,
            'correct_prediction': bet_won,
            'model_type': pred['model']
        })
    
    # Create results dataframe
    df_results = pd.DataFrame(results)
    print(f"✅ Calculated predictive edges for {len(df_results)} games")
    
    # Save to CSV
    df_results.to_csv(output_file, index=False)
    print(f"💾 Saved results to {output_file}")
    
    # Display analysis
    print("\n" + "="*80)
    print("📊 PREDICTIVE EDGE ANALYSIS")
    print("="*80)
    
    # Overall stats
    total_games = len(df_results)
    avg_fav_edge = df_results['fav_predictive_edge'].mean()
    avg_dog_edge = df_results['dog_predictive_edge'].mean()
    avg_best_edge = df_results['best_edge'].mean()
    
    print(f"\n🎯 Overall Statistics:")
    print(f"   Total Games Analyzed: {total_games}")
    print(f"   Average Favorite Edge: {avg_fav_edge:.4f} ({avg_fav_edge*100:.2f}%)")
    print(f"   Average Underdog Edge: {avg_dog_edge:.4f} ({avg_dog_edge*100:.2f}%)")
    print(f"   Average Best Edge: {avg_best_edge:.4f} ({avg_best_edge*100:.2f}%)")
    
    # Side distribution
    fav_side_count = len(df_results[df_results['best_side'] == 'favorite'])
    dog_side_count = len(df_results[df_results['best_side'] == 'underdog'])
    
    print(f"\n📊 Best Side Distribution:")
    print(f"   Favorite side has edge: {fav_side_count} games ({fav_side_count/total_games*100:.1f}%)")
    print(f"   Underdog side has edge: {dog_side_count} games ({dog_side_count/total_games*100:.1f}%)")
    
    # Edge distribution
    positive_fav_edge = df_results[df_results['fav_predictive_edge'] > 0]
    positive_dog_edge = df_results[df_results['dog_predictive_edge'] > 0]
    positive_best_edge = df_results[df_results['best_edge'] > 0]
    
    print(f"\n📈 Positive Edge Distribution:")
    print(f"   Favorite Positive Edge: {len(positive_fav_edge)} games ({len(positive_fav_edge)/total_games*100:.1f}%)")
    print(f"   Underdog Positive Edge: {len(positive_dog_edge)} games ({len(positive_dog_edge)/total_games*100:.1f}%)")
    print(f"   Best Side Positive Edge: {len(positive_best_edge)} games ({len(positive_best_edge)/total_games*100:.1f}%)")
    
    # Performance with positive best edge
    if len(positive_best_edge) > 0:
        # Determine if bet would have won based on best side
        def check_best_side_win(row):
            if row['best_side'] == 'favorite':
                return row['actual_cover'] == 1  # Favorite covered
            else:  # underdog
                return row['actual_cover'] == 0  # Favorite didn't cover = underdog covered
        
        positive_best_edge['best_side_won'] = positive_best_edge.apply(check_best_side_win, axis=1)
        best_edge_correct = positive_best_edge[positive_best_edge['best_side_won'] == True]
        best_edge_accuracy = len(best_edge_correct) / len(positive_best_edge) * 100
        
        print(f"\n✅ Positive Best Edge Performance:")
        print(f"   Games: {len(positive_best_edge)}")
        print(f"   Accuracy: {best_edge_accuracy:.2f}% ({len(best_edge_correct)}/{len(positive_best_edge)})")
        print(f"   Avg Edge: {positive_best_edge['best_edge'].mean():.4f} ({positive_best_edge['best_edge'].mean()*100:.2f}%)")
    
    # Edge thresholds analysis
    print(f"\n🎚️  Performance by Best Edge Threshold:")
    thresholds = [0.01, 0.02, 0.03, 0.05, 0.10]
    for threshold in thresholds:
        edge_games = df_results[df_results['best_edge'] >= threshold].copy()
        if len(edge_games) > 0:
            def check_best_side_win(row):
                if row['best_side'] == 'favorite':
                    return row['actual_cover'] == 1
                else:
                    return row['actual_cover'] == 0
            edge_games['best_side_won'] = edge_games.apply(check_best_side_win, axis=1)
            correct = edge_games[edge_games['best_side_won'] == True]
            accuracy = len(correct) / len(edge_games) * 100
            avg_edge = edge_games['best_edge'].mean()
            print(f"   Edge ≥ {threshold:.0%}: {len(edge_games)} games, {accuracy:.1f}% accuracy, avg edge: {avg_edge:.4f}")
    
    # Best edges
    print(f"\n🏆 Top 10 Highest Best Edges:")
    top_edges = df_results.nlargest(10, 'best_edge')
    for idx, game in top_edges.iterrows():
        side = game['best_side']
        if side == 'favorite':
            result = "✅" if game['actual_cover'] == 1 else "❌"
            prob = game['model_fav_probability']
        else:
            result = "✅" if game['actual_cover'] == 0 else "❌"
            prob = game['model_dog_probability']
        
        print(f"   {result} {game['date']}: {game['favorite']} vs {game['underdog']} | "
              f"Side: {side.upper()} | "
              f"Edge: {game['best_edge']:.4f} ({game['best_edge']*100:.2f}%) | "
              f"Model Prob: {prob:.3f}")
    
    print("\n" + "="*80)
    
    return df_results

if __name__ == "__main__":
    calculate_predictive_edges()
