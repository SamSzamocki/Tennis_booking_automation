#!/bin/bash
# Tennis Court Monitor - Status Checker

echo "🎾 Tennis Court Monitor Status"
echo "=============================="
echo ""

# Check if cron job exists
echo "📅 Cron Job Status:"
if crontab -l 2>/dev/null | grep -q "watcher.py"; then
    echo "   ✅ Cron job is installed and active"
    echo "   ⏰ Runs every 30 minutes"
else
    echo "   ❌ No cron job found"
    echo "   💡 Run ./setup_cron.sh to install"
fi
echo ""

# Check log file
LOG_FILE="$(pwd)/monitor.log"
echo "📋 Recent Activity:"
if [ -f "$LOG_FILE" ]; then
    echo "   📄 Log file: $LOG_FILE"
    echo "   📊 Total runs: $(grep -c "Starting Better tennis court monitor" "$LOG_FILE" 2>/dev/null || echo "0")"
    echo "   🎾 Courts found: $(grep -c "FOUND.*AVAILABLE SLOT" "$LOG_FILE" 2>/dev/null || echo "0")"
    echo ""
    echo "   🕒 Last 3 runs:"
    grep "Starting Better tennis court monitor\|No available slots found\|FOUND.*AVAILABLE SLOT" "$LOG_FILE" 2>/dev/null | tail -3 | sed 's/^/      /'
else
    echo "   📄 No log file yet (script hasn't run)"
fi
echo ""

# Next run time
echo "⏰ Next Scheduled Run:"
CURRENT_MIN=$(date +%M)
NEXT_30=$((30 - CURRENT_MIN % 30))
if [ $NEXT_30 -eq 30 ]; then
    NEXT_30=0
fi
if [ $NEXT_30 -eq 0 ]; then
    echo "   🚀 Within the next minute!"
else
    echo "   ⏳ In approximately $NEXT_30 minutes"
fi
echo ""

echo "💡 Useful Commands:"
echo "   📖 Watch live: tail -f monitor.log"
echo "   🔄 Manual run: python watcher.py"
echo "   🗑️  Remove cron: crontab -e"
echo "   📊 This status: ./monitor_status.sh"
