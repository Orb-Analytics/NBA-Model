# SMS and Social Media Integration Setup

## Testing SMS Notifications

### 1. Get Twilio Account (Free Trial)
1. Sign up at https://www.twilio.com/try-twilio
2. You get $15 free credit (enough for ~1,900 SMS messages)
3. Get your credentials from the Twilio Console:
   - Account SID
   - Auth Token
   - Twilio Phone Number

### 2. Add Secrets to GitHub
Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add three secrets:
- `TWILIO_ACCOUNT_SID` - Your Twilio Account SID
- `TWILIO_AUTH_TOKEN` - Your Twilio Auth Token
- `TWILIO_PHONE_NUMBER` - Your Twilio phone number (format: +1234567890)

### 3. Run the Test
1. Go to Actions tab in GitHub
2. Click "📱 Test SMS Notifications" workflow
3. Click "Run workflow"
4. Enter your phone number (format: +1234567890)
5. Click "Run workflow"
6. Check your phone for the test message!

### 4. Local Testing (Optional)
```bash
# Install twilio
pip install twilio

# Set environment variables
export TWILIO_ACCOUNT_SID='your_sid_here'
export TWILIO_AUTH_TOKEN='your_token_here'
export TWILIO_PHONE_NUMBER='+1234567890'
export TEST_PHONE_NUMBER='+1234567890'

# Run test
python src/send_test_sms.py
```

## Next Steps: Social Media Integration

### Twitter/X
- Free API access (Basic tier)
- Need to apply for developer account
- Can post predictions automatically

### Reddit
- Completely free API
- Can post to r/sportsbook or your own subreddit
- No application needed

### Priority
1. ✅ SMS (Twilio) - Simple, instant notifications
2. Reddit - Easy to set up, free
3. Twitter - Requires developer account approval

## Cost Estimate
- **SMS**: ~$0.0079 per message
  - Daily predictions = ~$0.24/month (30 days)
  - Well within free $15 credit
- **Twitter**: Free
- **Reddit**: Free
