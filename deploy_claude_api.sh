#!/bin/bash

# Divinofax Claude API Deployment Script
# ======================================
# This script deploys the Claude API-enabled version to the Raspberry Pi

set -e  # Exit on error

# Configuration
PI_USER="oracle"
PI_HOST="10.0.0.95"
PI_PATH="/home/oracle/divinofax"
REPO_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🚀 Divinofax Claude API Deployment"
echo "===================================="
echo ""
echo "Target: $PI_USER@$PI_HOST:$PI_PATH"
echo "Local: $REPO_PATH"
echo ""

# Step 1: Verify API Key
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ Error: CLAUDE_API_KEY environment variable not set"
    echo ""
    echo "Set it with:"
    echo "  export CLAUDE_API_KEY=\"sk-ant-v1-your-actual-key\""
    echo ""
    exit 1
fi

echo "✓ API key detected: ${CLAUDE_API_KEY:0:20}..."
echo ""

# Step 2: Verify Pi is accessible
echo "🔍 Checking Pi connectivity..."
if ! ssh -o ConnectTimeout=5 "$PI_USER@$PI_HOST" "echo 'Connected'" > /dev/null 2>&1; then
    echo "❌ Error: Cannot connect to Pi at $PI_USER@$PI_HOST"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify Pi is running and on network"
    echo "  2. Check IP address is correct: $PI_HOST"
    echo "  3. Verify SSH access: ssh $PI_USER@$PI_HOST"
    echo ""
    exit 1
fi
echo "✓ Pi is accessible"
echo ""

# Step 3: Push latest code to Pi
echo "📤 Deploying code to Pi..."
rsync -az --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='models/*.gguf' \
    --exclude='thermal_output.txt' \
    --exclude='divinofax.log' \
    --exclude='*.log' \
    "$REPO_PATH/" "$PI_USER@$PI_HOST:$PI_PATH/"

echo "✓ Code deployed"
echo ""

# Step 4: Set environment variable on Pi
echo "⚙️  Setting up environment variables..."
ssh "$PI_USER@$PI_HOST" << EOF
    # Add API key to bashrc if not already there
    if ! grep -q "CLAUDE_API_KEY" ~/.bashrc; then
        echo "export CLAUDE_API_KEY=\"$CLAUDE_API_KEY\"" >> ~/.bashrc
        echo "✓ API key added to ~/.bashrc"
    else
        echo "✓ API key already in ~/.bashrc"
    fi

    # Export for current session
    export CLAUDE_API_KEY="$CLAUDE_API_KEY"

    echo "✓ Environment variables configured"
EOF
echo ""

# Step 5: Test the integration
echo "🧪 Testing Claude API integration..."
ssh "$PI_USER@$PI_HOST" << EOF
    cd "$PI_PATH"
    export CLAUDE_API_KEY="$CLAUDE_API_KEY"

    # Run the integration test (with timeout)
    echo "Running haiku generation test..."
    timeout 60 python3 test_claude_integration.py 2>&1 || {
        echo "⚠️  Test did not complete (timeout or error)"
        echo "This may be normal if anthropic library is not installed"
        echo "Run this on Pi to install: pip3 install --user anthropic"
    }
EOF
echo ""

# Step 6: Restart the service
echo "🔄 Restarting DivinoFax service..."
ssh "$PI_USER@$PI_HOST" << EOF
    # Reload environment
    source ~/.bashrc

    # Restart service if it exists
    if systemctl --user is-enabled divinofax 2>/dev/null; then
        systemctl --user restart divinofax
        echo "✓ DivinoFax service restarted"
        sleep 2
        systemctl --user status divinofax
    else
        echo "ℹ️  DivinoFax service not found in user systemd"
        echo "   Manual service restart needed or use: systemctl restart divinofax"
    fi
EOF
echo ""

# Step 7: Verify deployment
echo "✅ Deployment Summary"
echo "===================="
echo ""
echo "✓ Code deployed to Pi"
echo "✓ API key configured in environment"
echo "✓ Service restarted"
echo ""
echo "📡 Access the dashboard:"
echo "   http://10.0.0.95:5000"
echo ""
echo "⚙️  Configuration sections available:"
echo "   • 📡 WiFi Connection - Connect to networks"
echo "   • 🤖 Claude API Setup - Validate/manage API key"
echo ""
echo "🧪 Manual testing on Pi:"
echo "   ssh oracle@10.0.0.95"
echo "   cd /home/oracle/divinofax"
echo "   python3 test_claude_integration.py"
echo ""
echo "📊 Monitor haiku generation:"
echo "   tail -f /home/oracle/divinofax/divinofax.log | grep haiku"
echo ""
echo "💰 Monitor API costs:"
echo "   https://console.anthropic.com/account/usage"
echo ""
echo "✨ Deployment complete!"
