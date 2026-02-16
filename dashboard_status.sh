#!/bin/bash
# Quick dashboard status checker
# Run this anytime to see if your dashboard is up

REMOTE_HOST="oracle@divinofax.local"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔮 DivinoFax Dashboard Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check Pi connection
if ! ping -c 1 divinofax.local &>/dev/null; then
    echo -e "${RED}❌ Pi is not reachable${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pi is reachable${NC}"
echo ""

# Get service status
STATUS=$(ssh "$REMOTE_HOST" "sudo systemctl is-active divinofax-dashboard 2>/dev/null" || echo "error")

if [ "$STATUS" = "active" ]; then
    echo -e "${GREEN}🟢 Dashboard is RUNNING${NC}"
else
    echo -e "${RED}🔴 Dashboard is STOPPED${NC}"
fi

echo ""

# Get dashboard version
echo -e "${BLUE}Dashboard Info:${NC}"
ssh "$REMOTE_HOST" "sudo systemctl status divinofax-dashboard --no-pager | grep -E 'Active|Loaded' | sed 's/^/  /'"

echo ""

# Try to fetch dashboard status
echo -e "${BLUE}Attempting to fetch dashboard data...${NC}"
if RESPONSE=$(curl -s -m 3 http://divinofax.local:5000/api/status 2>/dev/null); then
    echo -e "${GREEN}✅ Dashboard is responsive${NC}"
    echo ""

    # Parse JSON response (using Python for better parsing)
    RUNNING=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('Running' if data.get('running') else 'Stopped')" 2>/dev/null || echo "Unknown")
    MEMORY=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('stats', {}).get('memory', {}).get('used', 'N/A'))" 2>/dev/null || echo "N/A")
    DISK=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('stats', {}).get('disk', {}).get('used', 'N/A'))" 2>/dev/null || echo "N/A")

    echo "💾 Memory Used: $MEMORY"
    echo "📁 Disk Used: $DISK"
    echo ""

    # Get recent fortunes
    FORTUNES=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); fortunes=data.get('recent_fortunes', []); print(len(fortunes))" 2>/dev/null || echo "?")
    echo "📜 Recent Fortunes: $FORTUNES cards in queue"
else
    echo -e "${YELLOW}⚠️  Cannot reach dashboard HTTP server${NC}"
fi

echo ""
echo -e "${BLUE}Access at:${NC}"
echo "  🌐 http://divinofax.local:5000"
echo "  🌐 http://10.0.0.95:5000"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
