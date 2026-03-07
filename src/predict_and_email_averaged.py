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
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
import argparse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))

from ensemble_spread_models import EnsembleSpreadPredictor
from prediction_core import american_to_prob
from verify_game_matchup import verify_games


def format_american_odds(odds, default=-110):
    """Format American odds robustly as '+105' or '-110'.

    The dataset and novig odds can sometimes be parsed as floats (e.g. -110.0).
    The email templates previously assumed ints.
    """

    try:
        if odds is None or (isinstance(odds, float) and pd.isna(odds)):
            odds = default
        odds_int = int(round(float(odds)))
        return f"{odds_int:+d}"
    except Exception:
        return f"{int(default):+d}"


def calculate_units(odds, result):
    """Calculate units won/lost for a bet.
    
    Args:
        odds: American odds (e.g., -110, +150)
        result: 'WIN' or 'LOSS'
    
    Returns:
        float: Units won (positive) or lost (negative)
    """
    if pd.isna(odds) or result not in ['WIN', 'LOSS']:
        return 0.0
    
    if result == 'LOSS':
        return -1.0  # Always lose 1 unit
    
    # WIN
    if odds > 0:
        # Underdog: profit = stake * (odds / 100)
        return odds / 100
    else:
        # Favorite: profit = stake * (100 / abs(odds))
        return 100 / abs(odds)


# Team name to ESPN abbreviation mapping for logos
TEAM_LOGOS = {
    'Atlanta': 'atl', 'Boston': 'bos', 'Brooklyn': 'bkn', 'Charlotte': 'cha',
    'Chicago': 'chi', 'Cleveland': 'cle', 'Dallas': 'dal', 'Denver': 'den',
    'Detroit': 'det', 'Golden State': 'gs', 'Houston': 'hou', 'Indiana': 'ind',
    'La Clippers': 'lac', 'La Lakers': 'lal', 'Memphis': 'mem', 'Miami': 'mia',
    'Milwaukee': 'mil', 'Minnesota': 'min', 'New Orleans': 'no', 'New York': 'ny',
    'Okla City': 'okc', 'Orlando': 'orl', 'Philadelphia': 'phi', 'Phoenix': 'phx',
    'Portland': 'por', 'Sacramento': 'sac', 'San Antonio': 'sa', 'Toronto': 'tor',
    'Utah': 'utah', 'Washington': 'wsh'
}


def get_team_logo_url(team_name, size=40):
    """Get ESPN logo URL for a team."""
    abbrev = TEAM_LOGOS.get(team_name, 'nba')
    return f'https://a.espncdn.com/i/teamlogos/nba/500/{abbrev}.png'


def get_yesterday_results(backtest_path='data/averaged_model_backtest.csv', yesterday_date=None):
    """Get yesterday's picks and their results from the backtest file."""
    if not os.path.exists(backtest_path):
        return [], 0.0
    
    backtest_df = pd.read_csv(backtest_path)
    backtest_df['date'] = pd.to_datetime(backtest_df['date']).dt.strftime('%Y-%m-%d')
    
    if yesterday_date:
        yesterday_picks = backtest_df[
            (backtest_df['date'] == yesterday_date) & 
            (backtest_df['pick_side'] != 'NO BET')
        ].copy()
    else:
        yesterday_picks = pd.DataFrame()
    
    # Calculate units for yesterday
    total_units = 0.0
    records = yesterday_picks.to_dict('records')
    
    for record in records:
        if record['pick_side'] == 'FAVORITE':
            odds = record.get('fav_odds', -110)
        else:
            odds = record.get('dog_odds', -110)
        
        units = calculate_units(odds, record.get('result', ''))
        record['units'] = units
        total_units += units
    
    return records, total_units


def get_season_record(backtest_path='data/averaged_model_backtest.csv', master_path='data/NBA Training Set 25-26.csv'):
    """Calculate season record from backtest file (includes all results to date)."""
    if not os.path.exists(backtest_path):
        return {'wins': 0, 'losses': 0, 'total': 0, 'win_pct': 0.0, 'units': 0.0, 'roi': 0.0}
    
    backtest_df = pd.read_csv(backtest_path)
    picks = backtest_df[backtest_df['pick_side'] != 'NO BET'].copy()
    # Filter to completed picks only (exclude PENDING)
    completed_picks = picks[picks['result'].isin(['WIN', 'LOSS'])]
    
    wins = len(completed_picks[completed_picks['result'] == 'WIN'])
    losses = len(completed_picks[completed_picks['result'] == 'LOSS'])
    total = wins + losses
    win_pct = (wins / total * 100) if total > 0 else 0.0
    
    # Calculate total units
    total_units = 0.0
    for _, row in completed_picks.iterrows():
        if row['pick_side'] == 'FAVORITE':
            odds = row.get('fav_odds', -110)
        else:
            odds = row.get('dog_odds', -110)
        
        units = calculate_units(odds, row.get('result', ''))
        total_units += units
    
    # Calculate ROI
    roi = (total_units / total * 100) if total > 0 else 0.0
    
    return {
        'wins': wins,
        'losses': losses,
        'total': total,
        'win_pct': win_pct,
        'units': total_units,
        'roi': roi
    }


def get_performance_splits(backtest_path='data/averaged_model_backtest.csv', master_path='data/NBA Training Set 25-26.csv'):
    """Calculate performance splits from backtest file."""
    if not os.path.exists(backtest_path) or not os.path.exists(master_path):
        return None
    
    # Read both files
    backtest_df = pd.read_csv(backtest_path)
    master_df = pd.read_csv(master_path)
    
    # Standardize dates
    backtest_df['date'] = pd.to_datetime(backtest_df['date']).dt.strftime('%Y-%m-%d')
    master_df['Date'] = pd.to_datetime(master_df['Date']).dt.strftime('%Y-%m-%d')
    
    # Create merge keys
    backtest_df['merge_key'] = (backtest_df['date'] + '|' + 
                                 backtest_df['favorite'] + '|' + 
                                 backtest_df['underdog'])
    master_df['merge_key'] = (master_df['Date'] + '|' + 
                              master_df['Favorite'] + '|' + 
                              master_df['Underdog'])
    
    # Merge to get home/away info
    merged_df = backtest_df.merge(
        master_df[['merge_key', 'Fav. At Home?']], 
        on='merge_key', 
        how='left'
    )
    
    # Filter to only picks
    picks = merged_df[merged_df['pick_side'] != 'NO BET'].copy()
    
    # Calculate splits
    def calc_record(df):
        if len(df) == 0:
            return {'wins': 0, 'losses': 0, 'pct': 0.0, 'units': 0.0}
        wins = len(df[df['result'] == 'WIN'])
        losses = len(df[df['result'] == 'LOSS'])
        total = wins + losses
        pct = (wins / total * 100) if total > 0 else 0.0
        
        # Calculate units
        total_units = 0.0
        for _, row in df.iterrows():
            if row['pick_side'] == 'FAVORITE':
                odds = row.get('fav_odds', -110)
            else:
                odds = row.get('dog_odds', -110)
            
            units = calculate_units(odds, row.get('result', ''))
            total_units += units
        
        return {'wins': wins, 'losses': losses, 'pct': pct, 'units': total_units}
    
    # By pick type
    fav_picks = calc_record(picks[picks['pick_side'] == 'FAVORITE'])
    dog_picks = calc_record(picks[picks['pick_side'] == 'UNDERDOG'])
    
    # By home/away (all games in dataset)
    all_games = merged_df[merged_df['pick_side'] != 'NO BET']
    fav_home = calc_record(all_games[all_games['Fav. At Home?'] == 1])
    fav_away = calc_record(all_games[all_games['Fav. At Home?'] == 0])
    
    # By pick + location
    pfh = calc_record(picks[(picks['pick_side'] == 'FAVORITE') & (picks['Fav. At Home?'] == 1)])
    pfa = calc_record(picks[(picks['pick_side'] == 'FAVORITE') & (picks['Fav. At Home?'] == 0)])
    pda = calc_record(picks[(picks['pick_side'] == 'UNDERDOG') & (picks['Fav. At Home?'] == 0)])
    pdh = calc_record(picks[(picks['pick_side'] == 'UNDERDOG') & (picks['Fav. At Home?'] == 1)])
    
    return {
        'fav_picks': fav_picks,
        'dog_picks': dog_picks,
        'fav_home': fav_home,
        'fav_away': fav_away,
        'pfh': pfh,
        'pfa': pfa,
        'pda': pda,
        'pdh': pdh
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
        
        # Extract model probabilities (3 models: Logistic, Linear, RF)
        logistic_prob = pred.get('logistic_probability', np.nan)
        linear_prob = pred.get('linear_probability', np.nan)
        rf_prob = pred.get('random_forest_probability', np.nan)
        
        # Average valid model probabilities
        probs = [logistic_prob, linear_prob, rf_prob]
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
            'fav_at_home': int(game_row.get('Fav. At Home?', 1)),  # Include home/away status
            'logistic_prob': logistic_prob,
            'linear_prob': linear_prob,
            'rf_prob': rf_prob,
            'num_models': len(valid_probs),
            'averaged_fav_prob': averaged_fav_prob,
            'averaged_dog_prob': averaged_dog_prob,
            'standardized_fav': standardized_fav,
            'standardized_dog': standardized_dog,
            'pick_side': pick_side,
            'pick_team': pick_team,
            'pick_line': pick_line,
            'edge': edge,
            'cover_prob': cover_prob,
            'fav_edge': fav_edge,
            'dog_edge': dog_edge
        })
    
    return predictions


def get_social_logo_base64(icon_name):
    """Get base64-encoded social media logo."""
    logo_path = f'social_logos/{icon_name}.svg'
    if not os.path.exists(logo_path):
        return ''
    with open(logo_path, 'rb') as f:
        logo_data = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/svg+xml;base64,{logo_data}'


def format_email_html(predictions, yesterday_results, season_record, date_str):
    """Format predictions and results into HTML email with team logos."""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=League+Gothic&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'League Gothic', Arial, sans-serif; background-color: #2a2a2a; padding: 10px; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 10px; }}
            .header {{ text-align: center; border-bottom: 3px solid #9a29e9; padding-bottom: 20px; margin-bottom: 20px; }}
            .record {{ font-size: 20px; font-weight: bold; color: #000000; text-align: center; margin: 20px 0; line-height: 1.6; }}
            .section {{ margin: 20px 0; }}
            .section-title {{ font-size: 24px; font-weight: bold; color: #000000; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }}
            .pick {{ background-color: #e5e5e5; padding: 25px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #9a29e9; }}
            .pick-content {{ display: table; width: 100%; }}
            .pick-left {{ display: table-cell; vertical-align: middle; width: 55%; white-space: nowrap; }}
            .pick-right {{ display: table-cell; vertical-align: middle; width: 45%; text-align: left; border-left: 2px solid #999; padding-left: 15px; }}
            .pick-right-container {{ display: table; width: 100%; }}
            .pick-stats {{ display: table-cell; vertical-align: middle; text-align: left; padding-right: 15px; width: 70%; }}
            .pick-spread-cell {{ display: table-cell; vertical-align: middle; text-align: right; width: 30%; }}
            .pick-emoji {{ font-size: 48px; display: inline-block; vertical-align: middle; margin-right: 15px; }}
            .pick-logo {{ width: 70px; height: 70px; vertical-align: middle; margin-right: 15px; }}
            .pick-team {{ font-size: 40px; font-weight: bold; display: inline-block; vertical-align: middle; white-space: nowrap; }}
            .pick-matchup {{ font-size: 16px; color: #666; margin-top: 5px; font-family: Arial, sans-serif; }}
            .pick-spread-box {{ background-color: #9a29e9; color: white; padding: 10px 14px; border-radius: 6px; font-size: 24px; font-weight: bold; display: inline-block; min-width: 55px; text-align: center; }}
            .pick-stat {{ color: #222; font-size: 18px; font-family: Arial, sans-serif; margin-bottom: 5px; font-weight: 500; }}
            .result-win {{ background-color: #e8f5e9; border-left-color: #4caf50; }}
            .result-loss {{ background-color: #ffebee; border-left-color: #f44336; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; font-size: 12px; color: #777; }}
            .logo {{ width: 50px; height: 50px; vertical-align: middle; margin-right: 12px; }}
            .ad-section {{ text-align: center; margin: 20px 0; padding: 15px; background-color: #ffffff; border-radius: 8px; font-family: Arial, sans-serif; }}
            .ad-image {{ max-width: 600px; width: 100%; height: auto; display: block; margin: 0 auto; }}
            .ad-image-spacing {{ margin-bottom: 15px; }}
            .ad-text {{ font-size: 14px; color: #000000; line-height: 1.6; margin: 15px auto; max-width: 600px; padding: 0 10px; }}
            .split-item {{ margin: 12px 0; font-size: 14px; line-height: 1.8; font-family: Arial, sans-serif; }}
            .splits-section {{ font-family: Arial, sans-serif; }}
            .split-row {{ background-color: #f0f0f0; padding: 20px; margin: 12px 0; border-radius: 8px; border-left: 4px solid #9a29e9; }}
            .split-content {{ display: table; width: 100%; }}
            .split-left {{ display: table-cell; vertical-align: middle; width: 35%; font-size: 20px; font-weight: bold; color: #000000; text-align: center; }}
            .split-right {{ display: table-cell; vertical-align: middle; width: 65%; text-align: left; border-left: 2px solid #9a29e9; padding-left: 20px; }}
            .split-data {{ font-size: 16px; line-height: 2.0; color: #333; white-space: nowrap; }}
            .game-summary-row {{ background-color: #f0f0f0; padding: 20px; margin: 12px 0; border-radius: 8px; border-left: 4px solid #9a29e9; }}
            .game-summary-item {{ font-size: 18px; padding: 10px 0; border-bottom: 2px solid #ddd; }}
            .game-summary-item:last-child {{ border-bottom: none; }}
            .game-summary-label {{ font-weight: bold; color: #000000; }}
            .game-summary-value {{ color: #333; margin-left: 10px; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; font-size: 12px; color: #777; font-family: Arial, sans-serif; }}
            @media only screen and (max-width: 600px) {{
                body {{ padding: 5px; }}
                .container {{ padding: 15px; }}
                .header h1 {{ font-size: 20px; margin: 10px 0; }}
                .header p {{ font-size: 14px; }}
                .header div {{ font-size: 16px !important; }}
                .record {{ font-size: 16px; }}
                .section-title {{ font-size: 16px; }}
                .pick-team {{ font-size: 24px; }}
                .pick-matchup {{ font-size: 14px; }}
                .pick-spread-box {{ font-size: 18px; padding: 6px 12px; }}
                .pick-stat {{ font-size: 15px; margin-bottom: 8px; color: #222; font-weight: 500; }}
                .pick-emoji {{ font-size: 36px; }}
                .pick-logo {{ width: 50px; height: 50px; }}
                .split-item {{ font-size: 13px; line-height: 1.9; }}
                .logo {{ width: 35px; height: 35px; }}
                
                /* Stack split layout on mobile with better spacing */
                .split-row {{ padding: 12px; margin: 8px 0; }}
                .split-content {{ display: block !important; }}
                .split-left {{ display: block !important; width: 100% !important; text-align: center; margin-bottom: 8px; font-size: 15px; }}
                .split-right {{ display: block !important; width: 100% !important; border-left: none !important; padding-left: 0 !important; border-top: 2px solid #ddd; padding-top: 8px; text-align: center; }}
                .split-data {{ font-size: 13px; line-height: 1.6; white-space: normal; overflow-wrap: break-word; }}
                .split-data strong {{ display: block; margin-top: 5px; white-space: nowrap; }}
                
                /* Game summary mobile styles */
                .game-summary-row {{ padding: 15px; }}
                .game-summary-item {{ font-size: 16px; padding: 8px 0; }}
                
                /* Stack pick layout on mobile */
                .pick {{ padding: 15px; }}
                .pick-content {{ display: block !important; }}
                .pick-left {{ display: block !important; width: 100% !important; margin-bottom: 10px; text-align: center; white-space: normal !important; }}
                .pick-middle {{ display: block !important; width: 100% !important; text-align: center; margin-bottom: 15px; padding: 0; }}
                .pick-right {{ display: block !important; width: 100% !important; border-left: none !important; padding-left: 0 !important; border-top: 2px solid #ddd; padding-top: 15px; text-align: center; }}
                .pick-right-inner {{ display: block !important; text-align: center; }}
                .pick-stats {{ display: block !important; padding-right: 0 !important; margin-bottom: 10px; text-align: center; }}
                .pick-spread-cell {{ display: block !important; text-align: center !important; }}
                .pick-spread-box {{ display: inline-block; width: fit-content; margin: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏀 NBA PREDICTIONS - {date_str}</h1>
                <div style="font-size: 20px; color: #000000; font-weight: bold; margin-top: 10px;">Presented by: Orb Analytics Ltd.</div>
                <div style="margin-top: 10px;">
                    <img src="cid:orb_logo" alt="Orb Analytics" style="max-width: 200px; height: auto; display: block; margin: 0 auto;" />
                </div>
                
                <!-- Follow us text -->
                <div style="text-align: center; margin-top: 20px; font-size: 20px; font-weight: bold; color: #000000;">
                    Follow us on social media!
                </div>
                
                <!-- Social Media Icons (from Stripo, converted to standard HTML) -->
                <table role="presentation" cellpadding="0" cellspacing="0" align="center" style="margin: 15px auto 0; background-color: #f0f0f0; border-radius: 8px; padding: 15px;">
                    <tr>
                        <td valign="top" align="center" style="padding: 0 10px;">
                            <a target="_blank" href="https://orbanalytics.substack.com/">
                                <img height="32" title="Substack" src="https://cdn.simpleicons.org/substack/FF6719" alt="Substack" width="32" style="display:block;border:0;" />
                            </a>
                        </td>
                        <td align="center" valign="top" style="padding: 0 10px;">
                            <a href="https://www.tiktok.com/@orb.analytics" target="_blank">
                                <img alt="TikTok" width="32" height="32" title="TikTok" src="https://ezfbzub.stripocdn.email/content/assets/img/social-icons/logo-colored/tiktok-logo-colored.png" style="display:block;border:0;" />
                            </a>
                        </td>
                        <td align="center" valign="top" style="padding: 0 10px;">
                            <a target="_blank" href="https://www.instagram.com/orb.analytics/">
                                <img width="32" height="32" title="Instagram" src="https://ezfbzub.stripocdn.email/content/assets/img/social-icons/logo-colored/instagram-logo-colored.png" alt="Instagram" style="display:block;border:0;" />
                            </a>
                        </td>
                        <td align="center" valign="top" style="padding: 0 10px;">
                            <a target="_blank" href="https://www.youtube.com/@OrbAnalyticsLimited">
                                <img title="YouTube" src="https://ezfbzub.stripocdn.email/content/assets/img/social-icons/logo-colored/youtube-logo-colored.png" alt="YouTube" width="32" height="32" style="display:block;border:0;" />
                            </a>
                        </td>
                        <td align="center" valign="top" style="padding: 0 10px;">
                            <a href="https://x.com/OrbPicks" target="_blank">
                                <img width="32" height="32" title="X" src="https://ezfbzub.stripocdn.email/content/assets/img/social-icons/logo-colored/x-logo-colored.png" alt="X" style="display:block;border:0;" />
                            </a>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div class="record">
                SEASON RECORD: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)<br>
                Units: {season_record['units']:+.2f} | ROI: {season_record['roi']:+.2f}%
            </div>
    """
    
    # Today's Picks FIRST
    html += """
        <div class="section">
            <div class="section-title">🎯 TODAY'S PICKS</div>
    """
    
    picks = [p for p in predictions if p['pick_side'] != 'NO BET']
    
    if not picks:
        html += "<p>⚪ No picks today - no games meet the 3% edge threshold</p>"
    else:
        picks_sorted = sorted(picks, key=lambda x: x['edge'], reverse=True)
        
        for pick in picks_sorted:
            pick_team = pick['pick_team']
            favorite = pick['favorite']
            underdog = pick['underdog']
            logo_url = get_team_logo_url(pick_team)
            
            # Determine opponent and home/away
            if pick['pick_side'] == 'FAVORITE':
                opponent = underdog
                is_home = pick.get('fav_at_home', 1) == 1
                spread_line = f"{-pick['spread']:+.1f}"
                pick_odds = pick['fav_odds']
                cover_prob = pick.get('standardized_fav', 0.5)
            else:
                opponent = favorite
                is_home = pick.get('fav_at_home', 1) == 0
                spread_line = f"{pick['spread']:+.1f}"
                pick_odds = pick['dog_odds']
                cover_prob = pick.get('standardized_dog', 0.5)
            
            location_str = "vs" if is_home else "@"
            
            html += f"""
                <div class="pick">
                    <div class="pick-content">
                        <div class="pick-left">
                            <img src="{logo_url}" class="pick-logo">
                            <div style="display: inline-block; vertical-align: middle;">
                                <div class="pick-team">{pick_team}</div>
                                <div class="pick-matchup">{location_str} {opponent}</div>
                            </div>
                        </div>
                        <div class="pick-right">
                            <div class="pick-right-container">
                                <div class="pick-stats">
                                    <div class="pick-stat">Odds: <strong>{format_american_odds(pick_odds)}</strong></div>
                                    <div class="pick-stat">Cover Prob: <strong>{cover_prob:.1%}</strong></div>
                                    <div class="pick-stat">Edge: <strong>{pick['edge']:.1%}</strong></div>
                                </div>
                                <div class="pick-spread-cell">
                                    <span class="pick-spread-box">{spread_line}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """
    
    html += f"""
            </div>
            
            <div class="game-summary-row" style="font-family: Arial, sans-serif; margin-top: 20px;">
                <div class="game-summary-item">
                    <span class="game-summary-label">Total Games Today:</span>
                    <span class="game-summary-value">{len(predictions)}</span>
                </div>
                <div class="game-summary-item">
                    <span class="game-summary-label">Picks Made:</span>
                    <span class="game-summary-value">{len(picks)}</span>
                </div>
                <div class="game-summary-item">
                    <span class="game-summary-label">No Bets:</span>
                    <span class="game-summary-value">{len(predictions) - len(picks)}</span>
                </div>
            </div>
            
            <div style="text-align: center; margin: 20px 0; font-family: Arial, sans-serif;">
                <p style="margin-top: 20px;">Model: 35% Averaged Models + 65% Implied Odds<br>
                Minimum Edge: 3.0%</p>
            </div>
    """
    
    # Yesterday's Results
    if yesterday_results:
        wins = sum(1 for r in yesterday_results if r['result'] == 'WIN')
        losses = sum(1 for r in yesterday_results if r['result'] == 'LOSS')
        yesterday_units = sum(r.get('units', 0.0) for r in yesterday_results)
        
        html += """
            <div class="section">
                <div class="section-title">📅 YESTERDAY'S RESULTS</div>
        """
        
        for result in yesterday_results:
            result_class = "result-win" if result['result'] == 'WIN' else "result-loss"
            emoji = "✅" if result['result'] == 'WIN' else "❌"
            
            pick_team = result['pick_team']
            favorite = result['favorite']
            underdog = result['underdog']
            logo_url = get_team_logo_url(pick_team)
            
            # Determine opponent and home/away
            if result['pick_side'] == 'FAVORITE':
                opponent = underdog
                is_home = result.get('fav_at_home', 1) == 1
                spread_line = f"{-result['spread']:+.1f}"
                pick_odds = result.get('fav_odds', -110)
            else:
                opponent = favorite
                is_home = result.get('fav_at_home', 1) == 0
                spread_line = f"{result['spread']:+.1f}"
                pick_odds = result.get('dog_odds', -110)
            
            location_str = "vs" if is_home else "@"
            units = result.get('units', 0.0)
            
            html += f"""
                <div class="pick {result_class}">
                    <div class="pick-content">
                        <div class="pick-left">
                            <span class="pick-emoji">{emoji}</span>
                            <img src="{logo_url}" class="pick-logo">
                            <div style="display: inline-block; vertical-align: middle;">
                                <div class="pick-team">{pick_team}</div>
                                <div class="pick-matchup">{location_str} {opponent}</div>
                            </div>
                        </div>
                        <div class="pick-right">
                            <div class="pick-right-container">
                                <div class="pick-stats">
                                    <div class="pick-stat">Odds: <strong>{format_american_odds(pick_odds)}</strong></div>
                                    <div class="pick-stat">Edge: <strong>{result['edge']:.1%}</strong></div>
                                    <div class="pick-stat">Units: <strong>{units:+.2f}</strong></div>
                                </div>
                                <div class="pick-spread-cell">
                                    <span class="pick-spread-box">{spread_line}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """
        
        html += f"<p style='text-align: center; font-weight: bold; margin-top: 20px; font-size: 20px;'>Record: {wins}-{losses} | Units: {yesterday_units:+.2f}</p></div>"
    
    # Novig Ad Section
    html += """
        <div class="ad-section">
            <a href="https://apps.apple.com/us/app/novig/id6443958997" target="_blank">
                <img src="cid:novig_ad" class="ad-image ad-image-spacing" alt="Novig - Download Now">
            </a>
            <p class="ad-text">
                🚀 Sign up today & use code <strong>'ORB'</strong> for $50 in bonuses when you spend $5<br><br>
                🔥 Play Smarter with Novig – America's #1 Sports Prediction Market 🔥<br><br>
                ✅ Better Odds – Play against real users, with no house cut (VIG)
            </p>
        </div>
    """
    
    # Add performance splits
    splits = get_performance_splits()
    if splits:
        html += f"""
                <div style="font-size: 18px; font-weight: bold; color: #000000; margin-bottom: 15px; text-align: center;">PERFORMANCE SPLITS</div>
                
                <div class="split-row">
                    <div class="split-content">
                        <div class="split-left">Favorites vs<br>Underdogs</div>
                        <div class="split-right">
                            <div class="split-data">
                                Picking Favorites: <strong>{splits['fav_picks']['wins']}-{splits['fav_picks']['losses']} ({splits['fav_picks']['pct']:.1f}%)</strong> → <strong>{splits['fav_picks']['units']:+.2f} units</strong>
                            </div>
                            <div class="split-data" style="margin-top: 10px;">
                                Picking Underdogs: <strong>{splits['dog_picks']['wins']}-{splits['dog_picks']['losses']} ({splits['dog_picks']['pct']:.1f}%)</strong> → <strong>{splits['dog_picks']['units']:+.2f} units</strong>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="split-row">
                    <div class="split-content">
                        <div class="split-left">Favorite at Home<br>vs Favorite Away</div>
                        <div class="split-right">
                            <div class="split-data">
                                Favorite at Home: <strong>{splits['fav_home']['wins']}-{splits['fav_home']['losses']} ({splits['fav_home']['pct']:.1f}%)</strong> → <strong>{splits['fav_home']['units']:+.2f} units</strong>
                            </div>
                            <div class="split-data" style="margin-top: 10px;">
                                Favorite Away: <strong>{splits['fav_away']['wins']}-{splits['fav_away']['losses']} ({splits['fav_away']['pct']:.1f}%)</strong> → <strong>{splits['fav_away']['units']:+.2f} units</strong>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="split-row">
                    <div class="split-content">
                        <div class="split-left" style="font-size: 24px;">By Pick +<br>Location:</div>
                        <div class="split-right">
                            <div class="split-data">
                                Picking Favorite at Home: <strong>{splits['pfh']['wins']}-{splits['pfh']['losses']} ({splits['pfh']['pct']:.1f}%)</strong> → <strong>{splits['pfh']['units']:+.2f} units</strong>
                            </div>
                            <div class="split-data" style="margin-top: 10px;">
                                Picking Favorite Away: <strong>{splits['pfa']['wins']}-{splits['pfa']['losses']} ({splits['pfa']['pct']:.1f}%)</strong> → <strong>{splits['pfa']['units']:+.2f} units</strong>
                            </div>
                            <div class="split-data" style="margin-top: 10px;">
                                Picking Underdog Away: <strong>{splits['pda']['wins']}-{splits['pda']['losses']} ({splits['pda']['pct']:.1f}%)</strong> → <strong>{splits['pda']['units']:+.2f} units</strong>
                            </div>
                            <div class="split-data" style="margin-top: 10px;">
                                Picking Underdog at Home: <strong>{splits['pdh']['wins']}-{splits['pdh']['losses']} ({splits['pdh']['pct']:.1f}%)</strong> → <strong>{splits['pdh']['units']:+.2f} units</strong>
                            </div>
                        </div>
                    </div>
                </div>
        """
    
    html += f"""
            <div class="footer">
                <div class="section-title">DISCLAIMER:</div>
                <p>The information provided on this website is for informational purposes only. It is not intended to be gambling or financial advice, and should not be relied upon as such. We are not responsible for any actions or decisions taken by readers based on the information provided on this website.</p>
                
                <p>The picks and predictions provided on this website are based on our own research and analysis, and are intended to be used for entertainment and informational purposes only. We do not guarantee the accuracy or completeness of the information provided, and we are not responsible for any losses or damages incurred as a result of using this information for gambling or other purposes.</p>
                
                <p>By accessing and using this website, you acknowledge and agree to the terms of this disclaimer, and you assume all risks and liabilities associated with your use of the information provided on this website.</p>
                
                <p><strong>Season Record: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%) | ROI: {season_record['roi']:+.2f}%</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def format_email_html_all_logos(predictions, yesterday_results, season_record, date_str):
    """Format predictions and results into HTML email with ALL team names replaced by logos."""
    
    def team_logo_html(team_name, show_name=True):
        """Generate HTML for a team logo with optional name."""
        logo_url = get_team_logo_url(team_name)
        if show_name:
            return f'<img src="{logo_url}" class="logo"> {team_name}'
        else:
            return f'<img src="{logo_url}" class="logo" title="{team_name}">'
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
            .header {{ text-align: center; border-bottom: 3px solid: #9a29e9; padding-bottom: 20px; margin-bottom: 20px; }}
            .record {{ font-size: 24px; font-weight: bold; color: #9a29e9; text-align: center; margin: 20px 0; }}
            .section {{ margin: 30px 0; }}
            .section-title {{ font-size: 20px; font-weight: bold; color: #9a29e9; padding-bottom: 10px; margin-bottom: 15px; }}
            .pick {{ background-color: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #9a29e9; }}
            .pick-header {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
            .pick-details {{ margin-left: 20px; color: #555; }}
            .result-win {{ background-color: #e8f5e9; border-left-color: #4caf50; }}
            .result-loss {{ background-color: #ffebee; border-left-color: #f44336; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd; font-size: 12px; color: #777; }}
            .logo {{ width: 30px; height: 30px; vertical-align: middle; margin: 0 4px; }}
            .vs {{ color: #999; margin: 0 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏀 NBA PREDICTIONS - {date_str}</h1>
            </div>
            
            <div class="record">
                SEASON RECORD: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)<br>
                💰 Units: {season_record['units']:+.2f}
            </div>
    """
    
    # Today's Picks
    html += """
        <div class="section">
            <div class="section-title">🎯 TODAY'S PICKS</div>
    """
    
    picks = [p for p in predictions if p['pick_side'] != 'NO BET']
    
    if not picks:
        html += "<p>⚪ No picks today - no games meet the 3% edge threshold</p>"
    else:
        picks_sorted = sorted(picks, key=lambda x: x['edge'], reverse=True)
        
        for pick in picks_sorted:
            pick_team = pick['pick_team']
            favorite = pick['favorite']
            underdog = pick['underdog']
            
            if pick['pick_side'] == 'FAVORITE':
                pick_line = f"{team_logo_html(pick_team)} {pick['pick_line']:+.1f}"
                pick_odds = pick['fav_odds']
            else:
                pick_line = f"{team_logo_html(pick_team)} {pick['pick_line']:+.1f}"
                pick_odds = pick['dog_odds']
            
            matchup_str = f"{team_logo_html(favorite, show_name=False)} <span class='vs'>vs</span> {team_logo_html(underdog, show_name=False)}"
            
            html += f"""
                <div class="pick">
                    <div class="pick-header">
                        {pick_line}
                    </div>
                    <div class="pick-details">
                        {matchup_str}<br>
                        Novig Odds: {format_american_odds(pick_odds)}<br>
                        Orb Cover Probability: {pick['cover_prob']:.1%}<br>
                        Edge: {pick['edge']:.1%}
                    </div>
                </div>
            """
    
    html += f"""
            </div>
        """
    
    # Yesterday's Results
    if yesterday_results:
        wins = sum(1 for r in yesterday_results if r['result'] == 'WIN')
        losses = sum(1 for r in yesterday_results if r['result'] == 'LOSS')
        yesterday_units = sum(r.get('units', 0.0) for r in yesterday_results)
        
        html += """
            <div class="section">
                <div class="section-title">📅 YESTERDAY'S RESULTS</div>
        """
        
        for result in yesterday_results:
            result_class = "result-win" if result['result'] == 'WIN' else "result-loss"
            emoji = "✅" if result['result'] == 'WIN' else "❌"
            
            pick_team = result['pick_team']
            favorite = result['favorite']
            underdog = result['underdog']
            
            if result['pick_side'] == 'FAVORITE':
                pick_str = f"{team_logo_html(pick_team)} {-result['spread']:+.1f}"
            else:
                pick_str = f"{team_logo_html(pick_team)} {result['spread']:+.1f}"
            
            matchup_str = f"{team_logo_html(favorite, show_name=False)} <span class='vs'>vs</span> {team_logo_html(underdog, show_name=False)}"
            
            units = result.get('units', 0.0)
            html += f"""
                <div class="pick {result_class}">
                    <div class="pick-header">
                        {emoji} {pick_str}
                    </div>
                    <div class="pick-details">
                        {matchup_str}<br>
                        Edge: {result['edge']:.1%} | Units: {units:+.2f}
                    </div>
                </div>
            """
        
        html += f"<p style='text-align: center; font-weight: bold; margin-top: 20px;'>Record: {wins}-{losses} | Units: {yesterday_units:+.2f}</p></div>"
    
    # Add performance splits
    splits = get_performance_splits()
    if splits:
        html += f"""
                <div style="font-size: 16px; font-weight: bold; color: #9a29e9; margin-bottom: 10px;">PERFORMANCE SPLITS</div>
                
                <div style="margin-bottom: 10px;">
                    <strong>By Pick Type:</strong><br>
                    • Picking Favorites: {splits['fav_picks']['wins']}-{splits['fav_picks']['losses']} ({splits['fav_picks']['pct']:.1f}%) | {splits['fav_picks']['units']:+.2f} units<br>
                    • Picking Underdogs: {splits['dog_picks']['wins']}-{splits['dog_picks']['losses']} ({splits['dog_picks']['pct']:.1f}%) | {splits['dog_picks']['units']:+.2f} units
                </div>
                
                <div style="margin-bottom: 10px;">
                    <strong>By Home/Away (All Games):</strong><br>
                    • Favorite at Home: {splits['fav_home']['wins']}-{splits['fav_home']['losses']} ({splits['fav_home']['pct']:.1f}%) | {splits['fav_home']['units']:+.2f} units<br>
                    • Favorite Away: {splits['fav_away']['wins']}-{splits['fav_away']['losses']} ({splits['fav_away']['pct']:.1f}%) | {splits['fav_away']['units']:+.2f} units
                </div>
                
                <div>
                    <strong>By Pick + Location:</strong><br>
                    • Picking Favorite at Home: {splits['pfh']['wins']}-{splits['pfh']['losses']} ({splits['pfh']['pct']:.1f}%) | {splits['pfh']['units']:+.2f} units<br>
                    • Picking Favorite Away: {splits['pfa']['wins']}-{splits['pfa']['losses']} ({splits['pfa']['pct']:.1f}%) | {splits['pfa']['units']:+.2f} units<br>
                    • Picking Underdog Away: {splits['pda']['wins']}-{splits['pda']['losses']} ({splits['pda']['pct']:.1f}%) | {splits['pda']['units']:+.2f} units<br>
                    • Picking Underdog at Home: {splits['pdh']['wins']}-{splits['pdh']['losses']} ({splits['pdh']['pct']:.1f}%) | {splits['pdh']['units']:+.2f} units
                </div>
        """
            
    html += f"""
            <div style="text-align: center; margin: 30px 0;">
                <p><strong>Total Games Today:</strong> {len(predictions)}</p>
                <p><strong>Picks Made:</strong> {len(picks)}</p>
                <p><strong>No Bets:</strong> {len(predictions) - len(picks)}</p>
                <p style="margin-top: 20px;">Model: 35% Averaged Models + 65% Implied Odds<br>
                Minimum Edge: 3.0%</p>
            </div>
            
            <div class="footer">
                <div class="section-title">DISCLAIMER:</div>
                <p>The information provided on this website is for informational purposes only. It is not intended to be gambling or financial advice, and should not be relied upon as such. We are not responsible for any actions or decisions taken by readers based on the information provided on this website.</p>
                
                <p>The picks and predictions provided on this website are based on our own research and analysis, and are intended to be used for entertainment and informational purposes only. We do not guarantee the accuracy or completeness of the information provided, and we are not responsible for any losses or damages incurred as a result of using this information for gambling or other purposes.</p>
                
                <p>By accessing and using this website, you acknowledge and agree to the terms of this disclaimer, and you assume all risks and liabilities associated with your use of the information provided on this website.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def format_email(predictions, yesterday_results, season_record, date_str):
    """Format predictions and results into email body."""
    
    lines = []
    lines.append("="*100)
    lines.append(f"🏀 NBA PREDICTIONS - {date_str}")
    lines.append("="*100)
    lines.append("")
    
    # Season Record
    lines.append("SEASON RECORD")
    lines.append(f"   {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)")
    lines.append(f"   Units: {season_record['units']:+.2f}")
    lines.append("")
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
                pick_odds = pick['fav_odds']
            else:
                pick_line = f"{pick['pick_team']} {pick['pick_line']:+.1f}"
                pick_odds = pick['dog_odds']
            
            lines.append(f"🏀 {pick_line} ({pick['favorite']} vs {pick['underdog']})")
            lines.append(f"   Novig Odds: {format_american_odds(pick_odds)}")
            lines.append(f"   Orb Cover Probability: {pick['cover_prob']:.1%}")
            lines.append(f"   Edge: {pick['edge']:.1%}")
            lines.append("")
    
    lines.append("="*100)
    
    # Yesterday's Results (if any)
    if yesterday_results:
        lines.append("")
        lines.append("📅 YESTERDAY'S RESULTS")
        lines.append("="*100)
        
        wins = sum(1 for r in yesterday_results if r['result'] == 'WIN')
        losses = sum(1 for r in yesterday_results if r['result'] == 'LOSS')
        yesterday_units = sum(r.get('units', 0.0) for r in yesterday_results)
        
        for result in yesterday_results:
            emoji = "✅" if result['result'] == 'WIN' else "❌" if result['result'] == 'LOSS' else "⏳"
            
            if result['pick_side'] == 'FAVORITE':
                pick_str = f"{result['pick_team']} {-result['spread']:+.1f}"
            else:
                pick_str = f"{result['pick_team']} {result['spread']:+.1f}"
            
            units = result.get('units', 0.0)
            lines.append(f"{emoji} {pick_str}")
            lines.append(f"   {result['favorite']} vs {result['underdog']}")
            lines.append(f"   Edge: {result['edge']:.1%} | Units: {units:+.2f}")
            lines.append("")
        
        lines.append(f"Record: {wins}-{losses} | Units: {yesterday_units:+.2f}")
        lines.append("="*100)
    
    # Add performance splits
    splits = get_performance_splits()
    if splits:
        lines.append("")
        lines.append("PERFORMANCE SPLITS")
        lines.append("="*100)
        lines.append("")
        lines.append("**By Pick Type:**")
        lines.append(f"- Picking Favorites: {splits['fav_picks']['wins']}-{splits['fav_picks']['losses']} ({splits['fav_picks']['pct']:.1f}%) | {splits['fav_picks']['units']:+.2f} units")
        lines.append(f"- Picking Underdogs: {splits['dog_picks']['wins']}-{splits['dog_picks']['losses']} ({splits['dog_picks']['pct']:.1f}%) | {splits['dog_picks']['units']:+.2f} units")
        lines.append("")
        lines.append("**By Home/Away (All Games):**")
        lines.append(f"- Favorite at Home: {splits['fav_home']['wins']}-{splits['fav_home']['losses']} ({splits['fav_home']['pct']:.1f}%) | {splits['fav_home']['units']:+.2f} units")
        lines.append(f"- Favorite Away: {splits['fav_away']['wins']}-{splits['fav_away']['losses']} ({splits['fav_away']['pct']:.1f}%) | {splits['fav_away']['units']:+.2f} units")
        lines.append("")
        lines.append("**By Pick + Location:**")
        lines.append(f"- Picking Favorite at Home: {splits['pfh']['wins']}-{splits['pfh']['losses']} ({splits['pfh']['pct']:.1f}%) | {splits['pfh']['units']:+.2f} units")
        lines.append(f"- Picking Favorite Away: {splits['pfa']['wins']}-{splits['pfa']['losses']} ({splits['pfa']['pct']:.1f}%) | {splits['pfa']['units']:+.2f} units")
        lines.append(f"- Picking Underdog Away: {splits['pda']['wins']}-{splits['pda']['losses']} ({splits['pda']['pct']:.1f}%) | {splits['pda']['units']:+.2f} units")
        lines.append(f"- Picking Underdog at Home: {splits['pdh']['wins']}-{splits['pdh']['losses']} ({splits['pdh']['pct']:.1f}%) | {splits['pdh']['units']:+.2f} units")
        lines.append("")
        lines.append("="*100)
    
    lines.append("")
    lines.append(f"Total Games Today: {len(predictions)}")
    lines.append(f"Picks Made: {len(picks)}")
    lines.append(f"No Bets: {len(predictions) - len(picks)}")
    lines.append("")
    lines.append("Model: 35% Averaged Models + 65% Implied Odds")
    lines.append("Minimum Edge: 3.0%")
    lines.append("")
    lines.append("="*100)
    lines.append("DISCLAIMER:")
    lines.append("="*100)
    lines.append("")
    lines.append("The information provided on this website is for informational purposes only. It is not")
    lines.append("intended to be gambling or financial advice, and should not be relied upon as such. We are")
    lines.append("not responsible for any actions or decisions taken by readers based on the information")
    lines.append("provided on this website.")
    lines.append("")
    lines.append("The picks and predictions provided on this website are based on our own research and")
    lines.append("analysis, and are intended to be used for entertainment and informational purposes only.")
    lines.append("We do not guarantee the accuracy or completeness of the information provided, and we are")
    lines.append("not responsible for any losses or damages incurred as a result of using this information")
    lines.append("for gambling or other purposes.")
    lines.append("")
    lines.append("By accessing and using this website, you acknowledge and agree to the terms of this")
    lines.append("disclaimer, and you assume all risks and liabilities associated with your use of the")
    lines.append("information provided on this website.")
    lines.append("")
    lines.append("="*100)
    
    return "\n".join(lines)


def load_email_subscribers(subscribers_file='data/email_subscribers.txt'):
    """Load email subscribers from file."""
    if not os.path.exists(subscribers_file):
        print(f"⚠️  Subscriber file not found: {subscribers_file}")
        print("   Falling back to default recipients")
        return ['lpchaitin@gmail.com']
    
    try:
        with open(subscribers_file, 'r') as f:
            emails = [line.strip() for line in f if line.strip() and '@' in line]
        
        if not emails:
            print(f"⚠️  No valid emails in {subscribers_file}")
            return ['lpchaitin@gmail.com']
        
        return emails
    except Exception as e:
        print(f"⚠️  Error reading subscriber file: {e}")
        return ['lpchaitin@gmail.com']


def send_email_html(subject, html_body, predictions=None, yesterday_results=None, test_mode=False):
    """Send HTML email (logos loaded from ESPN CDN, Novig ads attached).
    
    Args:
        test_mode: If True, only send to lpchaitin@gmail.com. If False, send to all recipients.
    """
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not all([smtp_server, smtp_username, smtp_password]):
        print("⚠️ SMTP credentials not configured - email not sent")
        return False
    
    # Determine recipients based on mode
    if test_mode:
        recipients = 'lpchaitin@gmail.com'
        print("🧪 TEST MODE: Sending only to lpchaitin@gmail.com")
    else:
        # Load subscribers from file
        subscriber_list = load_email_subscribers()
        recipients = ','.join(subscriber_list)
        print(f"📧 PRODUCTION MODE: Sending to {len(subscriber_list)} subscribers")
        print(f"   Loaded from data/email_subscribers.txt")
    
    # Create multipart message for embedded images
    msg = MIMEMultipart('related')
    msg['From'] = smtp_username
    msg['To'] = smtp_username  # Show sender in To field
    msg['Bcc'] = recipients
    msg['Subject'] = subject
    
    # Attach HTML body
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    # Attach Orb Analytics logo
    try:
        with open('Novig_logos/Orb_logo.png', 'rb') as f:
            img_data = f.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<orb_logo>')
        image.add_header('Content-Disposition', 'inline', filename='orb_logo.png')
        msg.attach(image)
        print("✅ Orb logo attached")
    except Exception as e:
        print(f"⚠️  Could not attach Orb logo: {e}")
    
    # Attach Novig ad images
    try:
        with open('Novig_logos/novig-5for50-ORB.png', 'rb') as f:
            img_data = f.read()
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<novig_ad>')
        image.add_header('Content-Disposition', 'inline', filename='novig-5for50-ORB.png')
        msg.attach(image)
        
        print("✅ Novig ad images attached")
    except Exception as e:
        print(f"⚠️  Could not attach Novig images: {e}")
    
    # Send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print("✅ HTML email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_email(subject, body):
    """Send plain text email via SMTP (legacy function)."""
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not all([smtp_server, smtp_username, smtp_password]):
        print("⚠️ SMTP credentials not configured - email not sent")
        return False
    
    # Load subscribers from file
    subscriber_list = load_email_subscribers()
    recipients = ','.join(subscriber_list)
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = smtp_username  # Show sender in To field
    msg['Bcc'] = recipients
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


def save_predictions_to_history(predictions, date_str, history_path='data/averaged_model_predictions_history.csv'):
    """
    Save today's predictions to history file immediately after generation.
    
    This ensures the predictions_history file only contains games that were actually
    predicted and emailed, preventing phantom picks from appearing in backtests.
    """
    if not predictions:
        print("⚠️  No predictions to save")
        return
    
    # Convert predictions to DataFrame with all necessary columns
    # Model probabilities are already included in the predictions dict
    new_rows = []
    for pred in predictions:
        new_rows.append({
            'date': date_str,
            'favorite': pred['favorite'],
            'underdog': pred['underdog'],
            'spread': pred['spread'],
            'fav_odds': pred['fav_odds'],
            'dog_odds': pred['dog_odds'],
            'fav_at_home': pred.get('fav_at_home', 1),  # Include home/away status
            'logistic_prob': pred.get('logistic_prob', np.nan),
            'linear_prob': pred.get('linear_prob', np.nan),
            'rf_prob': pred.get('rf_prob', np.nan),
            'num_models': pred.get('num_models', 0),
            'averaged_fav_prob': pred.get('averaged_fav_prob', np.nan),
            'averaged_dog_prob': pred.get('averaged_dog_prob', np.nan),
            'standardized_fav': pred.get('standardized_fav', np.nan),
            'standardized_dog': pred.get('standardized_dog', np.nan),
            'fav_edge': pred['fav_edge'],
            'dog_edge': pred['dog_edge'],
            'pick_side': pred['pick_side'],
            'pick_team': pred['pick_team'],
            'edge': pred['edge'],
            # Note: actual_cover and result will be filled in later by backtest
            'actual_cover': np.nan,
            'result': 'PENDING'
        })
    
    new_df = pd.DataFrame(new_rows)
    
    # Append to history file
    if os.path.exists(history_path):
        history_df = pd.read_csv(history_path)
        # Remove any existing predictions for this date (in case of re-run)
        history_df = history_df[history_df['date'] != date_str]
        # Append new predictions
        updated_df = pd.concat([history_df, new_df], ignore_index=True)
        updated_df = updated_df.sort_values('date').reset_index(drop=True)
        updated_df.to_csv(history_path, index=False)
        print(f"📚 Saved {len(new_df)} predictions to history: {history_path}")
    else:
        new_df.to_csv(history_path, index=False)
        print(f"📚 Created new history file with {len(new_df)} predictions: {history_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate and email averaged model predictions')
    parser.add_argument('--date', type=str, default=None,
                       help='Date to predict (YYYY-MM-DD, default: today)')
    parser.add_argument('--no-email', action='store_true',
                       help='Skip sending email')
    parser.add_argument('--test-mode', action='store_true',
                       help='Send email only to lpchaitin@gmail.com (for testing)')
    
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
    yesterday_results, yesterday_units = get_yesterday_results(yesterday_date=yesterday_str)
    print(f"   Found {len(yesterday_results)} picks from yesterday")
    if yesterday_results:
        print(f"   Yesterday's Units: {yesterday_units:+.2f}")
    
    # Get season record
    print("📊 Loading season record...")
    season_record = get_season_record()
    print(f"   Season: {season_record['wins']}-{season_record['losses']} ({season_record['win_pct']:.1f}%)")
    print(f"   Total Units: {season_record['units']:+.2f}")
    
    # Generate today's predictions
    print(f"🎯 Generating predictions for {today_str}...")
    predictions = generate_averaged_predictions(today_str)
    print(f"   Generated {len(predictions)} predictions")
    picks = [p for p in predictions if p['pick_side'] != 'NO BET']
    print(f"   Picks: {len(picks)}")
    print()
    
    # Save predictions to history immediately (before backtest runs)
    # This ensures only games that were actually predicted/emailed are in the history
    save_predictions_to_history(predictions, today_str)
    
    # Format HTML email with team logos
    html_body = format_email_html(predictions, yesterday_results, season_record, today_str)
    
    # Also generate plain text for console preview
    text_body = format_email(predictions, yesterday_results, season_record, today_str)
    
    print("="*100)
    print("EMAIL PREVIEW (Plain Text):")
    print("="*100)
    print(text_body)
    print("="*100)
    print()
    
    # Send HTML email with embedded logos
    if not args.no_email:
        # Add timestamp to subject to prevent Gmail threading when sending multiple times
        timestamp = datetime.now().strftime('%I:%M%p')
        subject = f"🏀 NBA Predictions - {today_str} [{timestamp}]"
        send_email_html(subject, html_body, predictions, yesterday_results)
    else:
        print("⚠️ Email sending skipped (--no-email flag)")
    
    # Verify game matchup consistency (after email, before X posting)
    print("\n" + "="*100)
    print("🔍 POST-EMAIL VERIFICATION: Checking game matchup consistency...")
    print("="*100)
    verification_passed = verify_games(today_str, verbose=True)
    
    if not verification_passed:
        print("\n⚠️  WARNING: Game verification failed!")
        print("This may indicate duplicate or incorrect data was used for predictions.")
        print("Review the data sources before posting to X/Twitter.")
    else:
        print("\n✅ Verification passed - safe to proceed with X posting")


if __name__ == "__main__":
    main()
