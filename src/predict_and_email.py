"""
Generate and Email NBA Predictions (New Framework)
Author: Orb Analytics (Liam Chaitin)
Purpose: Main script to generate predictions with all 4 models and send via email
"""

import pandas as pd
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import argparse

# Import our new modules
from ensemble_spread_models import EnsembleSpreadPredictor
from prediction_core import build_prediction_record
from email_formatter import format_predictions_for_email
from model_history import get_season_records, record_predictions


def generate_predictions(date: str, data_path: str = 'data/NBA Training Set 25-26.csv'):
    """
    Generate predictions for all games on specified date using all 4 models.
    
    Args:
        date: Date string (YYYY-MM-DD)
        data_path: Path to master dataset
    
    Returns:
        List of prediction record dicts
    """
    print(f"🔮 Generating predictions for {date}")
    print("="*100)
    
    # Initialize predictor
    predictor = EnsembleSpreadPredictor(data_path)
    predictor.load_data(verbose=True)
    
    # Train models on all data before this date
    print(f"\n📚 Training models on data before {date}...")
    success = predictor.train_models(date, verbose=True)
    
    if not success:
        print("❌ Failed to train models")
        return []
    
    # Get games for this date
    today_games = predictor.df[predictor.df['Date'] == date].copy()
    
    if len(today_games) == 0:
        print(f"⚠️ No games found for {date}")
        return []
    
    print(f"\n🏀 Found {len(today_games)} games on {date}")
    print("="*100)
    
    # Generate predictions for each game
    predictions = []
    
    for idx, game_row in today_games.iterrows():
        # Get predictions from all models
        ensemble_pred = predictor.predict_game(game_row)
        
        if not ensemble_pred:
            print(f"⚠️ Could not predict game: {game_row['Favorite']} vs {game_row['Underdog']}")
            continue
        
        # Build model predictions dict with consistent naming
        model_predictions = {
            'Logistic': ensemble_pred['logistic_probability'],
            'Linear': ensemble_pred['linear_probability'],
            'Random Forest': ensemble_pred['random_forest_probability'],
            'Decision Tree': ensemble_pred['decision_tree_probability']
        }
        
        # Build standardized prediction record
        prediction_record = build_prediction_record(game_row, model_predictions)
        predictions.append(prediction_record)
        
        print(f"✅ {prediction_record['favorite_team']} ({prediction_record['spread']}) vs {prediction_record['underdog_team']}")
    
    print("="*100)
    print(f"✅ Generated {len(predictions)} predictions\n")
    
    return predictions


def send_email(subject: str, body: str):
    """
    Send email using SMTP configuration from environment variables.
    
    Args:
        subject: Email subject line
        body: Email body text
    """
    # Get SMTP config from environment
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    to_email = os.environ.get('TO_EMAIL', smtp_username)
    
    if not all([smtp_server, smtp_username, smtp_password]):
        print("❌ Missing SMTP configuration in environment variables")
        print("   Required: SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD")
        return False
    
    # Parse recipient emails (handle comma-separated list)
    if ',' in to_email:
        recipients = [email.strip() for email in to_email.split(',')]
    else:
        recipients = [to_email.strip()]
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = ', '.join(recipients)  # Properly format multiple recipients
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        print(f"📧 Sending email to {len(recipients)} recipient(s)...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        # Use sendmail with list of recipients
        server.sendmail(smtp_username, recipients, msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Generate and email NBA predictions')
    parser.add_argument('--date', type=str, help='Date to predict (YYYY-MM-DD), defaults to today')
    parser.add_argument('--no-email', action='store_true', help='Skip sending email (just print)')
    parser.add_argument('--save-to-file', type=str, help='Save predictions to text file instead of/in addition to email')
    
    args = parser.parse_args()
    
    # Determine date
    if args.date:
        date = args.date
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    date_display = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
    
    # Generate predictions
    predictions = generate_predictions(date)
    
    if not predictions:
        print("❌ No predictions generated")
        return
    
    # Record predictions to history (with PENDING status)
    print("💾 Recording predictions to history...")
    record_predictions(predictions)
    
    # Get current season records
    print("📊 Computing season records...")
    season_records = get_season_records(end_date=date)
    
    # Format email
    email_body = format_predictions_for_email(predictions, season_records, date_display)
    
    # Print to console
    print("\n" + "="*100)
    print("📧 EMAIL PREVIEW")
    print("="*100)
    print(email_body)
    print("="*100)
    
    # Save to file if requested
    if args.save_to_file:
        with open(args.save_to_file, 'w') as f:
            f.write(email_body)
        print(f"✅ Saved predictions to {args.save_to_file}")
    
    # Send email if not disabled
    if not args.no_email:
        subject = f"🏀 NBA Predictions - {date_display}"
        send_email(subject, email_body)
    else:
        print("⚠️ Email sending skipped (--no-email flag)")


if __name__ == "__main__":
    main()
