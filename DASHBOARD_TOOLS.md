# 🚀 Dashboard Tools - Quick Reference

All three tools are now set up and ready to use!

## ✅ What's Installed

- ✅ **Dashboard running on Pi** (auto-starts on Pi reboot)
- ✅ **Mac control script** - Manage from your Mac
- ✅ **Status checker** - Quick system health check
- ✅ **iOS guide** - Control from iPhone/iPad

---

## 🖥️ Mac Control Script

**Location:** `/Users/kathrynbennett/divinofax/control_dashboard.sh`

### Quick Commands

```bash
# Check if dashboard is running
./control_dashboard.sh status

# Start the dashboard
./control_dashboard.sh start

# Stop the dashboard
./control_dashboard.sh stop

# Restart the dashboard
./control_dashboard.sh restart

# View live logs
./control_dashboard.sh logs

# Open dashboard in your browser
./control_dashboard.sh open

# Test connection to Pi
./control_dashboard.sh test

# Show help
./control_dashboard.sh help
```

### Add to PATH (Optional - makes it global)

```bash
# Copy to a location in your PATH
cp /Users/kathrynbennett/divinofax/control_dashboard.sh /usr/local/bin/divinofax-control
chmod +x /usr/local/bin/divinofax-control

# Then use from anywhere:
divinofax-control status
```

---

## 📊 Status Checker

**Location:** `/Users/kathrynbennett/divinofax/dashboard_status.sh`

### Quick Check

```bash
./dashboard_status.sh
```

**Shows:**
- 🟢/🔴 Service status
- 💾 Memory usage
- 📁 Disk usage
- 📜 Number of recent fortunes
- 🌐 Dashboard URL

### Use Case
Quick health check before/after events or deployment.

---

## 📱 iOS Shortcuts

**Complete guide:** `/Users/kathrynbennett/divinofax/IOS_SHORTCUT_GUIDE.md`

### Three Easy Steps

1. **Open Safari on iPhone**
2. **Go to:** `http://divinofax.local:5000`
3. **Tap Share → Add to Home Screen**

Now you have one-tap access!

### Advanced Control

For start/stop/restart:
1. Install **Termius** app (free)
2. Add connection: `oracle@divinofax.local`
3. Run commands from SSH terminal

---

## 🎯 Dashboard Features

Once running, the dashboard shows:

| Feature | What It Shows |
|---------|---------------|
| 🟢 Status | Running/Stopped indicator |
| ▶️ Controls | Start/Stop/Restart buttons |
| 💾 Memory | RAM usage on Pi |
| 📁 Storage | Disk space on Pi |
| 📜 Fortunes | Last 5 cards generated |
| 🔄 Auto-Refresh | Updates every 5 seconds |

---

## 🔐 Auto-Start on Pi Reboot

**YES - The dashboard is configured to auto-start!**

When you reboot the Pi:
1. System boots
2. DivinoFax service auto-starts
3. Dashboard service auto-starts
4. Dashboard accessible at `http://divinofax.local:5000`

**Check auto-start status:**
```bash
ssh oracle@divinofax.local "sudo systemctl is-enabled divinofax-dashboard"
# Output: enabled
```

---

## 🔍 Troubleshooting

### Dashboard won't load
```bash
# Check status
./control_dashboard.sh status

# Restart it
./control_dashboard.sh restart

# View logs
./control_dashboard.sh logs
```

### Can't reach Pi
```bash
# Test connection
./control_dashboard.sh test

# Ping manually
ping divinofax.local
```

### iPhone can't find dashboard
- Make sure iPhone is on same WiFi
- Try IP address instead: `http://10.0.0.95:5000`
- Restart iPhone WiFi

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `DASHBOARD_SETUP.md` | Detailed setup instructions |
| `DASHBOARD_TOOLS.md` | This file - quick reference |
| `IOS_SHORTCUT_GUIDE.md` | iOS automation guide |

---

## 🚀 Quick Start Checklist

- [x] Dashboard installed on Pi
- [x] Dashboard auto-starts on reboot
- [x] Accessible at `http://divinofax.local:5000`
- [x] Mac control script ready
- [x] Status checker ready
- [x] iOS guide available

---

## 💡 Pro Tips

### Tip 1: Create an Alias
```bash
# Add to ~/.zshrc or ~/.bashrc
alias divinofax='./control_dashboard.sh'

# Then use:
divinofax status      # Instead of ./control_dashboard.sh status
divinofax restart     # Simpler!
```

### Tip 2: Automated Monitoring
```bash
# Run status check every 30 seconds
watch -n 30 ./dashboard_status.sh
```

### Tip 3: Quick Browser Access
```bash
# Open dashboard directly from Mac terminal
open http://divinofax.local:5000
```

### Tip 4: SSH Alias for Logs
Add to `~/.ssh/config`:
```
Host divinofax-logs
    HostName divinofax.local
    User oracle
    LocalCommand ssh %h "sudo journalctl -u divinofax-dashboard -f"
```

Then: `ssh divinofax-logs`

---

## 🎬 Typical Workflow

**Before an art event:**
```bash
# 1. Check everything is ready
./control_dashboard.sh status

# 2. Make sure service will restart if issues occur
ssh oracle@divinofax.local "sudo systemctl is-enabled divinofax-dashboard"

# 3. Monitor from any device during event
open http://divinofax.local:5000      # Mac browser
# or use iPhone/iPad
```

**During event:**
- Monitor dashboard from iPhone
- Quick start/restart if needed
- Check fortunes are being generated

**After event:**
```bash
# Save logs if needed
scp oracle@divinofax.local:/home/oracle/divinofax/divinofax.log ~/event_logs.txt
```

---

## 🆘 Need Help?

### Mac Script Issues
```bash
./control_dashboard.sh help    # View all commands
```

### Status Checker Issues
```bash
bash -x ./dashboard_status.sh  # Run with debug output
```

### Dashboard Configuration
```bash
# View service file
cat /etc/systemd/system/divinofax-dashboard.service

# View real-time logs
./control_dashboard.sh logs
```

---

## 📞 Quick Contact Info

- **Dashboard URL:** `http://divinofax.local:5000`
- **Pi IP:** `10.0.0.95`
- **SSH Access:** `ssh oracle@divinofax.local`
- **Dashboard Service:** `divinofax-dashboard` (systemd)

---

**You're all set!** 🎉 Your dashboard is running, will auto-start on reboot, and can be controlled from your Mac, iPhone, or any device on your network.
