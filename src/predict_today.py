"""
Generate Today's NBA Spread Predictions
Author: Orb Analytics (Liam Chaitin)
Purpose: Predict today's games and format for email notification
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Import feature lists
from daily_spread_predictions import HOME_PREDICTORS, AWAY_PREDICTORS, DailySpreadPredictor


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


def get_confidence_emoji(probability):
    """Get emoji based on confidence level."""
    if probability >= 0.7 or probability <= 0.3:
        return "💪"
    else:
        return "⚖️"


def format_prediction_text(pred):
    """Format a single prediction for email."""
    emoji = get_confidence_emoji(pred['cover_probability'])
    cover_text = "COVER" if pred['predicted_cover'] == 1 else "NO COVER"
    
    # Calculate predictive edges
    fav_odds = pred.get('fav_odds', -110)
    dog_odds = pred.get('dog_odds', -110)
    
    model_fav_prob = pred['cover_probability']
    model_dog_prob = 1 - model_fav_prob
    
    fav_implied_prob = american_odds_to_probability(fav_odds)
    dog_implied_prob = american_odds_to_probability(dog_odds)
    
    fav_edge = model_fav_prob - fav_implied_prob if fav_implied_prob else None
    dog_edge = model_dog_prob - dog_implied_prob if dog_implied_prob else None
    
    # Determine best side
    if fav_edge and dog_edge:
        if fav_edge > dog_edge:
            best_side = "FAVORITE"
            best_edge = fav_edge
            best_team = pred['favorite']
        else:
            best_side = "UNDERDOG"
            best_edge = dog_edge
            best_team = pred['underdog']
    else:
        best_side = "N/A"
        best_edge = None
        best_team = None
    
    # Format edge indicators
    fav_edge_text = ""
    dog_edge_text = ""
    
    if fav_edge is not None:
        if fav_edge > 0:
            fav_edge_text = f"✅ FAV Edge: +{fav_edge:.1%}"
        else:
            fav_edge_text = f"❌ FAV Edge: {fav_edge:.1%}"
    
    if dog_edge is not None:
        if dog_edge > 0:
            dog_edge_text = f"✅ DOG Edge: +{dog_edge:.1%}"
        else:
            dog_edge_text = f"❌ DOG Edge: {dog_edge:.1%}"
    
    best_bet_text = ""
    # Only show best bet if at least one side has positive edge
    if fav_edge is not None and dog_edge is not None:
        # If both are negative, no bet
        if fav_edge <= 0 and dog_edge <= 0:
            best_bet_text = f"\n   ⛔ NO BET: No positive edge on either side"
        # If both are positive, take the greater one
        elif fav_edge > 0 and dog_edge > 0:
            if fav_edge > dog_edge and best_team:
                best_bet_text = f"\n   🎯 BEST BET: {best_team} ({fav_edge:+.1%} edge)"
            elif best_team:
                best_bet_text = f"\n   🎯 BEST BET: {best_team} ({dog_edge:+.1%} edge)"
        # Otherwise, take the positive edge
        elif best_edge and best_edge > 0 and best_team:
            best_bet_text = f"\n   🎯 BEST BET: {best_team} ({best_edge:+.1%} edge)"
    
    return f"""{emoji} {pred['favorite']} vs {pred['underdog']} (Spread: {pred['spread']})
   Prediction: Favorite will {cover_text}
   Confidence: {pred['cover_probability']:.1%}
   {fav_edge_text} | {dog_edge_text}{best_bet_text}
   Model: {pred['model']}"""


def save_predictions_to_results(predictions, today_date, results_path):
    """
    Save today's predictions to the results CSV file.
    Appends new predictions and updates existing ones with actual results.
    
    Args:
        predictions: List of prediction dictionaries
        today_date: Date string (YYYY-MM-DD)
        results_path: Path to daily_predictions_results.csv
    """
    # Load existing results if file exists
    if os.path.exists(results_path):
        existing_df = pd.read_csv(results_path)
        existing_df['date'] = pd.to_datetime(existing_df['date']).dt.strftime('%Y-%m-%d')
    else:
        existing_df = pd.DataFrame()
    
    # Convert predictions to DataFrame format
    new_rows = []
    for pred in predictions:
        row = {
            'favorite': pred['favorite'],
            'underdog': pred['underdog'],
            'spread': pred['spread'],
            'fav_at_home': 1 if pred['model'] == 'Home Favorite' else 0,
            'model': pred['model'],
            'predicted_cover': pred['predicted_cover'],
            'cover_probability': pred['cover_probability'],
            'actual_cover': pred.get('actual_cover', ''),
            'correct': pred.get('correct', ''),
            'date': today_date
        }
        new_rows.append(row)
    
    new_df = pd.DataFrame(new_rows)
    
    # Remove any existing predictions for this date (to avoid duplicates on reruns)
    if len(existing_df) > 0:
        existing_df = existing_df[existing_df['date'] != today_date]
    
    # Combine and save
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv(results_path, index=False)


def update_results_with_scores(data_path, results_path):
    """
    Update the results CSV with actual outcomes for games that now have scores.
    
    Args:
        data_path: Path to NBA Training Set CSV (master data with scores)
        results_path: Path to daily_predictions_results.csv
    """
    if not os.path.exists(results_path):
        return
    
    # Load the results file
    results_df = pd.read_csv(results_path)
    
    # Load the master training set with scores
    master_df = pd.read_csv(data_path)
    
    # For each pending prediction, check if we now have a score
    updates_made = 0
    for idx, row in results_df.iterrows():
        # Skip if already has result
        if pd.notna(row['correct']) and row['correct'] != '':
            continue
        
        # Find the corresponding game in master data
        game_date = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
        fav = row['favorite']
        dog = row['underdog']
        spread = float(row['spread'])
        
        # Find matching game
        game = master_df[
            (master_df['Date'] == game_date) &
            (master_df['Favorite'] == fav) &
            (master_df['Underdog'] == dog) &
            (master_df['Spread'] == spread)
        ]
        
        if len(game) == 1 and pd.notna(game.iloc[0]['Favorite Score']):
            # Game has a score now - calculate actual result
            fav_score = game.iloc[0]['Favorite Score']
            dog_score = game.iloc[0]['Underdog Score']
            
            if pd.notna(fav_score) and pd.notna(dog_score):
                fav_margin = fav_score - dog_score
                actual_cover = 1 if fav_margin > spread else 0
                correct = 1 if actual_cover == row['predicted_cover'] else 0
                
                # Update the results
                results_df.at[idx, 'actual_cover'] = float(actual_cover)
                results_df.at[idx, 'correct'] = bool(correct)
                updates_made += 1
    
    # Save updated results
    if updates_made > 0:
        results_df.to_csv(results_path, index=False)
        # print(f"Updated {updates_made} predictions with actual results")


def predict_today_games(data_path, today_date=None):
    """
    Predict today's games and return formatted output.
    
    Args:
        data_path: Path to NBA Training Set CSV
        today_date: Date to predict (defaults to today)
        
    Returns:
        Formatted string with predictions
    """
    if today_date is None:
        today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Don't print this in production, only the final formatted output
    # print(f"🎯 Generating predictions for {today_date}")
    
    # Initialize predictor
    predictor = DailySpreadPredictor(data_path)
    predictor.load_data(verbose=False)
    
    # Run prediction for today only (verbose=False for clean email output)
    result = predictor.train_and_predict_day(today_date, verbose=False)
    
    if result is None or len(result['predictions']) == 0:
        return f"No games scheduled for {today_date}"
    
    predictions = result['predictions']
    
    # Save predictions to results file
    results_path = os.path.join(os.path.dirname(data_path), 'daily_predictions_results.csv')
    save_predictions_to_results(predictions, today_date, results_path)
    
    # Update any pending results that now have scores
    update_results_with_scores(data_path, results_path)
    
    # Load master data to get odds for today's games
    df_master = pd.read_csv(data_path)
    df_master['Date'] = pd.to_datetime(df_master['Date']).dt.strftime('%Y-%m-%d')
    today_games = df_master[df_master['Date'] == today_date]
    
    # Add odds to predictions
    for pred in predictions:
        game_match = today_games[
            (today_games['Favorite'] == pred['favorite']) &
            (today_games['Underdog'] == pred['underdog'])
        ]
        if not game_match.empty:
            pred['fav_odds'] = game_match.iloc[0].get('Fav. Odds', -110)
            pred['dog_odds'] = game_match.iloc[0].get('Dog Odds', -110)
        else:
            pred['fav_odds'] = -110
            pred['dog_odds'] = -110
    
    # Sort by confidence (high confidence first)
    predictions_sorted = sorted(
        predictions, 
        key=lambda x: max(x['cover_probability'], 1 - x['cover_probability']),
        reverse=True
    )
    
    # Format output
    output = []
    output.append(f"🏀 NBA SPREAD PREDICTIONS - {today_date}")
    output.append("=" * 70)
    output.append(f"\nTotal: {len(predictions)} games\n")
    
    for pred in predictions_sorted:
        output.append(format_prediction_text(pred))
        output.append("")  # Empty line between predictions
    
    # Add summary
    output.append("=" * 70)
    
    # Calculate model's season record up to this date
    try:
        results_df = pd.read_csv(os.path.join(os.path.dirname(data_path), 'daily_predictions_results.csv'))
        results_df['date'] = pd.to_datetime(results_df['date'])
        today_dt = pd.to_datetime(today_date)
        
        # Get all predictions before today
        prior_results = results_df[results_df['date'] < today_dt].copy()
        
        if len(prior_results) > 0:
            # Overall record
            total_games = len(prior_results)
            correct = prior_results['correct'].sum()
            accuracy = (correct / total_games * 100) if total_games > 0 else 0
            
            # Record by model type
            home_fav = prior_results[prior_results['model'] == 'Home Favorite']
            away_fav = prior_results[prior_results['model'] == 'Away Favorite']
            
            home_record = f"{home_fav['correct'].sum()}-{len(home_fav) - home_fav['correct'].sum()}" if len(home_fav) > 0 else "0-0"
            away_record = f"{away_fav['correct'].sum()}-{len(away_fav) - away_fav['correct'].sum()}" if len(away_fav) > 0 else "0-0"
            
            home_acc = (home_fav['correct'].sum() / len(home_fav) * 100) if len(home_fav) > 0 else 0
            away_acc = (away_fav['correct'].sum() / len(away_fav) * 100) if len(away_fav) > 0 else 0
            
            output.append("\n📊 MODEL RECORD THIS SEASON (through " + str(today_dt.date()) + "):")
            output.append(f"Overall: {correct}-{total_games - correct} ({accuracy:.1f}%)")
            output.append(f"🏠 Home Favorite Model: {home_record} ({home_acc:.1f}%)")
            output.append(f"✈️  Away Favorite Model: {away_record} ({away_acc:.1f}%)")
            output.append("")
    except Exception as e:
        # If we can't load results, just skip the record section
        pass
    
    output.append("\n📊 CONFIDENCE BREAKDOWN:")
    
    high_conf = [p for p in predictions if p['cover_probability'] >= 0.7 or p['cover_probability'] <= 0.3]
    med_conf = [p for p in predictions if 0.55 <= p['cover_probability'] < 0.7 or 0.3 < p['cover_probability'] <= 0.45]
    low_conf = [p for p in predictions if 0.45 < p['cover_probability'] < 0.55]
    
    output.append(f"💪 High Confidence (>70% or <30%): {len(high_conf)} games")
    output.append(f"⚖️  Medium Confidence (55-70% or 30-45%): {len(med_conf)} games")
    output.append(f"⚠️  Low Confidence (45-55%): {len(low_conf)} games")
    
    output.append("\n" + "=" * 70)
    output.append("\n🎲 BETTING RECOMMENDATIONS:")
    output.append("💪 High Confidence bets are recommended")
    output.append("⚖️  Medium Confidence bets are optional")
    output.append("⚠️  Low Confidence bets should be avoided")
    
    output.append("\n" + "=" * 70)
    output.append(f"\n📈 Model Info:")
    output.append(f"Training data: All games before {today_date}")
    output.append(f"Home Favorite Model: {len([p for p in predictions if p['model'] == 'Home Favorite'])} predictions")
    output.append(f"Away Favorite Model: {len([p for p in predictions if p['model'] == 'Away Favorite'])} predictions")
    
    return "\n".join(output)


def main():
    """Main execution."""
    # Use relative path that works in both dev container and GitHub Actions
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, 'data', 'NBA Training Set 25-26.csv')
    
    # Get today's date (or from command line argument)
    if len(sys.argv) > 1:
        today_date = sys.argv[1]
    else:
        today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Generate predictions
    predictions_text = predict_today_games(data_path, today_date)
    
    # Print to stdout (will be captured for email)
    print(predictions_text)
    
    # Also save to file
    output_dir = os.path.join(project_root, 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'predictions_{today_date.replace("-", "_")}.txt')
    with open(output_file, 'w') as f:
        f.write(predictions_text)
    
    print(f"\n\n✅ Predictions saved to {output_file}")


if __name__ == "__main__":
    main()
