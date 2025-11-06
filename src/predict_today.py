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
import warnings
warnings.filterwarnings('ignore')

# Import feature lists
from daily_spread_predictions import HOME_PREDICTORS, AWAY_PREDICTORS, DailySpreadPredictor


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
    
    return f"""{emoji} {pred['favorite']} vs {pred['underdog']} (Spread: {pred['spread']})
   Prediction: Favorite will {cover_text}
   Confidence: {pred['cover_probability']:.1%}
   Model: {pred['model']}"""


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
    
    print(f"🎯 Generating predictions for {today_date}")
    
    # Initialize predictor
    predictor = DailySpreadPredictor(data_path)
    predictor.load_data()
    
    # Run prediction for today only
    result = predictor.train_and_predict_day(today_date)
    
    if result is None or len(result['predictions']) == 0:
        return f"No games scheduled for {today_date}"
    
    predictions = result['predictions']
    
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
    data_path = '/workspaces/NBA-model/data/NBA Training Set 25-26.csv'
    
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
    output_file = f'./data/predictions_{today_date.replace("-", "_")}.txt'
    with open(output_file, 'w') as f:
        f.write(predictions_text)
    
    print(f"\n\n✅ Predictions saved to {output_file}")


if __name__ == "__main__":
    main()
