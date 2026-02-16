#!/bin/bash
# Deploy DivinoFax to Raspberry Pi with password authentication

set -e

PI_HOST="${1:-divinofax.local}"
PI_USER="${2:-oracle}"
PI_PASSWORD="${3}"
PI_PATH="/home/${PI_USER}/divinofax"
LOCAL_REPO="/Users/kathrynbennett/divinofax"

if [ -z "$PI_PASSWORD" ]; then
    echo "❌ Password required!"
    echo "Usage: $0 [hostname] [username] [password]"
    echo "Example: $0 divinofax.local oracle Oracle123!"
    exit 1
fi

# Check sshpass is available
if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    brew install sshpass
fi

echo "🚀 DivinoFax Deployment Script"
echo "================================"
echo "Target: ${PI_USER}@${PI_HOST}"
echo "Remote Path: ${PI_PATH}"
echo ""

# Test connection
echo "📡 Testing connection..."
if ! sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "${PI_USER}@${PI_HOST}" "echo 'Connected'" > /dev/null 2>&1; then
    echo "❌ Cannot connect to ${PI_USER}@${PI_HOST}"
    exit 1
fi
echo "✅ Connection successful"
echo ""

# Update git locally
echo "📝 Updating local repository..."
cd "$LOCAL_REPO"
git pull origin main
echo "✅ Local repo updated"
echo ""

# Copy code to Pi using rsync with sshpass
echo "📤 Syncing code to Pi..."
export RSYNC_RSH="sshpass -p '$PI_PASSWORD' ssh -o StrictHostKeyChecking=no"
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.claude' --exclude='*.txt' --exclude='*.log' \
    "$LOCAL_REPO/" "${PI_USER}@${PI_HOST}:${PI_PATH}/"
echo "✅ Code synced"
echo ""

# Run verification
echo "🔍 Running verification on Pi..."
sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no "${PI_USER}@${PI_HOST}" << 'PICOMMAND'
cd /home/oracle/divinofax

echo "Checking Python version..."
python3 --version

echo ""
echo "Checking core modules..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from astrology import AstrologyCalculator
    from moon_phase import MoonPhaseCalculator
    from suit_context import SuitContext
    from thermal_printer import ThermalPrinter
    print('✅ All core modules importable')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo ""
echo "Checking data files..."
ls -la data/oracle_cards.json data/rfid_mappings.json data/suits.json 2>&1 | tail -3

echo ""
echo "Testing astrology module..."
python3 src/astrology.py 2>&1 | head -3

echo ""
echo "✅ Verification complete!"
PICOMMAND

echo ""
echo "================================"
echo "✨ Deployment successful!"
echo "================================"
echo ""
echo "Next: SSH into your Pi:"
echo "  sshpass -p '$PI_PASSWORD' ssh oracle@${PI_HOST}"
echo ""
echo "Then run the system:"
echo "  cd /home/oracle/divinofax"
echo "  python3 src/divinofax.py"
echo ""
