# 🎾 Tennis Court Monitor - User Instructions

## 🚀 Quick Start

Your tennis court monitoring system is **ready to go**! It automatically checks for available courts every 30 minutes and notifies you when slots become available.

### ✅ **System Status**
- **✅ Installed and configured**
- **✅ Runs every 30 minutes automatically** 
- **✅ Monitors today's date automatically**
- **✅ Sends notifications when courts are found**

---

## 📱 **How You'll Get Notified**

When tennis courts become available, you'll receive:
- **📧 Email notification** (if configured)
- **📲 Pushover notification** (if configured) 
- **📝 Log entry** (always)

**Example notification:**
```
🎾 Tennis Court Available at Islington Tennis Centre!

⏰ 14:00 - 15:00 | 💰 £12.35 | 🏟️ 2 spaces | 🔗 [booking link]
⏰ 16:00 - 17:00 | 💰 £12.35 | 🏟️ 1 spaces | 🔗 [booking link]

Checked at: 2025-08-30 14:07:31
```

---

## 💻 **Laptop Requirements**

### **⚠️ IMPORTANT: Sleep Behavior**
- **✅ Cron jobs resume automatically** when you wake your laptop
- **❌ Cron jobs pause** when laptop is closed/sleeping
- **✅ No reconfiguration needed** after waking up

### **📅 What This Means:**
```
2:00 PM - Script runs ✅
2:30 PM - Script runs ✅  
3:00 PM - You close laptop 💤
3:30 PM - (missed - laptop sleeping)
4:15 PM - You open laptop 🔋
4:30 PM - Script runs ✅ (automatically resumes)
```

### **💡 Best Practices:**
- Keep laptop plugged in when possible
- Check status when you wake up your laptop
- Consider leaving laptop open during peak booking times

---

## 🔧 **Daily Management Commands**

### **📊 Check System Status**
```bash
cd /Users/samszamocki/Documents/Tennis_booking_automation
./monitor_status.sh
```
Shows: cron job status, recent activity, next run time

### **👀 Watch Live Activity**
```bash
./watch_live.sh
```
Shows real-time monitoring (Press Ctrl+C to stop)

### **🔄 Run Manual Check**
```bash
source venv/bin/activate && python watcher.py
```
Immediately check for courts (doesn't affect scheduled runs)

### **📋 View Recent Logs**
```bash
tail -20 monitor.log
```
See the last 20 log entries

---

## 🎯 **What the System Monitors**

- **🏟️ Venue:** Islington Tennis Centre - Highbury Tennis
- **📅 Date:** Always checks TODAY's date automatically
- **⏰ Times:** All available time slots (6am - 10pm)
- **🔄 Frequency:** Every 30 minutes
- **🎾 Activity:** Tennis court bookings only

---

## 🛠️ **Troubleshooting**

### **❓ "Is it working?"**
```bash
./monitor_status.sh
```
This shows you everything you need to know.

### **❓ "No notifications received?"**
1. Check if courts are actually available (they might all be booked)
2. Verify email/Pushover settings in `.env` file
3. Check `monitor.log` for any error messages

### **❓ "Missed some runs?"**
- Normal if laptop was closed/sleeping
- System automatically resumes when laptop wakes up
- No action needed

### **❓ "Want to stop monitoring?"**
```bash
crontab -e
# Delete the line containing "watcher.py"
```

### **❓ "Script errors?"**
```bash
tail -50 monitor.log
```
Look for error messages and check internet connection.

---

## 📧 **Notification Setup**

### **Email Notifications**
Edit `.env` file:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password  # Use Gmail App Password!
EMAIL_TO=your_notification_email@gmail.com
```

### **Pushover Notifications** 
Edit `.env` file:
```bash
PUSHOVER_USER_KEY=your_user_key
PUSHOVER_API_TOKEN=your_api_token
```
Sign up at [pushover.net](https://pushover.net) (~$5 one-time)

---

## 🔄 **System Behavior**

### **Normal Operation:**
- Runs every 30 minutes automatically
- Usually finds "No available slots" (this is normal!)
- Logs each check with timestamp
- Only sends notifications when courts are found

### **When Courts Are Found:**
- 🎾 Immediate notification sent
- 📝 Detailed log entry created
- 🔗 Direct booking links provided
- ⚡ **Act fast** - courts get booked quickly!

### **Automatic Features:**
- ✅ Handles cookie popups
- ✅ Updates date daily
- ✅ Manages browser sessions
- ✅ Recovers from minor errors

---

## 📈 **Monitoring Stats**

Check your monitoring effectiveness:
```bash
# Total monitoring runs
grep -c "Starting Better tennis court monitor" monitor.log

# Courts found
grep -c "FOUND.*AVAILABLE SLOT" monitor.log

# Success rate
grep -c "Check completed" monitor.log
```

---

## ⚡ **Quick Reference**

| Command | Purpose |
|---------|---------|
| `./monitor_status.sh` | Check system status |
| `./watch_live.sh` | Watch real-time activity |
| `tail -f monitor.log` | View live logs |
| `python watcher.py` | Manual check |
| `crontab -l` | View scheduled jobs |

---

## 🎯 **Success Tips**

1. **📱 Set up notifications** - You'll miss opportunities without them
2. **🔋 Keep laptop plugged in** - Prevents unexpected sleep
3. **📊 Check status daily** - Especially after waking laptop
4. **⚡ Act quickly** - Courts get booked within minutes of becoming available
5. **🕐 Peak times** - Most cancellations happen in the evening before the next day

---

## 🆘 **Need Help?**

1. **Check status first:** `./monitor_status.sh`
2. **View recent logs:** `tail -20 monitor.log`
3. **Test manually:** `python watcher.py`
4. **Check internet connection**
5. **Verify `.env` file settings**

**Remember:** The system works by detecting cancellations, so notifications are rare but valuable! 🎾
