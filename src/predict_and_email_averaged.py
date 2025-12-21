#!/usr/bin/env python3
"""
Generate and Email Averaged Model NBA Predictions
Purpose: Generate predictions using the standardized & averaged model approach
         Show yesterday's results, today's predictions, and season record
"""

import pandas as pd
import numpy as np
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from ensemble_spread_models import EnsembleSpreadPredictor
from prediction_core import american_to_prob


def get_yesterday_results(backtest_path='data/averaged_model_backtest.csv', yesterday_date=None):
    """Get yesterday's picks and their results from the backtest file."""
    if not os.path.exists(backtest_path):
        return []
    
    backtest_df = pd.read_csv(backtest_path)
    backtest_df['date'] = pd.to_datetime(backtest_df['date']).dt.strftime('%Y-%m-%d')
    
    if yesterday_date:
        yesterday_picks = backtest_df[
            (backtest_df['date'] == yesterday_date) & 
            (backtest_df['pick_side'] != 'NO BET')
        ].copy()
    else:
        yesterday_picks = pd.DataFrame()
    
    return yesterday_picks.to_dict('records')


def get_season_record(backtest_path='data/averaged_model_backtest.csv'):
    """Calculate season record from backtest file (includes all results to date)."""
    if not os.path.exists(backtest_path):
        return {'wins': 0, 'losses': 0, 'total': 0, 'win_pct': 0.0}
    
    backtest_df = pd.read_csv(backtest_path)
    picks = backtest_df[backtest_df['pick_side'] != 'NO BET'].copy()
    
    wins = len(picks[picks['result'] == 'WIN'])
    losses = len(picks[picks['result'] == 'LOSS'])
    total = wins + losses
    win_pct = (wins / total * 100) if total > 0 else 0.0
    
    return {
        'wins': wins,
        'losses': losses,
        'total': total,
        'win_pct': win_pct
    }


def generate_averaged_predictions(date_str, data_path='data/NBA Training Set 25-26.csv', min_edge=0.03):
    """Generate predictions using the standardized & averaged model."""
    
    predictor = EnsembleSpreadPredictor(data_path)
    predictor.load_data(verbose=False)
    master_df = predictor.df.copy()
    master_df['Date'] = pd.to_datetime(master_df['Date'])
    
    # Train models
    success = predictor.train_models(date_str, verbose=False)
    if not success:
        return []
    
    # Get today's games
    games_today = master_df[master_df['Date'] == pd.to_datetime(date_str)].copy()
    
    if len(games_today) == 0:
        return []
    
    predictions = []
    
    for idx, game_row in games_today.iterrows():
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
        
        # Average valid model probabilities
        probs = [logistic_prob, linear_prob, rf_prob, tree_prob]
        valid_probs = [p for p in probs if not pd.isna(p)]
        
        if len(valid_probs) == 0:
            continue
        
        averaged_fav_prob = np.mean(valid_probs)
        averaged_dog_prob = 1 - averaged_fav_prob
        
        # Apply standardization
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
        elif dog_edge >= min_edge and dog_edge > fav_edge:
            pick_side = "UNDERDOG"
            pick_team = underdog
            pick_line = spread
            edge = dog_edge
            cover_prob = standardized_dog
        else:
            pick_side = "NO BET"
            pick_team = None
            pick_line = None
            edge = max(fav_edge, dog_edge)
            cover_prob = None
        
        predictions.append({
            'favorite': favorite,
            'underdog': underdog,
            'spread': spread,
            'fav_odds': fav_odds,
            'dog_odds': dog_odds,
            'pick_side': pick_side,
            'pick_team': pick_team,
            'pick_line': pick_line,
            'edge': edge,
            'cover_prob': cover_prob,
            'fav_edge': fav_edge,
            'dog_edge': dog_edge
        })
    
    return predictions


def format_email(predictions, yesterday_results, season_record, date_str):
    """Format predictions and results into email body."""
    
    lines = []
    lines.append("="*100)
    lines.append(f"🏀 NBA PREDICTIONS - {date_str}")
    lines.append("📊 Standardized & Averaged Model")
    lines.append("="*100)
    lines.append("")
    
    # Season Record
    lines.append("📈 SEASON RECORD")
    lines.append(f"   {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)")
    lines.append("")
    lines.append("="*100)
    
    # Yesterday's Results (if any)
    if yesterday_results:
        lines.append("")
        lines.append("📅 YESTERDAY'S RESULTS")
        lines.append("="*100)
        
        wins = sum(1 for r in yesterday_results if r['result'] == 'WIN')
        losses = sum(1 for r in yesterday_results if r['result'] == 'LOSS')
        
        for result in yesterday_results:
            emoji = "✅" if result['result'] == 'WIN' else "❌" if result['result'] == 'LOSS' else "⏳"
            
            if result['pick_side'] == 'FAVORITE':
                pick_str = f"{result['pick_team']} {-result['spread']:+.1f}"
            else:
                pick_str = f"{result['pick_team']} {result['spread']:+.1f}"
            
            lines.append(f"{emoji} {pick_str}")
            lines.append(f"   {result['favorite']} vs {result['underdog']}")
            lines.append(f"   Edge: {result['edge']:.1%}")
            lines.append("")
        
        lines.append(f"Record: {wins}-{losses}")
        lines.append("="*100)
    
    # Today's Predictions
    lines.append("")
    lines.append("🎯 TODAY'S PICKS")
    lines.append("="*100)
    lines.append("")
    
    picks = [p for p in predictions if p['pick_side'] != 'NO BET']
    
    if not picks:
        lines.append("⚪ No picks today - no games meet the 3% edge threshold")
    else:
        # Sort by edge (highest first)
        picks_sorted = sorted(picks, key=lambda x: x['edge'], reverse=True)
        
        for pick in picks_sorted:
            # Format pick line
            if pick['pick_side'] == 'FAVORITE':
                pick_line = f"{pick['pick_team']} {pick['pick_line']:+.1f}"
            else:
                pick_line = f"{pick['pick_team']} {pick['pick_line']:+.1f}"
            
            lines.append(f"🏀 {pick_line}")
            lines.append(f"   Game: {pick['favorite']} vs {pick['underdog']} (Spread: {pick['favorite']} {-pick['spread']:+.1f})")
            lines.append(f"   Orb Cover Probability: {pick['cover_prob']:.1%}")
            lines.append(f"   Edge: {pick['edge']:.1%}")
            lines.append("")
    
    lines.append("="*100)
    lines.append("")
    lines.append(f"Total Games Today: {len(predictions)}")
    lines.append(f"Picks Made: {len(picks)}")
    lines.append(f"No Bets: {len(predictions) - len(picks)}")
    lines.append("")
    lines.append("📊 Model: 35% Averaged Models + 65% Implied Odds")
    lines.append("📈 Minimum Edge: 3.0%")
    lines.append("="*100)
    
    return "\n".join(lines)


def send_email(subject, body):
    """Send email via SMTP."""
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not all([smtp_server, smtp_username, smtp_password]):
        print("⚠️ SMTP credentials not configured - email not sent")
        return False
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = 'lpchaitin@gmail.com,eborsook@gmail.com'
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print("✅ Email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate and email averaged model predictions')
    parser.add_argument('--date', type=str, default=None,
                       help='Date to predict (YYYY-MM-DD, default: today)')
    parser.add_argument('--no-email', action='store_true',
                       help='Skip sending email')
    
    args = parser.parse_args()
    
    # Get dates
    if args.date:
        today = datetime.strptime(args.date, '%Y-%m-%d')
    else:
        today = datetime.now()
    
    today_str = today.strftime('%Y-%m-%d')
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    print("="*100)
    print("🏀 GENERATING AVERAGED MODEL PREDICTIONS")
    print("="*100)
    print(f"Date: {today_str}")
    print()
    
    # Get yesterday's results
    print(f"📅 Loading yesterday's results ({yesterday_str})...")
    yesterday_results = get_yesterday_results(yesterday_date=yesterday_str)
    print(f"   Found {len(yesterday_results)} picks from yesterday")
    
    # Get season record
    print("📊 Loading season record...")
    season_record = get_season_record()
    print(f"   Season: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)")
    
    # Generate today's predictions
    print(f"🎯 Generating predictions for {today_str}...")
    predictions = generate_averaged_predictions(today_str)
    print(f"   Generated {len(predictions)} predictions")
    picks = [p for p in predictions if p['pick_side'] != 'NO BET']
    print(f"   Picks: {len(picks)}")
    print()
    
    # Format email
    email_body = format_email(predictions, yesterday_results, season_record, today_str)
    
    print("="*100)
    print("EMAIL PREVIEW:")
    print("="*100)
    print(email_body)
    print("="*100)
    print()
    
    # Send email
    if not args.no_email:
        subject = f"🏀 NBA Predictions - {today_str}"
        send_email(subject, email_body)
    else:
        print("⚠️ Email sending skipped (--no-email flag)")


if __name__ == "__main__":
    main()
