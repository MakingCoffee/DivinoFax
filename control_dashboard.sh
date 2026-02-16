#!/bin/bash
# DivinoFax Dashboard Control Script
# Easily manage the dashboard from your Mac

set -e

REMOTE_HOST="oracle@divinofax.local"
DASHBOARD_URL="http://divinofax.local:5000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Show help
show_help() {
    cat << EOF
🔮 DivinoFax Dashboard Control

USAGE:
    ./control_dashboard.sh [COMMAND]

COMMANDS:
    status          - Check if dashboard is running
    start           - Start the dashboard service
    stop            - Stop the dashboard service
    restart         - Restart the dashboard service
    logs            - View live dashboard logs
    open            - Open dashboard in browser
    test            - Test connection to Pi
    help            - Show this help message

EXAMPLES:
    ./control_dashboard.sh status      # Check status
    ./control_dashboard.sh restart     # Restart service
    ./control_dashboard.sh open        # Open in browser

EOF
}

# Test connection
test_connection() {
    echo -e "${BLUE}🔍 Testing connection to Pi...${NC}"
    if ping -c 1 divinofax.local &> /dev/null; then
        echo -e "${GREEN}✅ Pi is reachable${NC}"
        echo "   IP: 10.0.0.95"
        echo "   Hostname: divinofax.local"
    else
        echo -e "${RED}❌ Cannot reach Pi${NC}"
        exit 1
    fi
}

# Check status
check_status() {
    echo -e "${BLUE}📊 Checking dashboard status...${NC}"

    STATUS=$(ssh "$REMOTE_HOST" "sudo systemctl is-active divinofax-dashboard" 2>/dev/null || echo "error")

    if [ "$STATUS" = "active" ]; then
        echo -e "${GREEN}✅ Dashboard is RUNNING${NC}"
        echo ""
        echo "Access at:"
        echo "  🌐 $DASHBOARD_URL"
        echo ""
        echo "Service details:"
        ssh "$REMOTE_HOST" "sudo systemctl status divinofax-dashboard --no-pager | tail -5"
    else
        echo -e "${RED}❌ Dashboard is STOPPED${NC}"
        echo ""
        echo "Start it with: ./control_dashboard.sh start"
    fi
}

# Start dashboard
start_dashboard() {
    echo -e "${BLUE}🚀 Starting dashboard...${NC}"
    ssh "$REMOTE_HOST" "sudo systemctl start divinofax-dashboard"
    sleep 1
    check_status
}

# Stop dashboard
stop_dashboard() {
    echo -e "${BLUE}🛑 Stopping dashboard...${NC}"
    ssh "$REMOTE_HOST" "sudo systemctl stop divinofax-dashboard"
    echo -e "${GREEN}✅ Dashboard stopped${NC}"
}

# Restart dashboard
restart_dashboard() {
    echo -e "${BLUE}🔄 Restarting dashboard...${NC}"
    ssh "$REMOTE_HOST" "sudo systemctl restart divinofax-dashboard"
    sleep 1
    check_status
}

# View logs
view_logs() {
    echo -e "${BLUE}📜 Dashboard logs (Ctrl+C to exit):${NC}"
    echo ""
    ssh "$REMOTE_HOST" "sudo journalctl -u divinofax-dashboard -f"
}

# Open in browser
open_browser() {
    echo -e "${BLUE}🌐 Opening dashboard in browser...${NC}"

    if check_status &>/dev/null; then
        open "$DASHBOARD_URL"
        echo -e "${GREEN}✅ Dashboard opened at $DASHBOARD_URL${NC}"
    else
        echo -e "${RED}❌ Dashboard is not running${NC}"
        read -p "Start it now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            start_dashboard
            sleep 2
            open "$DASHBOARD_URL"
        fi
    fi
}

# Main command handler
case "${1:-help}" in
    status)
        check_status
        ;;
    start)
        start_dashboard
        ;;
    stop)
        stop_dashboard
        ;;
    restart)
        restart_dashboard
        ;;
    logs)
        view_logs
        ;;
    open)
        open_browser
        ;;
    test)
        test_connection
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
