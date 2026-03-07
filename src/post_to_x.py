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
    access_token = os.environ.get('X_ACCESS_TOLKEN')
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
    
    # Skip get_me() verification - requires paid API tier
    # Credentials will be verified when posting tweets
    print("✅ X API client created successfully")
    return client


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
    """Format a single pick for tweeting (shortened - no opponent)."""
    # Determine matchup and odds
    if pick['pick_side'] == 'FAVORITE':
        pick_team = pick['favorite']
        line = -abs(pick['spread'])
        odds = pick.get('fav_odds', -110)
    else:
        pick_team = pick['underdog']
        line = abs(pick['spread'])
        odds = pick.get('dog_odds', -110)
    
    # Format edge and odds
    edge = pick['edge'] * 100
    odds_str = f"{int(odds):+d}" if odds == int(odds) else f"{odds:+.0f}"
    
    # Create tweet text (no opponent to save characters)
    tweet = f"🏀 {pick_team} {line:+.1f} ({odds_str}, {edge:.1f}%)\n"
    
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


def create_results_tweets(yesterdays_df, date, wins, losses, units):
    """Create tweet(s) for yesterday's results and season record. Returns a list of tweets."""
    win_pct = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # Use 260 as limit to account for emoji overhead (Twitter counts many emojis as 2 chars)
    TWITTER_LIMIT = 260
    footer = "\n#NBA #SportsBetting"
    
    # Header with date and record
    header = f"🏀 {datetime.strptime(date, '%Y-%m-%d').strftime('%b %d')}\n\n"
    header += f"📊 {wins}-{losses} ({win_pct:.1f}%, {units:+.1f}u)\n\n"
    
    # Handle no results case
    if len(yesterdays_df) == 0:
        tweet = header + "No games yesterday" + footer
        return [tweet]
    
    # Build results tweets (may need to split if many results)
    tweets = []
    current_tweet = header + "Yesterday's Results:\n"
    
    for i, (idx, result) in enumerate(yesterdays_df.iterrows()):
        result_text = format_result_tweet(result)
        
        # Check if adding this result would exceed limit
        potential_tweet = current_tweet + result_text + footer
        if len(potential_tweet) > TWITTER_LIMIT:
            # Save current tweet and start a new one
            tweets.append(current_tweet.rstrip('\n') + footer)
            current_tweet = result_text
        else:
            current_tweet += result_text
    
    # Add the last tweet
    if current_tweet:
        tweets.append(current_tweet.rstrip('\n') + footer)
    
    return tweets


def create_results_tweet(yesterdays_df, date, wins, losses, units):
    """Create tweet for yesterday's results (backward compatibility - returns first tweet only)."""
    tweets = create_results_tweets(yesterdays_df, date, wins, losses, units)
    return tweets[0] if tweets else "🏀 No games yesterday\n\n#NBA #SportsBetting"


def create_picks_tweets(picks_df):
    """Create tweet(s) for today's picks. Returns a list of tweets."""
    # Handle no picks case
    if len(picks_df) == 0:
        return ["🏀 No picks today\n\n#NBA #SportsBetting"]
    
    tweets = []
    current_tweet = "🏀 Today's Picks:\n\n"
    footer = "\n#NBA #SportsBetting"
    
    # Use 260 as limit to account for emoji overhead (Twitter counts many emojis as 2 chars)
    TWITTER_LIMIT = 260
    
    for i, (idx, pick) in enumerate(picks_df.iterrows()):
        pick_text = format_pick_tweet(pick)
        
        # Check if adding this pick would exceed limit
        potential_tweet = current_tweet + pick_text + footer
        if len(potential_tweet) > TWITTER_LIMIT:
            # Save current tweet and start a new one
            tweets.append(current_tweet.rstrip('\n') + footer)
            current_tweet = pick_text
        else:
            current_tweet += pick_text
    
    # Add the last tweet
    if current_tweet:
        tweets.append(current_tweet.rstrip('\n') + footer)
    
    return tweets


def create_picks_tweet(picks_df):
    """Create tweet for today's picks (backward compatibility - returns first tweet only)."""
    tweets = create_picks_tweets(picks_df)
    return tweets[0] if tweets else "🏀 No picks today\n\n#NBA #SportsBetting"


def post_predictions(test_mode=False):
    """Post today's predictions to X as a multi-tweet thread."""
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
    
    # Create tweets
    results_tweets = create_results_tweets(yesterdays_df, date, wins, losses, units)
    picks_tweets = create_picks_tweets(picks_df)
    
    # Display all tweets that will be posted
    tweet_num = 1
    for i, results_tweet in enumerate(results_tweets):
        print("\n" + "=" * 80)
        if len(results_tweets) > 1:
            print(f"TWEET {tweet_num} - RESULTS & RECORD ({i+1}/{len(results_tweets)}):")
        else:
            print(f"TWEET {tweet_num} - RESULTS & RECORD:")
        print("=" * 80)
        print(results_tweet)
        print("=" * 80)
        print(f"Character count: {len(results_tweet)}")
        print("=" * 80)
        tweet_num += 1
    
    for i, picks_tweet in enumerate(picks_tweets):
        print("\n" + "=" * 80)
        print(f"TWEET {tweet_num} - TODAY'S PICKS ({i+1}/{len(picks_tweets)}):")
        print("=" * 80)
        print(picks_tweet)
        print("=" * 80)
        print(f"Character count: {len(picks_tweet)}")
        print("=" * 80)
        tweet_num += 1
    
    if test_mode:
        print("\n⚠️  TEST MODE - Tweets not posted")
        return
    
    # Authenticate and post
    try:
        client = authenticate_x_api()
        last_tweet_id = None
        tweet_num = 1
        
        # Post results tweets
        for i, results_tweet in enumerate(results_tweets):
            if i == 0:
                print(f"\n📤 Posting Tweet {tweet_num} (Results & Record)...")
                response = client.create_tweet(text=results_tweet)
            else:
                print(f"\n📤 Posting Tweet {tweet_num} (Results continued {i+1}/{len(results_tweets)}) as reply...")
                response = client.create_tweet(
                    text=results_tweet,
                    in_reply_to_tweet_id=last_tweet_id
                )
            
            last_tweet_id = response.data['id']
            print(f"✅ Tweet {tweet_num} posted successfully!")
            print(f"🔗 Tweet ID: {last_tweet_id}")
            tweet_num += 1
        
        # Post pick tweets as replies
        for i, picks_tweet in enumerate(picks_tweets):
            print(f"\n📤 Posting Tweet {tweet_num} (Picks {i+1}/{len(picks_tweets)}) as reply...")
            response = client.create_tweet(
                text=picks_tweet,
                in_reply_to_tweet_id=last_tweet_id
            )
            last_tweet_id = response.data['id']
            print(f"✅ Tweet {tweet_num} posted successfully!")
            print(f"🔗 Tweet ID: {last_tweet_id}")
            tweet_num += 1
        
        print(f"\n🎉 Thread complete! ({len(results_tweets) + len(picks_tweets)} tweets)")
        
    except Exception as e:
        error_msg = str(e)
        if "duplicate content" in error_msg.lower():
            print(f"\n⚠️  Skipping post - already posted today (duplicate content)")
            print("This is expected if the workflow runs multiple times per day")
            return  # Exit gracefully without error
        elif "403" in error_msg or "401" in error_msg or "unauthorized" in error_msg.lower():
            print(f"\n❌ Authentication Error: {e}")
            print("\n🔧 Troubleshooting:")
            print("• Check X Developer Portal for app permissions ('Read and Write')")
            print("• Regenerate tokens after changing permissions")
            print("• Update GitHub secrets with new tokens")
            raise
        elif "503" in error_msg:
            print(f"\n❌ X API Service Error: {e}")
            print("• X/Twitter API may be temporarily down")
            print("• Try again in a few minutes")
            raise
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
