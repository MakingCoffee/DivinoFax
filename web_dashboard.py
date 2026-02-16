#!/usr/bin/env python3
"""
DivinoFax Web Dashboard
Simple Flask web interface to monitor and control the DivinoFax system
"""

from flask import Flask, render_template, jsonify
from datetime import datetime
import subprocess
import os
import re
import logging

app = Flask(__name__)

# Configure logging for the dashboard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
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

if __name__ == '__main__':
    # Run on all interfaces on port 5000
    # This script is meant to run on the Raspberry Pi, not on macOS
    app.run(host='0.0.0.0', port=5000, debug=True)
