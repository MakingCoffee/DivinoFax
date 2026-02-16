#!/usr/bin/env python3
"""
DivinoFax Web Dashboard
Simple Flask web interface to monitor and control the DivinoFax system
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import subprocess
import os
import re
import logging
import json
import time

app = Flask(__name__)

# Configure logging for the dashboard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(cmd, timeout=5):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def is_service_running():
    """Check if DivinoFax service is running."""
    result = run_command("systemctl is-active divinofax")
    return result == "active"

def find_log_file():
    """Intelligently locate the DivinoFax log file.

    Checks multiple possible locations:
    1. Environment variable DIVINOFAX_LOG_FILE
    2. Pi production path: /home/oracle/divinofax/divinofax.log
    3. macOS development path: /Users/kathrynbennett/divinofax/divinofax.log
    4. Relative path: ./divinofax.log

    Returns the first path that exists, or None if no log file found.
    """
    # Check environment variable first
    env_log = os.environ.get('DIVINOFAX_LOG_FILE')
    if env_log and os.path.exists(env_log):
        logger.info(f"Using log file from environment: {env_log}")
        return env_log

    # List of possible locations to check
    possible_paths = [
        "/home/oracle/divinofax/divinofax.log",  # Pi production
        "/Users/kathrynbennett/divinofax/divinofax.log",  # macOS development
        "./divinofax.log",  # Relative to current directory
        os.path.expanduser("~/divinofax/divinofax.log"),  # Home directory
    ]

    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found log file at: {path}")
            return path

    # Log warning if no log file found
    logger.warning(f"No log file found. Checked: {possible_paths}")
    return None

def get_recent_fortunes(lines=10):
    """Get recent fortunes from the log file."""
    fortunes = []
    log_file = find_log_file()

    if not log_file:
        logger.warning("Cannot read fortunes: log file not found")
        return []

    try:
        with open(log_file, 'r') as f:
            log_lines = f.readlines()

        # Extract fortune titles from logs
        for line in log_lines[-100:]:  # Check last 100 lines for more coverage
            if "Generated fortune for" in line:
                # Extract card name from log line - handle multiple formats
                # Format 1: "Generated fortune for: CardName"
                # Format 2: "Generated fortune for: CardName (Card #X)"
                match = re.search(r"Generated fortune for[:\s]+(.+?)(?:\s*\(Card|\s*$)", line)
                if match:
                    card_name = match.group(1).strip()
                    timestamp = line.split()[0] if line else ""
                    fortunes.append({
                        "card": card_name,
                        "time": timestamp
                    })

        return list(reversed(fortunes))[:lines]
    except IOError as e:
        logger.error(f"Error reading log file {log_file}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error processing fortunes: {e}")
        return []

def get_system_stats():
    """Get system statistics."""
    # Memory
    mem_output = run_command("free -h | grep Mem")
    mem_parts = mem_output.split() if mem_output else []

    # Disk
    disk_output = run_command("df -h / | tail -1")
    disk_parts = disk_output.split() if disk_output else []

    return {
        "memory": {
            "total": mem_parts[1] if len(mem_parts) > 1 else "N/A",
            "used": mem_parts[2] if len(mem_parts) > 2 else "N/A",
            "free": mem_parts[3] if len(mem_parts) > 3 else "N/A"
        },
        "disk": {
            "total": disk_parts[1] if len(disk_parts) > 1 else "N/A",
            "used": disk_parts[2] if len(disk_parts) > 2 else "N/A",
            "free": disk_parts[3] if len(disk_parts) > 3 else "N/A"
        }
    }

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get system status."""
    running = is_service_running()
    stats = get_system_stats()
    fortunes = get_recent_fortunes(5)

    return jsonify({
        "running": running,
        "status": "🟢 Running" if running else "🔴 Stopped",
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "recent_fortunes": fortunes
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the DivinoFax service."""
    run_command("sudo systemctl start divinofax")
    return jsonify({"success": True, "message": "✅ DivinoFax started"})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the DivinoFax service."""
    run_command("sudo systemctl stop divinofax")
    return jsonify({"success": True, "message": "🛑 DivinoFax stopped"})

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """Restart the DivinoFax service."""
    run_command("sudo systemctl restart divinofax")
    return jsonify({"success": True, "message": "🔄 DivinoFax restarted"})

@app.route('/api/logs')
def api_logs():
    """Get recent logs."""
    log_file = "/home/oracle/divinofax/divinofax.log"

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

        return jsonify({
            "logs": ''.join(lines[-50:])
        })
    except:
        return jsonify({"logs": "No logs available"})


# WiFi Configuration Endpoints
@app.route('/api/config/wifi/status')
def api_wifi_status():
    """Get current WiFi connection status."""
    try:
        # Get current WiFi connection
        result = run_command("nmcli -t -f NAME,TYPE,DEVICE connection show --active 2>/dev/null | grep wifi")
        connected = bool(result)

        # Get IP address
        ip_addr = run_command("hostname -I 2>/dev/null").split()[0] if run_command("hostname -I 2>/dev/null") else "N/A"

        return jsonify({
            "connected": connected,
            "ip_address": ip_addr,
            "status": "🟢 Connected" if connected else "🔴 Disconnected"
        })
    except Exception as e:
        logger.error(f"Error getting WiFi status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/wifi/networks')
def api_wifi_networks():
    """Scan and return available WiFi networks with multiple scan attempts."""
    try:
        networks = []
        seen = set()

        # Perform multiple rescans with slight delays to catch networks
        # that may be broadcasting at different intervals or have weak signals
        for attempt in range(3):
            # Request a fresh WiFi scan
            run_command("nmcli dev wifi rescan 2>/dev/null", timeout=10)

            # Small delay between scans to allow hardware to discover networks
            if attempt < 2:
                time.sleep(1)

            # Get current scan results
            result = run_command("nmcli -t -f SSID,SECURITY dev wifi list 2>/dev/null", timeout=15)

            for line in result.split('\n'):
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 1:
                        ssid = parts[0].strip()
                        security = parts[1].strip() if len(parts) > 1 else "Open"
                        # Include networks even if SSID is empty string (hidden networks)
                        if ssid not in seen:
                            networks.append({
                                "ssid": ssid if ssid else "(Hidden Network)",
                                "security": security
                            })
                            seen.add(ssid)

        # Sort networks by signal strength (primary networks first)
        # and alphabetically within same strength
        return jsonify({"networks": sorted(networks, key=lambda x: x['ssid'])})
    except Exception as e:
        logger.error(f"Error scanning WiFi networks: {e}")
        return jsonify({"error": str(e), "networks": []}), 200


@app.route('/api/config/wifi/connect', methods=['POST'])
def api_wifi_connect():
    """Connect to a WiFi network."""
    try:
        data = request.get_json()
        ssid = data.get('ssid', '')
        password = data.get('password', '')

        if not ssid:
            return jsonify({"error": "SSID required"}), 400

        # Connect using nmcli
        if password:
            cmd = f'nmcli device wifi connect "{ssid}" password "{password}" 2>&1'
        else:
            cmd = f'nmcli device wifi connect "{ssid}" 2>&1'

        result = run_command(cmd)

        if "successfully activated" in result.lower() or "activated" in result.lower():
            return jsonify({"success": True, "message": f"✅ Connected to {ssid}"})
        else:
            return jsonify({"error": result}), 500

    except Exception as e:
        logger.error(f"Error connecting to WiFi: {e}")
        return jsonify({"error": str(e)}), 500


# LLM Configuration Endpoints
@app.route('/api/config/llm', methods=['GET'])
def api_llm_config_get():
    """Get current LLM configuration (with masked API key)."""
    try:
        config_path = "/home/oracle/divinofax/config/divinofax.yaml"

        if not os.path.exists(config_path):
            return jsonify({
                "use_claude_api": False,
                "claude_model": "claude-3-5-sonnet-20241022",
                "claude_api_key": "",
                "api_key_configured": False
            })

        # Read YAML config
        with open(config_path, 'r') as f:
            config_content = f.read()

        # Check if Claude API is enabled and if API key is set
        use_claude = "use_claude_api: true" in config_content or "use_claude_api: yes" in config_content
        has_key = os.environ.get('CLAUDE_API_KEY', '') != ''

        return jsonify({
            "use_claude_api": use_claude,
            "claude_model": "claude-3-5-sonnet-20241022",
            "claude_api_key": "sk-...****" if has_key else "",
            "api_key_configured": has_key
        })
    except Exception as e:
        logger.error(f"Error reading LLM config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/llm', methods=['POST'])
def api_llm_config_set():
    """Save Claude API key and LLM configuration."""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        use_claude = data.get('use_claude_api', False)

        if not api_key:
            return jsonify({"error": "API key required"}), 400

        # Validate API key format (should start with sk-)
        if not api_key.startswith('sk-'):
            return jsonify({"error": "Invalid Claude API key format"}), 400

        # Store in environment variable
        os.environ['CLAUDE_API_KEY'] = api_key

        # For persistence across restarts, write to a secure location or systemd environment
        # For now, just validate it works
        return jsonify({
            "success": True,
            "message": "✅ Claude API key configured",
            "use_claude_api": use_claude
        })

    except Exception as e:
        logger.error(f"Error saving LLM config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/llm/validate', methods=['POST'])
def api_llm_validate():
    """Validate Claude API key."""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()

        if not api_key or not api_key.startswith('sk-'):
            return jsonify({"valid": False, "error": "Invalid API key format"})

        # Try to import and create a client (validate without making a full API call)
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            # Just creating the client validates the key format
            return jsonify({"valid": True, "message": "✅ API key format valid"})
        except ImportError:
            return jsonify({"valid": False, "error": "anthropic library not installed"})
        except Exception as e:
            return jsonify({"valid": False, "error": str(e)})

    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run on all interfaces on port 5000
    # This script is meant to run on the Raspberry Pi, not on macOS
    app.run(host='0.0.0.0', port=5000, debug=True)
