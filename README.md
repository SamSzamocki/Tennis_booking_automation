# 🎾 Tennis Court Booking Automation

Automated monitoring system for Better/GLL tennis court availability at Islington Tennis Centre. Gets notified instantly when courts become available due to cancellations.

## 🚀 Features

- **Automated Monitoring**: Checks for available tennis court slots every hour
- **Multiple Notifications**: Email and/or Pushover push notifications
- **Smart Parsing**: Detects court availability from Better's booking system
- **Robust Login**: Handles Better/GLL authentication automatically  
- **Cron Ready**: Designed to run as a scheduled background task
- **Detailed Logging**: Clear output for debugging and monitoring

## 📋 Prerequisites

- Python 3.7+
- Better/GLL account with valid login credentials
- (Optional) Gmail account for email notifications
- (Optional) Pushover account for mobile push notifications

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SamSzamocki/Tennis_booking_automation.git
   cd Tennis_booking_automation
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   python -m playwright install --with-deps
   ```

5. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your credentials (see Configuration section)
   ```

## ⚙️ Configuration

Edit the `.env` file with your settings:

### Required Settings
```bash
# Your Better/GLL login credentials
BETTER_EMAIL=your_email@example.com
BETTER_PASSWORD=your_password

# The specific court booking page to monitor
WATCH_URL=https://bookings.better.org.uk/location/islington-tennis-centre/highbury-tennis/2025-08-24/by-time
```

### Optional Email Notifications
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_sender_email@gmail.com
SMTP_PASS=your_app_password  # Use Gmail App Password, not regular password
EMAIL_TO=your_notification_email@gmail.com
```

**Gmail Setup**: 
1. Enable 2-factor authentication on your Google account
2. Generate an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use the App Password (not your regular password) in `SMTP_PASS`

### Optional Pushover Notifications
```bash
PUSHOVER_USER_KEY=your_user_key
PUSHOVER_API_TOKEN=your_api_token
```

**Pushover Setup**:
1. Sign up at [pushover.net](https://pushover.net) (~$5 one-time fee)
2. Install the Pushover app on your phone
3. Get your User Key and create an API Token from the dashboard

## 🏃‍♂️ Usage

### Manual Run
```bash
# Activate virtual environment
source venv/bin/activate

# Run the monitor once
python watcher.py
```

### Output Examples

**When no courts are available**:
```
Starting Better tennis court monitor at 2024-08-30 14:07:23
Watching URL: https://bookings.better.org.uk/location/islington-tennis-centre/highbury-tennis/2025-08-24/by-time
Navigating to Better booking system...
Filled email field
Filled password field
Clicked submit button
Login completed
Navigating to target page: https://bookings.better.org.uk/location/islington-tennis-centre/highbury-tennis/2025-08-24/by-time
No available slots found
Check completed at 2024-08-30 14:07:31
```

**When courts are found**:
```
🎾 FOUND 2 AVAILABLE SLOT(S)!

============================================================
🎾 Tennis Court Available at Islington Tennis Centre!

⏰ 14:00 - 15:00 | 💰 £12.35 | 🏟️ 2 spaces | 🔗 https://bookings.better.org.uk/location/...
⏰ 16:00 - 17:00 | 💰 £12.35 | 🏟️ 1 spaces | 🔗 https://bookings.better.org.uk/location/...

Checked at: 2024-08-30 14:07:31
Page: https://bookings.better.org.uk/location/islington-tennis-centre/highbury-tennis/2025-08-24/by-time
============================================================
Email notification sent successfully
Pushover notification sent successfully
```

## ⏰ Automated Monitoring (Cron)

To check every hour automatically:

1. **Open crontab**:
   ```bash
   crontab -e
   ```

2. **Add this line** (replace `/path/to/` with your actual path):
   ```bash
   7 * * * * cd /path/to/Tennis_booking_automation && /bin/bash -c 'source venv/bin/activate && python watcher.py' >> monitor.log 2>&1
   ```

   This runs the monitor at 7 minutes past every hour and logs output to `monitor.log`.

3. **Alternative: Run every 30 minutes during peak hours**:
   ```bash
   # Check every 30 minutes between 7 AM and 10 PM
   0,30 7-22 * * * cd /path/to/Tennis_booking_automation && /bin/bash -c 'source venv/bin/activate && python watcher.py' >> monitor.log 2>&1
   ```

## 📅 Updating the Date

The `WATCH_URL` contains a specific date. To monitor different dates:

1. **Manual update**: Edit the `.env` file and change the date in `WATCH_URL`
2. **Script for tomorrow**: Create a simple script to update the URL:
   ```bash
   #!/bin/bash
   # update_date.sh
   TOMORROW=$(date -d "+1 day" +%Y-%m-%d)
   sed -i "s/2025-08-24/$TOMORROW/g" .env
   ```

## 🔧 Troubleshooting

### Common Issues

**Login fails**:
- Verify your Better/GLL credentials are correct
- Check if your account requires 2FA (may need manual intervention)
- Try running with `headless=False` in the script for debugging

**No slots detected**:
- The page structure may have changed - check the HTML parsing logic
- Verify the `WATCH_URL` is correct and accessible
- Run manually to see detailed output

**Email notifications not working**:
- Ensure you're using a Gmail App Password, not your regular password
- Check that 2-factor authentication is enabled on your Google account
- Verify SMTP settings are correct

**Cron job not running**:
- Check cron logs: `grep CRON /var/log/syslog` (Linux) or `log show --predicate 'process == "cron"'` (macOS)
- Ensure full paths are used in the crontab entry
- Check that the virtual environment activates correctly

### Debug Mode

To run with visible browser for debugging:
```python
# In watcher.py, change this line:
browser = playwright.chromium.launch(headless=False)  # Set to False
```

## 📝 Exit Codes

- `0`: No available slots found (normal operation)
- `1`: Available slots found (triggers notifications)
- `2`: Error occurred (configuration or runtime error)

These exit codes are useful for cron job monitoring and alerting.

## ⚖️ Legal & Ethical Considerations

- **Rate Limiting**: The script checks hourly by default to be respectful of Better's servers
- **Terms of Service**: Review Better/GLL's terms of service regarding automated access
- **Personal Use**: This tool is intended for personal use to monitor availability
- **No Auto-booking**: The script only monitors and notifies; it does not automatically book courts

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is for personal use. Please respect Better/GLL's terms of service and use responsibly.