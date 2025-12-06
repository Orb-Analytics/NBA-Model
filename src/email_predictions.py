"""
Send Daily Predictions via Email
Author: Orb Analytics (Liam Chaitin)
Purpose: Email today's predictions using existing SMTP setup with updated daily records
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import pandas as pd
import numpy as np
from ensemble_spread_models import EnsembleSpreadPredictor


def get_model_records():
    """
    Calculate current season records for each model.
    Returns dict with model names and their win-loss records.
    """
    records = {}
    model_files = {
        'Logistic': 'data/logistic_model_results.csv',
        'Linear': 'data/linear_model_results.csv',
        'Random Forest': 'data/random_forest_model_results.csv',
        'Decision Tree': 'data/decision_tree_model_results.csv'
    }
    
    for model_name, file_path in model_files.items():
        try:
            df = pd.read_csv(file_path)
            if 'correct_prediction' in df.columns:
                wins = df['correct_prediction'].sum()
                total = len(df)
                losses = total - wins
                win_pct = (wins / total * 100) if total > 0 else 0
                records[model_name] = {
                    'wins': int(wins),
                    'losses': int(losses),
                    'total': total,
                    'win_pct': win_pct
                }
        except FileNotFoundError:
            records[model_name] = {'wins': 0, 'losses': 0, 'total': 0, 'win_pct': 0.0}
    
    return records


def american_odds_to_probability(odds):
    """Convert American odds to implied probability."""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


def generate_predictions_email(date=None):
    """
    Generate predictions email with individual model picks and updated records.
    
    Args:
        date: Date string (YYYY-MM-DD) or None for today
    
    Returns:
        Email body text with predictions and records
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Get current model records
    records = get_model_records()
    
    # Initialize predictor
    predictor = EnsembleSpreadPredictor('data/NBA Training Set 25-26.csv')
    predictor.load_data(verbose=False)
    
    # Train models on all data before today
    predictor.train_models(date, verbose=False)
    
    # Get today's games
    today_games = predictor.df[predictor.df['Date'] == date].copy()
    
    if len(today_games) == 0:
        return f"No games scheduled for {date}"
    
    # Build email body
    email_body = []
    email_body.append("="*100)
    email_body.append(f"🏀 NBA SPREAD PREDICTIONS - {datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')}")
    email_body.append("="*100)
    email_body.append("")
    
    # Add model records
    email_body.append("📊 SEASON RECORDS:")
    email_body.append("-" * 100)
    for model_name, record in records.items():
        email_body.append(f"  {model_name:<20} {record['wins']}-{record['losses']} ({record['win_pct']:.1f}%)")
    email_body.append("="*100)
    email_body.append("")
    
    # Process each game
    for idx, game in today_games.iterrows():
        pred = predictor.predict_game(game)
        
        if not pred:
            continue
        
        # Get odds data
        fav_odds = game.get('Fav. Spread Odds', None)
        dog_odds = game.get('Dog. Spread Odds', None)
        
        # Game header
        email_body.append(f"📋 {pred['favorite']} ({pred['spread']}) vs {pred['underdog']}")
        email_body.append(f"   {'Favorite at Home' if pred['fav_at_home'] == 1 else 'Favorite on Road'}")
        
        if pd.notna(fav_odds) and pd.notna(dog_odds):
            email_body.append(f"   Spread Odds: {pred['favorite']} ({fav_odds:+.0f}) | {pred['underdog']} ({dog_odds:+.0f})")
        
        email_body.append("")
        
        # Individual model predictions
        email_body.append(f"   {'MODEL':<20} {'PICK':<25} {'PROBABILITY':<15} {'EDGE'}")
        email_body.append(f"   {'-'*85}")
        
        model_names = {
            'logistic': 'Logistic',
            'linear': 'Linear',
            'random_forest': 'Random Forest',
            'decision_tree': 'Decision Tree'
        }
        
        votes_fav = 0
        votes_dog = 0
        
        for model_key, model_display in model_names.items():
            prob = pred[f'{model_key}_probability']
            prediction = pred[f'{model_key}_prediction']
            
            # Determine pick
            if prediction == 1:
                pick = f"{pred['favorite']} to COVER"
                votes_fav += 1
            else:
                pick = f"{pred['underdog']} to COVER"
                votes_dog += 1
            
            prob_str = f"{prob*100:.1f}%"
            
            # Calculate edge if odds available
            if pd.notna(fav_odds):
                market_prob = american_odds_to_probability(fav_odds)
                if prediction == 1:
                    edge = prob - market_prob
                else:
                    edge = (1 - prob) - (1 - market_prob)
                edge_str = f"{edge*100:+.1f}%"
            else:
                edge_str = "N/A"
            
            email_body.append(f"   {model_display:<20} {pick:<25} {prob_str:<15} {edge_str}")
        
        email_body.append(f"   {'-'*85}")
        
        # Consensus
        if votes_fav >= 3:
            consensus = f"CONSENSUS: {pred['favorite']} to COVER ({votes_fav}/4 models)"
        elif votes_dog >= 3:
            consensus = f"CONSENSUS: {pred['underdog']} to COVER ({votes_dog}/4 models)"
        else:
            consensus = f"SPLIT DECISION: {votes_fav} models favor {pred['favorite']}, {votes_dog} favor {pred['underdog']}"
        
        email_body.append(f"   🎯 {consensus}")
        email_body.append("")
        email_body.append("="*100)
        email_body.append("")
    
    return "\n".join(email_body)


def send_predictions_email(predictions_text, to_email, smtp_config):
    """
    Send predictions via email.
    
    Args:
        predictions_text: The prediction text to send
        to_email: Recipient email address
        smtp_config: Dict with smtp_user, smtp_pass, smtp_server, smtp_port
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏀 NBA Predictions - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = smtp_config['smtp_user']
        msg['To'] = to_email
        
        # Plain text version
        text_part = MIMEText(predictions_text, 'plain')
        msg.attach(text_part)
        
        # Connect and send
        server = smtplib.SMTP(smtp_config['smtp_server'], int(smtp_config['smtp_port']))
        server.starttls()
        server.login(smtp_config['smtp_user'], smtp_config['smtp_pass'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    """Send today's predictions via email with updated records and individual model picks."""
    # Get SMTP config from environment
    smtp_config = {
        'smtp_user': os.environ.get('SMTP_USERNAME'),
        'smtp_pass': os.environ.get('SMTP_PASSWORD'),
        'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': os.environ.get('SMTP_PORT', '587')
    }
    
    # Recipient email
    to_email = os.environ.get('RECIPIENT_EMAIL', smtp_config['smtp_user'])
    
    # Get date (optional argument)
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Generate predictions email with live records
    print(f"📧 Generating predictions email for {date}...")
    predictions_text = generate_predictions_email(date)
    
    # Optionally save to file
    output_file = f'data/predictions_{date.replace("-", "_")}.txt'
    with open(output_file, 'w') as f:
        f.write(predictions_text)
    print(f"💾 Predictions saved to {output_file}")
    
    # Send email
    success = send_predictions_email(predictions_text, to_email, smtp_config)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
