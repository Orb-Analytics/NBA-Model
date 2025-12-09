"""
Test SMS Sending via Twilio
Author: Orb Analytics (Liam Chaitin)
Purpose: Simple script to test sending SMS notifications
"""

import os
from twilio.rest import Client

def send_test_sms(to_phone, message):
    """
    Send a test SMS using Twilio.
    
    Args:
        to_phone: Phone number to send to (format: +1234567890)
        message: Message text to send
    """
    # Get Twilio credentials from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, from_phone]):
        print("❌ Missing Twilio credentials in environment variables")
        print("Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        return False
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        print(f"✅ SMS sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
        return False


def main():
    """Test sending a simple SMS."""
    # Get recipient phone number from environment or use default
    to_phone = os.environ.get('TEST_PHONE_NUMBER', '+1234567890')
    
    # Test message
    test_message = """🏀 NBA Predictions Test Alert

This is a test message from your NBA prediction bot!

If you received this, SMS notifications are working correctly.

- Orb Analytics"""
    
    print("📱 Testing SMS notification...")
    print(f"To: {to_phone}")
    print(f"Message length: {len(test_message)} characters")
    print("-" * 50)
    
    success = send_test_sms(to_phone, test_message)
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n⚠️  Test failed. Check credentials and try again.")


if __name__ == "__main__":
    main()
