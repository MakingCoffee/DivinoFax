# 📊 Web Dashboard Auto-Start Setup

This guide shows how to set up the web dashboard to start automatically when your Raspberry Pi boots.

## What This Does

- **Auto-starts** the web dashboard when Pi powers on
- **Accessible** from any device on your network at `http://divinofax.local:5000`
- **Auto-restarts** if the dashboard crashes
- **Works from** laptops, phones, tablets, anywhere on your home network

## Setup Instructions (Run on Pi)

### Step 1: Create the systemd service file

SSH into your Pi:
```bash
ssh oracle@divinofax.local
```

Create the service file:
```bash
sudo nano /etc/systemd/system/divinofax-dashboard.service
```

Paste this content:
```ini
[Unit]
Description=DivinoFax Web Dashboard
After=network.target

[Service]
Type=simple
User=oracle
WorkingDirectory=/home/oracle/divinofax
ExecStart=/usr/bin/python3 web_dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save with: `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 2: Enable and start the service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable divinofax-dashboard

# Start the service now
sudo systemctl start divinofax-dashboard

# Verify it's running
sudo systemctl status divinofax-dashboard
```

### Step 3: Access the dashboard

From any device on your network:
- **Laptop**: `http://divinofax.local:5000`
- **Phone**: `http://divinofax.local:5000` (if mDNS works) or `http://10.0.0.95:5000`
- **iPad**: Same as above

## Troubleshooting

### Dashboard won't start
```bash
# Check logs
sudo journalctl -u divinofax-dashboard -n 50

# Check if Flask is installed
python3 -c "import flask; print(flask.__version__)"

# Install if missing
pip3 install flask
```

### Can't access from another device
```bash
# Check if dashboard is listening on port 5000
sudo netstat -tlnp | grep 5000

# Check firewall
sudo ufw allow 5000/tcp  # If using UFW

# Check Pi's IP address
hostname -I
```

### Port 5000 already in use
Edit `web_dashboard.py` and change:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
# to:
app.run(host='0.0.0.0', port=5001, debug=True)
```

Then update service file with same port.

## Common Commands

```bash
# View live logs
sudo journalctl -u divinofax-dashboard -f

# Stop dashboard
sudo systemctl stop divinofax-dashboard

# Restart dashboard
sudo systemctl restart divinofax-dashboard

# Check if it auto-starts on boot
sudo systemctl is-enabled divinofax-dashboard
# Should output: enabled
```

## Dashboard Features

Once running, you can:
- ✅ See if DivinoFax service is running (green/red status)
- ✅ View recent fortunes generated
- ✅ See system stats (memory, disk usage)
- ✅ Start/Stop/Restart the DivinoFax service
- ✅ View recent logs
- ✅ Access from any device on your network
- ✅ Auto-refresh every 5 seconds

## Testing Locally (on Pi)

If you want to test first before setting up auto-start:
```bash
cd /home/oracle/divinofax
python3 web_dashboard.py
```

Then visit `http://localhost:5000` on the Pi itself.
