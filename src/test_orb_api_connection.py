#!/usr/bin/env python3
"""
Debug script to test Orb Analytics API connection.
"""

import os
import sys
import requests
import json

def test_connection():
    """Test the API connection and endpoint."""
    
    api_url = os.environ.get('ORB_PLATFORM_URL')
    api_key = os.environ.get('ORB_PLATFORM_KEY')
    
    print("=" * 70)
    print("🔍 Orb Analytics API Connection Test")
    print("=" * 70)
    print()
    
    # Check environment variables
    if not api_url:
        print("❌ ORB_PLATFORM_URL not set")
        return False
    if not api_key:
        print("❌ ORB_PLATFORM_KEY not set")
        return False
    
    print(f"✓ ORB_PLATFORM_URL: {api_url}")
    print(f"✓ ORB_PLATFORM_KEY: {'*' * 20}...{api_key[-4:] if len(api_key) > 4 else '****'}")
    print()
    
    # Test different endpoint variations
    endpoints_to_test = [
        "/predictions/batch",
        "/rest/v1/predictions/batch",
        "/predictions",
        "/rest/v1/predictions",
        "/api/predictions/batch",
        "/api/predictions",
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'apikey': api_key  # Supabase also uses this header
    }
    
    print("Testing endpoints:")
    print("-" * 70)
    
    for endpoint in endpoints_to_test:
        full_url = f"{api_url.rstrip('/')}{endpoint}"
        print(f"\nTesting: {full_url}")
        
        try:
            # Try a simple GET first
            response = requests.get(full_url, headers=headers, timeout=10)
            print(f"  GET Status: {response.status_code}")
            if response.status_code != 404:
                print(f"  Response preview: {response.text[:200]}")
            
            # Try POST with minimal payload
            test_payload = {'predictions': []}
            response = requests.post(full_url, headers=headers, json=test_payload, timeout=10)
            print(f"  POST Status: {response.status_code}")
            if response.status_code != 404:
                print(f"  Response preview: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    print()
    print("=" * 70)
    print("\nWhat's the correct endpoint for your Supabase API?")
    print("Common patterns:")
    print("  - https://yourproject.supabase.co/rest/v1/predictions")
    print("  - https://yourproject.supabase.co/functions/v1/predictions/batch")
    print()

if __name__ == '__main__':
    test_connection()
