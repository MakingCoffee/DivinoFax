#!/bin/bash
# Deploy DivinoFax to Raspberry Pi

set -e  # Exit on error

# Configuration
PI_HOST="${1:-pi@raspberrypi.local}"
PI_PATH="/home/pi/divinofax"
LOCAL_REPO="/Users/kathrynbennett/divinofax"

echo "🚀 DivinoFax Deployment Script"
echo "================================"
echo "Target: $PI_HOST"
echo "Remote Path: $PI_PATH"
echo ""

# Check if we can reach the Pi
echo "📡 Checking Pi connectivity..."
if ! ping -c 1 "$PI_HOST" > /dev/null 2>&1; then
    echo "❌ Cannot reach Pi at $PI_HOST"
    echo "Try: ssh $PI_HOST"
    exit 1
fi
echo "✅ Pi is reachable"
echo ""

# Ensure git is up to date locally
echo "📝 Updating local git repository..."
cd "$LOCAL_REPO"
git pull origin main
echo "✅ Local repo updated"
echo ""

# Copy code to Pi
echo "📤 Syncing code to Pi..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.claude' --exclude='*.txt' \
    "$LOCAL_REPO/" "$PI_HOST:$PI_PATH/"
echo "✅ Code synced"
echo ""

# Run verification on Pi
echo "🔍 Running verification on Pi..."
ssh "$PI_HOST" << 'PICOMMAND'
cd /home/pi/divinofax

echo ""
echo "Checking Python version..."
python3 --version

echo ""
echo "Checking required modules..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from astrology import AstrologyCalculator
    from moon_phase import MoonPhaseCalculator
    from suit_context import SuitContext
    from thermal_printer import ThermalPrinter
    print('✅ All core modules importable')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo ""
echo "Checking data files..."
ls -la data/oracle_cards.json data/rfid_mappings.json data/suits.json

echo ""
echo "Testing astrology module..."
python3 src/astrology.py 2>&1 | head -5

echo ""
echo "✅ Verification complete!"
PICOMMAND

echo ""
echo "================================"
echo "✨ Deployment successful!"
echo "================================"
echo ""
echo "Next steps on the Pi:"
echo "  1. ssh $PI_HOST"
echo "  2. cd /home/pi/divinofax"
echo "  3. python3 src/divinofax.py  # Start the system"
echo ""
echo "Or to test individual components:"
echo "  python3 src/astrology.py      # Test astrology"
echo "  python3 src/moon_phase.py     # Test moon phase"
echo "  python3 test_rfid_card.py     # Test with sample RFID"
echo ""
