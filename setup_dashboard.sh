#!/bin/bash
# Quick setup script for DivinoFax web dashboard auto-start
# Run this on the Raspberry Pi to set everything up automatically

set -e

echo "🚀 Setting up DivinoFax Web Dashboard..."

# Check if running on Pi
if ! grep -q "arm" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  WARNING: This doesn't appear to be running on a Raspberry Pi"
    echo "   This script is designed to run on the Pi itself"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# Create systemd service file
echo "📝 Creating systemd service file..."
sudo tee /etc/systemd/system/divinofax-dashboard.service > /dev/null << 'EOF'
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
EOF

# Reload systemd
echo "⚙️  Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service
echo "✅ Enabling auto-start on boot..."
sudo systemctl enable divinofax-dashboard

# Start service
echo "🚀 Starting dashboard service..."
sudo systemctl start divinofax-dashboard

# Check status
echo ""
echo "📊 Dashboard Status:"
sudo systemctl status divinofax-dashboard --no-pager

echo ""
echo "✅ Setup complete!"
echo ""
echo "📱 Access your dashboard at:"
echo "   - http://divinofax.local:5000"
echo "   - http://10.0.0.95:5000"
echo ""
echo "🔍 View logs with:"
echo "   sudo journalctl -u divinofax-dashboard -f"
