# 🎨 DivinoFax Art Project Deployment Guide

## 🎉 Complete Setup Status

✅ **System Running**: DivinoFax is live on your Pi
✅ **Auto-Start Configured**: System starts automatically on Pi power-on
✅ **Web Dashboard Ready**: Beautiful UI to monitor and control the system
✅ **SSH Access Configured**: Key-based authentication (no passwords!)
✅ **All 75 Cards Loaded**: Oracle deck ready to dispense fortunes
✅ **Celestial Context**: Moon phases and zodiac signs influencing fortunes

---

## 🚀 How to Use for Your Art Project

### Phase 1: Simple Operation (Power On & Forget)

```bash
# All you need to do:
1. Power on the Raspberry Pi
2. System auto-starts automatically
3. Place RFID cards on the reader
4. Watch fortunes print!
```

**That's it!** No commands needed. Just power and play.

---

### Phase 2: Monitor with Web Dashboard (Optional)

When you want to check status or control from a device:

**Start the web dashboard:**
```bash
ssh divinofax "cd /home/oracle/divinofax && python3 web_dashboard.py"
```

**Access the dashboard:**
- From laptop: `http://divinofax.local:5000`
- From phone: `http://10.0.0.95:5000`

**Dashboard features:**
- 🟢 Green/Red status indicator
- ▶️ Start/Stop/Restart buttons
- 📊 Memory and disk usage
- 📜 Last 5 fortunes printed
- 🔄 Auto-updates every 5 seconds

---

### Phase 3: Remote Control (If Needed)

From anywhere with internet access:

**Phone option 1 - SSH Terminal:**
- Install **Termius** app on your phone
- Add connection to `divinofax.local` (oracle user)
- Use SSH key already configured
- Run: `systemctl restart divinofax`

**Phone option 2 - Simple shell script:**
```bash
# Create control_divinofax.sh on your Mac
#!/bin/bash
case "$1" in
  start) ssh divinofax "sudo systemctl start divinofax" ;;
  stop)  ssh divinofax "sudo systemctl stop divinofax" ;;
  status) ssh divinofax "systemctl status divinofax" ;;
  logs)  ssh divinofax "journalctl -u divinofax -f" ;;
esac

# Then just run:
./control_divinofax.sh start
./control_divinofax.sh status
```

---

## 📋 Deployment Checklist for Art Events

### Before the Event

- [ ] Test RFID reader with sample cards
- [ ] Test thermal printer with paper
- [ ] Verify printer is properly connected
- [ ] Check paper roll is installed
- [ ] Confirm Pi has power adapter
- [ ] Create system backup (optional): `ssh divinofax "cd /home/oracle && tar -czf divinofax_backup.tar.gz divinofax/"`

### Day of Event

- [ ] Power on Raspberry Pi
- [ ] Wait 30 seconds for system to start
- [ ] Verify printer is powered
- [ ] Test with first RFID card
- [ ] Monitor: `ssh divinofax "tail -f /home/oracle/divinofax/divinofax.log"`
- [ ] Access dashboard if needed: `http://divinofax.local:5000`

### During Event

- [ ] Place RFID cards on reader
- [ ] Fortunes print automatically
- [ ] Monitor system if web dashboard is running
- [ ] Keep spare thermal paper nearby

### After Event

- [ ] Power off Raspberry Pi (or leave running)
- [ ] Save any logs: `scp oracle@divinofax.local:/home/oracle/divinofax/divinofax.log ./event_log.txt`
- [ ] Retrieve printed fortunes (if using for installation)

---

## 🎮 Quick Command Reference

### Monitor System
```bash
# View real-time logs
ssh divinofax "tail -f /home/oracle/divinofax/divinofax.log"

# Check service status
ssh divinofax "systemctl status divinofax"

# Check system health
ssh divinofax "free -h && df -h"
```

### Control System
```bash
# Stop the system
ssh divinofax "sudo systemctl stop divinofax"

# Start the system
ssh divinofax "sudo systemctl start divinofax"

# Restart if something goes wrong
ssh divinofax "sudo systemctl restart divinofax"
```

### Access Web Dashboard
```bash
# Start dashboard (runs on port 5000)
ssh divinofax "cd /home/oracle/divinofax && python3 web_dashboard.py"

# Then visit:
# http://divinofax.local:5000
# or http://10.0.0.95:5000
```

---

## 🔧 Troubleshooting

### System not responding
```bash
# Check if it's running
ssh divinofax "systemctl is-active divinofax"

# Restart it
ssh divinofax "sudo systemctl restart divinofax"

# Check logs for errors
ssh divinofax "journalctl -u divinofax -n 50"
```

### RFID cards not reading
- Check RC522 reader is powered and connected
- Verify SPI is enabled: `ssh divinofax "sudo raspi-config"`
- Test RFID reader: `ssh divinofax "python3 -c 'from src.rfid_reader import RFIDReader; print(\"OK\")' "`

### Printer not printing
- Check thermal printer has power (5-9V)
- Verify paper is loaded
- Check UART is enabled: `ssh divinofax "sudo raspi-config"`
- Test printer: `ssh divinofax "python3 src/thermal_printer.py"`

### Can't SSH to Pi
```bash
# Check if Pi is on network
ping divinofax.local

# Manual SSH with IP
ssh oracle@10.0.0.95

# Check SSH config
cat ~/.ssh/config | grep -A 5 "Host divinofax"
```

---

## 📊 System Architecture for Art Project

```
┌─────────────────────────────────────┐
│   Your Art Installation             │
│                                     │
│  Raspberry Pi 4 (running 24/7)     │
│  ├─ RFID Reader (RC522)             │
│  ├─ Thermal Printer (9600 baud)     │
│  ├─ DivinoFax System (auto-start)   │
│  └─ Optional Web Dashboard          │
│                                     │
└──────────────────────────────────────┤
         │
         │ USB/Serial
         │
    Laptop/Phone (optional)
         │
    Web Dashboard
    (monitor & control)
```

---

## 🎯 Art Installation Ideas

### Setup 1: Unattended Kiosk
- Power on Pi once, let it run all day
- Visitors place RFID cards on reader
- Fortunes print automatically
- No interaction needed from you

### Setup 2: Interactive Station
- Start web dashboard on your laptop
- Monitor fortunes in real-time
- Control from laptop if needed
- Display on screen: "Place card here"

### Setup 3: Data Collection
- Log all printed fortunes
- Export data at end of event: `scp oracle@divinofax.local:/home/oracle/divinofax/divinofax.log ./event_fortunes.txt`
- Analyze or display collected data

### Setup 4: Multi-Device
- Run dashboard on iPad or tablet
- Visitors see themselves on the screen
- Create immersive art experience

---

## 🔐 Security Notes

Your system is configured with:
- ✅ SSH key-based authentication (no passwords in commands)
- ✅ Local network only (no internet exposure)
- ✅ Automatic service restart on failure
- ✅ No sensitive data in logs

---

## 📱 Quickest Mobile Control Method

**iPhone/Android via SSH:**
1. Install "Termius" app (free)
2. Add connection:
   - Host: `divinofax.local` (or `10.0.0.95`)
   - User: `oracle`
   - Use SSH key (already set up)
3. Quick commands:
   - `systemctl status divinofax` (check status)
   - `systemctl restart divinofax` (restart)

---

## 🚀 What Happens When You Power On

1. **0-5 seconds**: Pi boots up
2. **5-10 seconds**: Linux loads
3. **10-15 seconds**: DivinoFax service auto-starts
4. **15+ seconds**: System ready for RFID cards
5. **Card placed**: Fortune generated and printed within 6-8 seconds

**Total startup time: ~15-20 seconds**

---

## 📚 Additional Documentation

- **QUICKSTART.md** - Fast getting-started guide
- **DEPLOYMENT_GUIDE.md** - Detailed hardware setup
- **REMOTE_CONTROL.md** - Control options
- **README.md** - Complete system documentation
- **INTEGRATION_FLOW.md** - Technical architecture

---

## 🎉 You're Ready!

Your DivinoFax is fully deployed and ready for art projects. Just:

1. Power on the Pi
2. Plug in the RFID reader and thermal printer
3. Load the paper
4. Let fortunes flow!

**No technical knowledge needed for basic operation.**

---

🔮 **May your fortunes be favorable and your art installation memorable!** 🔮
