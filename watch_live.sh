#!/bin/bash
# Tennis Court Monitor - Live Log Viewer

echo "🎾 Tennis Court Monitor - Live Activity"
echo "======================================"
echo "Press Ctrl+C to stop watching"
echo ""

# Create log file if it doesn't exist
touch monitor.log

# Watch the log file in real-time
tail -f monitor.log
