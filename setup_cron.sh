#!/bin/bash
# Tennis Court Monitor - Cron Setup Script

echo "🎾 Setting up Tennis Court Monitor to run every 30 minutes..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the cron job entry - runs every 30 minutes on Friday, Saturday, Sunday only
CRON_JOB="*/30 * * * 5,6,0 cd $SCRIPT_DIR && /bin/bash -c 'source venv/bin/activate && python watcher.py' >> $SCRIPT_DIR/monitor.log 2>&1"

# Add to crontab
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"
echo ""
echo "📋 Cron job details:"
echo "   - Runs every 30 minutes on Friday, Saturday, Sunday only"
echo "   - Checks all 3 weekend dates (Fri/Sat/Sun)"
echo "   - Sends Telegram notifications when slots found"
echo "   - Logs to: $SCRIPT_DIR/monitor.log"
echo "   - Script location: $SCRIPT_DIR"
echo ""
echo "🔍 To check if it's working:"
echo "   tail -f $SCRIPT_DIR/monitor.log"
echo ""
echo "🗑️  To remove the cron job later:"
echo "   crontab -e  # then delete the tennis monitor line"
echo ""
echo "⚠️  IMPORTANT: Your laptop must be powered on and awake for this to work!"
