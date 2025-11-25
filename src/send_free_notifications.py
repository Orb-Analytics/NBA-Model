"""
Free Notification Methods - No paid services required
Author: Orb Analytics (Liam Chaitin)
Purpose: Send predictions via free methods (Email-to-SMS, Discord, Telegram)
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_to_sms(phone_number, carrier, message, gmail_address, gmail_app_password):
    """
    Send SMS via email-to-SMS gateway (100% free).
    
    Args:
        phone_number: 10-digit phone number (e.g., '1234567890')
        carrier: Carrier name ('verizon', 'att', 'tmobile', 'sprint')
        message: Message text
        gmail_address: Your Gmail address
        gmail_app_password: Gmail app-specific password
    """
    # Carrier gateway mappings
    gateways = {
        'verizon': 'vtext.com',
        'att': 'txt.att.net',
        'tmobile': 'tmomail.net',
        'sprint': 'messaging.sprintpcs.com',
        'boost': 'sms.myboostmobile.com',
        'cricket': 'sms.cricketwireless.net',
        'uscellular': 'email.uscc.net'
    }
    
    if carrier.lower() not in gateways:
        print(f"❌ Unsupported carrier. Supported: {', '.join(gateways.keys())}")
        return False
    
    # Create SMS email address
    sms_address = f"{phone_number}@{gateways[carrier.lower()]}"
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_address
        msg['To'] = sms_address
        msg['Subject'] = ''  # Empty subject for cleaner SMS
        
        # Truncate message to 160 characters for SMS
        if len(message) > 160:
            message = message[:157] + "..."
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Send via Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ SMS sent via email to {sms_address}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email-to-SMS: {e}")
        return False


def send_discord_webhook(webhook_url, message, title="🏀 NBA Predictions"):
    """
    Send message to Discord channel (100% free, unlimited).
    
    Args:
        webhook_url: Discord webhook URL
        message: Message text
        title: Embed title
    """
    try:
        # Create Discord embed for rich formatting
        data = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 0x1d428a,  # NBA blue
                "footer": {
                    "text": "Orb Analytics NBA Predictions"
                }
            }]
        }
        
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            print("✅ Discord notification sent successfully")
            return True
        else:
            print(f"❌ Discord webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")
        return False


def send_telegram_message(bot_token, chat_id, message):
    """
    Send message via Telegram bot (100% free, instant).
    
    Args:
        bot_token: Telegram bot token from @BotFather
        chat_id: Your Telegram chat ID
        message: Message text (supports Markdown)
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully")
            return True
        else:
            print(f"❌ Telegram failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


def main():
    """Test all free notification methods."""
    print("🧪 Testing Free Notification Methods\n")
    
    # Test Email-to-SMS
    print("1️⃣ Email-to-SMS Test")
    print("-" * 50)
    gmail = os.environ.get('GMAIL_ADDRESS')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    phone = os.environ.get('PHONE_NUMBER')
    carrier = os.environ.get('CARRIER', 'verizon')
    
    if gmail and gmail_password and phone:
        test_msg = "🏀 NBA Predictions Test - Email to SMS working!"
        send_email_to_sms(phone, carrier, test_msg, gmail, gmail_password)
    else:
        print("⚠️  Set GMAIL_ADDRESS, GMAIL_APP_PASSWORD, PHONE_NUMBER, CARRIER to test\n")
    
    # Test Discord
    print("\n2️⃣ Discord Webhook Test")
    print("-" * 50)
    discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
    
    if discord_webhook:
        test_msg = "🏀 **NBA Predictions Test**\n\nDiscord notifications are working!\n\n✅ Free unlimited messages"
        send_discord_webhook(discord_webhook, test_msg)
    else:
        print("⚠️  Set DISCORD_WEBHOOK_URL to test\n")
    
    # Test Telegram
    print("\n3️⃣ Telegram Bot Test")
    print("-" * 50)
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.environ.get('TELEGRAM_CHAT_ID')
    
    if telegram_token and telegram_chat:
        test_msg = "🏀 *NBA Predictions Test*\n\nTelegram notifications are working!\n\n✅ Free, instant, unlimited"
        send_telegram_message(telegram_token, telegram_chat, test_msg)
    else:
        print("⚠️  Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to test\n")
    
    print("\n" + "=" * 50)
    print("Test complete! Check your notifications.")


if __name__ == "__main__":
    main()
