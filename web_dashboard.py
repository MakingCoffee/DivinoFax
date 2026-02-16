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

app = Flask(__name__)

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

def get_recent_fortunes(lines=10):
    """Get recent fortunes from the log file."""
    log_file = "/home/oracle/divinofax/divinofax.log"
    fortunes = []

    try:
        with open(log_file, 'r') as f:
            log_lines = f.readlines()

        # Extract fortune titles from logs
        for line in log_lines[-50:]:  # Check last 50 lines
            if "Generated fortune for" in line:
                # Extract card name from log line
                match = re.search(r"Generated fortune for.*: (.*?)$", line)
                if match:
                    card_name = match.group(1)
                    timestamp = line.split()[0] if line else ""
                    fortunes.append({
                        "card": card_name,
                        "time": timestamp
                    })

        return list(reversed(fortunes))[:lines]
    except:
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
    app.run(host='0.0.0.0', port=5000, debug=True)
