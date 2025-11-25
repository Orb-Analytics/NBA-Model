# 100% Free Notification Setup Guide

## Option 1: Email-to-SMS (Free SMS via Email)

### Setup (5 minutes):
1. **Enable Gmail App Password**:
   - Go to Google Account → Security → 2-Step Verification (turn on if not already)
   - Search "App passwords" 
   - Create new app password for "Mail"
   - Save the 16-character password

2. **Find your carrier's SMS gateway**:
   - Verizon: `phonenumber@vtext.com`
   - AT&T: `phonenumber@txt.att.net`
   - T-Mobile: `phonenumber@tmomail.net`
   - Sprint: `phonenumber@messaging.sprintpcs.com`

3. **Add to GitHub Secrets**:
   - `GMAIL_ADDRESS` - your Gmail address
   - `GMAIL_APP_PASSWORD` - the 16-char password
   - `PHONE_NUMBER` - your 10-digit phone (no +1)
   - `CARRIER` - your carrier (verizon, att, tmobile, etc.)

**Pros**: True SMS to your phone, no new apps  
**Cons**: 160 character limit, basic text only

---

## Option 2: Discord Webhook (Recommended - Easiest)

### Setup (2 minutes):
1. **Create Discord server** (if you don't have one):
   - Open Discord → Click "+" → Create My Own → Skip template
   - Name it "NBA Predictions"

2. **Create Webhook**:
   - Click channel settings (gear icon) → Integrations → Webhooks
   - Click "New Webhook"
   - Name it "NBA Bot"
   - Copy webhook URL

3. **Add to GitHub Secrets**:
   - `DISCORD_WEBHOOK_URL` - the URL you copied

**Pros**: Unlimited free, rich formatting, mobile notifications  
**Cons**: Requires Discord app

---

## Option 3: Telegram Bot (Best for Mobile)

### Setup (3 minutes):
1. **Create bot**:
   - Open Telegram
   - Search for `@BotFather`
   - Send `/newbot`
   - Name it "NBA Predictions Bot"
   - Username: `your_nba_predictions_bot`
   - Copy the bot token

2. **Get your Chat ID**:
   - Search for `@userinfobot` in Telegram
   - Start chat - it will reply with your Chat ID

3. **Add to GitHub Secrets**:
   - `TELEGRAM_BOT_TOKEN` - token from BotFather
   - `TELEGRAM_CHAT_ID` - your chat ID

**Pros**: Instant mobile push, unlimited free, great formatting  
**Cons**: Requires Telegram app

---

## My Recommendation

**Start with Discord** - it's the easiest and most reliable:
1. Takes 2 minutes to set up
2. Works on phone and desktop
3. Rich formatting (colors, bold, etc.)
4. Completely unlimited and free forever
5. Can share with friends easily

Then add **Telegram** if you want cleaner mobile notifications.

Skip email-to-SMS unless you really want actual SMS texts.

---

## Quick Test

Once you add secrets, go to:
- Actions → "Test Free Notifications" → Run workflow

You'll get test messages on all configured platforms!
