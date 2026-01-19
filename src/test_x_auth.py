#!/usr/bin/env python3
"""
Test X API Authentication
"""

import os
import tweepy


def test_authentication():
    """Test X API authentication."""
    print("=" * 80)
    print("🔐 TESTING X API AUTHENTICATION")
    print("=" * 80)
    print()
    
    # Check for credentials
    api_key = os.environ.get('X_API_KEY')
    api_secret = os.environ.get('X_API_SECRET_KEY')
    access_token = os.environ.get('X_ACCESS_TOLKEN')
    access_token_secret = os.environ.get('X_ACCESS_TOLKEN_SECRET')
    
    print("Checking environment variables:")
    print(f"  X_API_KEY: {'✓ Found' if api_key else '✗ Missing'}")
    print(f"  X_API_SECRET_KEY: {'✓ Found' if api_secret else '✗ Missing'}")
    print(f"  X_ACCESS_TOLKEN: {'✓ Found' if access_token else '✗ Missing'}")
    print(f"  X_ACCESS_TOLKEN_SECRET: {'✓ Found' if access_token_secret else '✗ Missing'}")
    print()
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ Missing required credentials")
        print()
        print("ℹ️  Note: Repository secrets are only available in GitHub Actions workflows.")
        print("   To test locally, you need to set these as environment variables:")
        print()
        print("   export X_API_KEY='your_key'")
        print("   export X_API_SECRET_KEY='your_secret'")
        print("   export X_ACCESS_TOLKEN='your_token'")
        print("   export X_ACCESS_TOLKEN_SECRET='your_token_secret'")
        return False
    
    # Attempt authentication
    print("Attempting authentication...")
    try:
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret,
            access_token, access_token_secret
        )
        api = tweepy.API(auth)
        
        # Verify credentials
        user = api.verify_credentials()
        
        print()
        print("=" * 80)
        print("✅ AUTHENTICATION SUCCESSFUL!")
        print("=" * 80)
        print()
        print(f"Authenticated as: @{user.screen_name}")
        print(f"Name: {user.name}")
        print(f"Followers: {user.followers_count}")
        print(f"Following: {user.friends_count}")
        print(f"Tweets: {user.statuses_count}")
        print()
        print("=" * 80)
        
        return True
        
    except tweepy.Unauthorized as e:
        print()
        print("=" * 80)
        print("❌ AUTHENTICATION FAILED - Unauthorized")
        print("=" * 80)
        print()
        print("This usually means:")
        print("  • Invalid API credentials")
        print("  • Incorrect access token or secret")
        print("  • App permissions not properly configured")
        print()
        print(f"Error details: {e}")
        return False
        
    except tweepy.TweepyException as e:
        print()
        print("=" * 80)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        return False
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ UNEXPECTED ERROR")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = test_authentication()
    exit(0 if success else 1)
