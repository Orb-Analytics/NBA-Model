#!/usr/bin/env python3
"""
Post NBA Predictions to X (Twitter)
Author: Orb Analytics (Liam Chaitin)
Purpose: Share daily NBA predictions on X/Twitter
"""

import os
import tweepy
from datetime import datetime
import pandas as pd


def authenticate_x_api():
    """Authenticate with X API v2."""
    # Get credentials from environment variables
    api_key = os.environ.get('X_API_KEY')
    api_secret = os.environ.get('X_API_SECRET_KEY')
    access_token = os.environ.get('X_ACCESS_TOLKEN')  # Note: User's typo in secret name
    access_token_secret = os.environ.get('X_ACCESS_TOLKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise Exception("Missing X API credentials in environment variables")
    
    # Create v2 client
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    # Verify credentials
    try:
        user = client.get_me()
        print(f"✅ Authenticated as @{user.data.username}")
        return client
    except Exception as e:
        raise Exception(f"Authentication failed: {e}")


def get_todays_picks(date=None):
    """Get today's picks from predictions history."""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Load predictions
    df = pd.read_csv('data/averaged_model_predictions_history.csv')
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Filter to today's picks
    todays_picks = df[(df['date'] == date) & (df['pick_side'] != 'NO BET')].copy()
    
    return todays_picks, date


def get_yesterdays_results(date=None):
    """Get yesterday's picks and results from backtest."""
    if date is None:
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        from datetime import timedelta
        yesterday = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Load backtest
    backtest = pd.read_csv('data/averaged_model_backtest.csv')
    backtest['date'] = pd.to_datetime(backtest['date']).dt.strftime('%Y-%m-%d')
    
    # Filter to yesterday's picks
    yesterdays_picks = backtest[
        (backtest['date'] == yesterday) & 
        (backtest['pick_side'] != 'NO BET') &
        (backtest['result'].isin(['WIN', 'LOSS']))
    ].copy()
    
    return yesterdays_picks


def get_season_record():
    """Get current season record and units."""
    backtest = pd.read_csv('data/averaged_model_backtest.csv')
    picks = backtest[backtest['pick_side'] != 'NO BET'].copy()
    completed = picks[picks['result'].isin(['WIN', 'LOSS'])]
    
    wins = len(completed[completed['result'] == 'WIN'])
    losses = len(completed[completed['result'] == 'LOSS'])
    
    # Calculate total units
    total_units = 0.0
    for _, row in completed.iterrows():
        # Determine which odds to use
        if row['pick_side'] == 'FAVORITE':
            odds = row.get('fav_odds', -110)
        else:
            odds = row.get('dog_odds', -110)
        
        units = calculate_units(odds, row['result'])
        total_units += units
    
    return wins, losses, total_units


def calculate_units(odds, result):
    """Calculate units won/lost for a bet.
    
    Args:
        odds: American odds (e.g., -110, +150)
        result: 'WIN' or 'LOSS'
    
    Returns:
        float: Units won (positive) or lost (negative)
    """
    if result == 'LOSS':
        return -1.0
    elif result == 'WIN':
        if odds < 0:
            return 100 / abs(odds)
        else:
            return odds / 100
    return 0.0


def format_pick_tweet(pick):
    """Format a single pick for tweeting."""
    # Determine matchup and odds
    if pick['pick_side'] == 'FAVORITE':
        pick_team = pick['favorite']
        opponent = pick['underdog']
        line = -abs(pick['spread'])
        odds = pick.get('fav_odds', -110)
    else:
        pick_team = pick['underdog']
        opponent = pick['favorite']
        line = abs(pick['spread'])
        odds = pick.get('dog_odds', -110)
    
    # Format edge and odds
    edge = pick['edge'] * 100
    odds_str = f"{int(odds):+d}" if odds == int(odds) else f"{odds:+.0f}"
    
    # Create tweet text
    tweet = f"🏀 {pick_team} {line:+.1f} vs {opponent} ({odds_str}, {edge:.1f}%)\n"
    
    return tweet


def format_result_tweet(result):
    """Format yesterday's result for tweeting."""
    # Determine emoji
    emoji = "✅" if result['result'] == 'WIN' else "❌"
    
    # Get pick details
    pick_team = result['pick_team']
    
    if result['pick_side'] == 'FAVORITE':
        line = -abs(result['spread'])
    else:
        line = abs(result['spread'])
    
    return f"{emoji} {pick_team} {line:+.1f}\n"


def create_predictions_tweet(picks_df, yesterdays_df, date, wins, losses, units):
    """Create the main predictions tweet with yesterday's results."""
    win_pct = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # Header with date
    tweet = f"🏀 {datetime.strptime(date, '%Y-%m-%d').strftime('%b %d')}\n\n"
    
    # Record with units
    tweet += f"📊 {wins}-{losses} ({win_pct:.1f}%, {units:+.1f}u)\n\n"
    
    # TODAY'S PICKS
    if len(picks_df) == 0:
        tweet += "No picks today\n\n"
    else:
        tweet += f"Today's Picks:\n"
        
        for idx, pick in picks_df.iterrows():
            pick_text = format_pick_tweet(pick)
            tweet += pick_text
        
        tweet += "\n"
    
    # YESTERDAY'S RESULTS
    if len(yesterdays_df) > 0:
        tweet += "Yesterday:\n"
        
        for idx, result in yesterdays_df.iterrows():
            result_text = format_result_tweet(result)
            
            # Check character limit
            if len(tweet + result_text) > 260:
                remaining = len(yesterdays_df) - idx
                tweet += f"[+{remaining} more]\n"
                break
                
            tweet += result_text
        
        tweet += "\n"
    
    # Footer
    tweet += "#NBA #SportsBetting"
    
    return tweet


def post_predictions(test_mode=False):
    """Post today's predictions to X."""
    print("=" * 80)
    print("🐦 POSTING NBA PREDICTIONS TO X")
    print("=" * 80)
    
    # Get data
    picks_df, date = get_todays_picks()
    yesterdays_df = get_yesterdays_results(date)
    wins, losses, units = get_season_record()
    
    print(f"\n📅 Date: {date}")
    print(f"📊 Record: {wins}-{losses} ({units:+.1f}u)")
    print(f"🎯 Today's Picks: {len(picks_df)}")
    print(f"📋 Yesterday's Results: {len(yesterdays_df)}")
    
    # Create tweet
    tweet = create_predictions_tweet(picks_df, yesterdays_df, date, wins, losses, units)
    
    print("\n" + "=" * 80)
    print("TWEET PREVIEW:")
    print("=" * 80)
    print(tweet)
    print("=" * 80)
    print(f"Character count: {len(tweet)}")
    print("=" * 80)
    
    if test_mode:
        print("\n⚠️  TEST MODE - Tweet not posted")
        return
    
    # Authenticate and post
    try:
        client = authenticate_x_api()
        response = client.create_tweet(text=tweet)
        print(f"\n✅ Tweet posted successfully!")
        print(f"🔗 Tweet ID: {response.data['id']}")
    except Exception as e:
        error_msg = str(e)
        if "duplicate content" in error_msg.lower():
            print(f"\n⚠️  Skipping post - already posted today (duplicate content)")
            print("This is expected if the workflow runs multiple times per day")
            return  # Exit gracefully without error
        else:
            print(f"\n❌ Failed to post tweet: {e}")
            raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Post NBA predictions to X')
    parser.add_argument('--test', action='store_true', help='Test mode - preview only, do not post')
    parser.add_argument('--date', type=str, help='Date to post picks for (YYYY-MM-DD)', default=None)
    
    args = parser.parse_args()
    
    if args.date:
        # Override get_todays_picks to use specified date
        global get_todays_picks
        original_func = get_todays_picks
        def get_todays_picks(date=None):
            return original_func(args.date)
    
    post_predictions(test_mode=args.test)


if __name__ == "__main__":
    main()
