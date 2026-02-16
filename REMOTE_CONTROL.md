# 🎮 DivinoFax Remote Control & UI Options

## Current Status: Auto-Start Configured ✅

Your DivinoFax is now configured to:
- **Auto-start** when Pi boots up
- **Run as a service** (systemd)
- **Restart automatically** if it crashes
- **Available** at `divinofax.local`

You can now simply:
1. Power on your Pi (it auto-starts)
2. Place RFID cards on the reader
3. Fortunes print automatically!

---

## Option 1: Web Dashboard (Recommended for Art Projects)

### Quick Web UI with Python Flask

Create a simple web interface to monitor and control the system:

```bash
# On your Pi, install Flask
pip3 install flask

# Create a simple web dashboard
# This lets you:
# - See if system is running
# - Restart the system
# - View recent fortunes
# - Check system health
```

**Benefits:**
- ✅ Access from any device (phone, tablet, laptop)
- ✅ Works on local network (no internet needed)
- ✅ Simple on/off toggle
- ✅ Beautiful, art-friendly interface possible

**Files to create:**
- `web_dashboard.py` - Flask app
- `templates/index.html` - Simple UI
- `static/style.css` - Styling

---

## Option 2: Command-Line Control (Simple)

```bash
# Check if running
ssh divinofax "systemctl status divinofax"

# Stop the system
ssh divinofax "sudo systemctl stop divinofax"

# Start the system
ssh divinofax "sudo systemctl start divinofax"

# Restart
ssh divinofax "sudo systemctl restart divinofax"

# View logs in real-time
ssh divinofax "journalctl -u divinofax -f"
```

Create a simple shell script to make this easier:

```bash
#!/bin/bash
# control_divinofax.sh

case "$1" in
  start)
    ssh divinofax "sudo systemctl start divinofax"
    echo "✅ DivinoFax started"
    ;;
  stop)
    ssh divinofax "sudo systemctl stop divinofax"
    echo "🛑 DivinoFax stopped"
    ;;
  status)
    ssh divinofax "systemctl status divinofax"
    ;;
  logs)
    ssh divinofax "journalctl -u divinofax -f"
    ;;
  *)
    echo "Usage: $0 {start|stop|status|logs}"
    ;;
esac
```

---

## Option 3: GitHub Pages Dashboard (No Server Needed)

Host a static HTML/JavaScript dashboard on GitHub Pages:

```
divinofax-dashboard/
├── index.html
├── style.css
└── script.js
```

**Setup:**
1. Create GitHub repo called `divinofax-dashboard`
2. Add simple HTML UI with status indicators
3. Enable GitHub Pages
4. Add JavaScript to SSH into your Pi and get status
5. Access at: `https://yourusername.github.io/divinofax-dashboard`

**Limitations:**
- ⚠️ Requires SSH key authentication
- ⚠️ No real browser SSH support (need backend)
- Better as a "view-only" dashboard with GitHub API

---

## Option 4: Telegram Bot (Mobile Control)

Create a Telegram bot to control DivinoFax from your phone:

```bash
pip3 install python-telegram-bot
```

Commands:
- `/status` - Check if running
- `/start` - Start the system
- `/stop` - Stop the system
- `/logs` - View recent logs
- `/restart` - Restart the system

**Benefits for Art Projects:**
- ✅ Control from anywhere
- ✅ Get notified when fortunes are printed
- ✅ No UI knowledge needed

---

## Recommended Setup for Your Art Project

### Phase 1: Current Status ✅
- System auto-starts on Pi boot
- Just power on and it runs
- Place RFID cards to get fortunes

### Phase 2: Add Simple Web UI (Optional)
```bash
# Create a minimal Flask dashboard to:
# - Show "System Running" status
# - Display last 5 fortunes
# - One-click restart button
```

### Phase 3: Mobile Control (If Needed)
- Use Telegram bot or simple web interface
- Control from your phone at art events

---

## Simplest Mobile Solution: Just SSH

Your easiest mobile option is just SSH from your phone:

1. Install **Termius** or **SSH Files** app on your phone
2. Add connection:
   - Host: `divinofax.local`
   - User: `oracle`
   - Use SSH key (already set up)
3. Quick commands:
   ```
   systemctl status divinofax
   systemctl restart divinofax
   ```

---

## File: Simple Web Dashboard

Would you like me to create a Flask web dashboard for you? It would include:

✅ Status indicator (running/stopped)
✅ Start/Stop/Restart buttons
✅ Last 10 fortunes printed
✅ System resource usage
✅ Beautiful art-friendly design

---

## Current System Control

```bash
# View logs (what fortunes were printed)
ssh divinofax "tail -50 /home/oracle/divinofax/divinofax.log"

# Check if service is running
ssh divinofax "systemctl is-active divinofax"

# Restart if something goes wrong
ssh divinofax "sudo systemctl restart divinofax"

# Check system resources
ssh divinofax "free -h && df -h"
```

---

## Next Steps

1. **Now**: Your system auto-starts on Pi power-on ✅
2. **Later**: Add web dashboard if you want mobile UI
3. **Art Events**: Just power on Pi and place cards!

Everything is set up for portable deployment! 🎉

