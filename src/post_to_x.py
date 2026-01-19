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
    """Authenticate with X API using OAuth 1.0a."""
    # Get credentials from environment variables
    api_key = os.environ.get('X_API_KEY')
    api_secret = os.environ.get('X_API_SECRET_KEY')
    access_token = os.environ.get('X_ACCESS_TOLKEN')  # Note: User's typo in secret name
    access_token_secret = os.environ.get('X_ACCESS_TOLKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        missing = []
        if not api_key: missing.append('X_API_KEY')
        if not api_secret: missing.append('X_API_SECRET_KEY')
        if not access_token: missing.append('X_ACCESS_TOLKEN')
        if not access_token_secret: missing.append('X_ACCESS_TOLKEN_SECRET')
        raise ValueError(f"Missing X API credentials: {', '.join(missing)}")
    
    # Authenticate with OAuth 1.0a
    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret,
        access_token, access_token_secret
    )
    
    # Create API object
    api = tweepy.API(auth)
    
    # Verify credentials
    try:
        user = api.verify_credentials()
        print(f"✅ Authenticated as @{user.screen_name}")
        return api
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


def get_season_record():
    """Get current season record."""
    backtest = pd.read_csv('data/averaged_model_backtest.csv')
    picks = backtest[backtest['pick_side'] != 'NO BET'].copy()
    completed = picks[picks['result'].isin(['WIN', 'LOSS'])]
    
    wins = len(completed[completed['result'] == 'WIN'])
    losses = len(completed[completed['result'] == 'LOSS'])
    
    return wins, losses


def format_pick_tweet(pick):
    """Format a single pick for tweeting."""
    # Determine matchup
    if pick['pick_side'] == 'FAVORITE':
        pick_team = pick['favorite']
        opponent = pick['underdog']
        line = -abs(pick['spread'])
    else:
        pick_team = pick['underdog']
        opponent = pick['favorite']
        line = abs(pick['spread'])
    
    # Format edge
    edge = pick['edge'] * 100
    
    # Create tweet text
    tweet = f"🏀 {pick_team} {line:+.1f}\n"
    tweet += f"vs {opponent}\n"
    tweet += f"Edge: {edge:.1f}%\n"
    
    return tweet


def create_predictions_tweet(picks_df, date, wins, losses):
    """Create the main predictions tweet."""
    win_pct = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # Header
    tweet = f"📊 NBA Predictions - {datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')}\n\n"
    
    # Record
    tweet += f"Season Record: {wins}-{losses} ({win_pct:.1f}%)\n\n"
    
    # Picks
    if len(picks_df) == 0:
        tweet += "No picks today - no edge found above 3% threshold\n\n"
    else:
        tweet += f"Today's Picks ({len(picks_df)}):\n\n"
        
        for idx, pick in picks_df.iterrows():
            pick_text = format_pick_tweet(pick)
            
            # Check if adding this pick would exceed 280 characters
            if len(tweet + pick_text) > 260:  # Leave room for footer
                tweet += f"[+{len(picks_df) - idx} more]\n"
                break
            
            tweet += pick_text + "\n"
    
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
    wins, losses = get_season_record()
    
    print(f"\n📅 Date: {date}")
    print(f"📊 Record: {wins}-{losses}")
    print(f"🎯 Picks: {len(picks_df)}")
    
    # Create tweet
    tweet = create_predictions_tweet(picks_df, date, wins, losses)
    
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
        api = authenticate_x_api()
        status = api.update_status(tweet)
        print(f"\n✅ Tweet posted successfully!")
        print(f"🔗 URL: https://twitter.com/user/status/{status.id}")
    except Exception as e:
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
