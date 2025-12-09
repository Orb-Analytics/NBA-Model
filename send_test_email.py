"""
Send test email with today's predictions
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import subprocess

def send_test_email():
    """Send a test email with today's predictions."""
    
    # Get predictions
    date = datetime.now().strftime('%Y-%m-%d')
    print(f"📧 Generating predictions for {date}...")
    
    # Run the predictions script
    result = subprocess.run(
        ['python', 'src/email_predictions.py', date],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error generating predictions: {result.stderr}")
        return False
    
    predictions_text = result.stdout
    
    # Get SMTP credentials from environment
    smtp_user = os.environ.get('SMTP_USERNAME')
    smtp_pass = os.environ.get('SMTP_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    
    if not smtp_user or not smtp_pass:
        print("❌ Missing SMTP credentials. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables")
        return False
    
    # Recipients
    to_emails = ['lpchaitin@gmail.com', 'eborsook@gmail.com', 'benitesa192@gmail.com']
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🏀 TEST - NBA Ensemble Predictions - {date}"
    msg['From'] = smtp_user
    msg['To'] = ', '.join(to_emails)
    
    # Email body
    body = f"""TEST EMAIL - NBA Ensemble Model Predictions

This is a test of the new 4-model prediction system with daily updated records.

────────────────────────────────────────────────────────────────────

{predictions_text}

────────────────────────────────────────────────────────────────────

This was a test email. Future emails will be sent automatically.

Good luck! 🍀
"""
    
    text_part = MIMEText(body, 'plain')
    msg.attach(text_part)
    
    # Send email
    try:
        print(f"📤 Sending test email to {len(to_emails)} recipients...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Test email sent successfully!")
        print(f"   Recipients: {', '.join(to_emails)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    send_test_email()
