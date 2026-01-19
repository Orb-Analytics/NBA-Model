#!/usr/bin/env python3
"""
Detailed X API Diagnostics
"""

import os
import requests
from requests_oauthlib import OAuth1


def test_oauth1_signature():
    """Test OAuth 1.0a signature generation."""
    print("=" * 80)
    print("🔍 X API DETAILED DIAGNOSTICS")
    print("=" * 80)
    print()
    
    # Get credentials
    api_key = os.environ.get('X_API_KEY')
    api_secret = os.environ.get('X_API_SECRET_KEY')
    access_token = os.environ.get('X_ACCESS_TOLKEN')
    access_token_secret = os.environ.get('X_ACCESS_TOLKEN_SECRET')
    
    # Mask credentials for display
    def mask(s):
        if not s or len(s) < 8:
            return "***"
        return s[:4] + "..." + s[-4:]
    
    print("Credentials (masked):")
    print(f"  API Key: {mask(api_key)}")
    print(f"  API Secret: {mask(api_secret)}")
    print(f"  Access Token: {mask(access_token)}")
    print(f"  Access Token Secret: {mask(access_token_secret)}")
    print()
    
    # Test with requests-oauthlib directly
    print("Testing OAuth 1.0a signature with verify_credentials endpoint...")
    print()
    
    auth = OAuth1(
        api_key,
        api_secret,
        access_token,
        access_token_secret
    )
    
    # Try to verify credentials using API v1.1
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    
    try:
        response = requests.get(url, auth=auth)
        
        print(f"Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("=" * 80)
            print("✅ AUTHENTICATION SUCCESSFUL!")
            print("=" * 80)
            print()
            print(f"Username: @{data.get('screen_name')}")
            print(f"Name: {data.get('name')}")
            print(f"User ID: {data.get('id_str')}")
            return True
        else:
            print("=" * 80)
            print("❌ AUTHENTICATION FAILED")
            print("=" * 80)
            print()
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print()
            
            if response.status_code == 401:
                print("🔧 TROUBLESHOOTING STEPS:")
                print()
                print("1. Verify all 4 credentials are from the SAME X app")
                print("   - Go to https://developer.twitter.com/en/portal/dashboard")
                print("   - Check that API Key and Access Token are from the same project")
                print()
                print("2. Check App Permissions:")
                print("   - App must have 'Read and Write' permissions")
                print("   - If you changed permissions, regenerate Access Token & Secret")
                print()
                print("3. Verify Access Token Type:")
                print("   - Must be 'OAuth 1.0a' User Access Tokens")
                print("   - NOT OAuth 2.0 tokens")
                print()
                print("4. Check if tokens are expired or revoked")
                print()
                print("5. Secret names in GitHub (check for typos):")
                print("   - X_API_KEY")
                print("   - X_API_SECRET_KEY")
                print("   - X_ACCESS_TOLKEN")
                print("   - X_ACCESS_TOLKEN_SECRET")
                
            elif response.status_code == 403:
                print("🔧 This usually means:")
                print("   - App permissions insufficient")
                print("   - Access level is too low (need Elevated access for posting)")
                
            return False
            
    except Exception as e:
        print("=" * 80)
        print("❌ ERROR DURING REQUEST")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = test_oauth1_signature()
    exit(0 if success else 1)
