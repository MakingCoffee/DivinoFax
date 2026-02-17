#!/bin/bash
# Hotspot Auto-Connect Script
# Runs on boot to connect to saved hotspot before starting the main DivinoFax service
# This allows the dashboard to be accessible via hotspot if no local WiFi is available

HOTSPOT_CONFIG="/home/oracle/divinofax/config/hotspot.json"
LOG_FILE="/var/log/divinofax_hotspot.log"

{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Hotspot auto-connect service started"

    # Check if hotspot config exists
    if [ ! -f "$HOTSPOT_CONFIG" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - No hotspot configuration found. Skipping auto-connect."
        exit 0
    fi

    # Extract SSID and password from JSON
    SSID=$(grep -o '"ssid":"[^"]*' "$HOTSPOT_CONFIG" | cut -d'"' -f4)
    PASSWORD=$(grep -o '"password":"[^"]*' "$HOTSPOT_CONFIG" | cut -d'"' -f4)

    if [ -z "$SSID" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Invalid hotspot configuration (missing SSID)"
        exit 1
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') - Attempting to connect to hotspot: $SSID"

    # Wait for WiFi hardware to be ready (Pi needs a moment after boot)
    sleep 3

    # Check if already connected to a network
    CURRENT_CONNECTION=$(nmcli -t -f TYPE connection show --active 2>/dev/null | grep -i wifi)
    if [ -n "$CURRENT_CONNECTION" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Already connected to a WiFi network. Skipping hotspot auto-connect."
        exit 0
    fi

    # Connect to hotspot with timeout
    if [ -n "$PASSWORD" ]; then
        timeout 30 sudo nmcli device wifi connect "$SSID" password "$PASSWORD" >> "$LOG_FILE" 2>&1
    else
        timeout 30 sudo nmcli device wifi connect "$SSID" >> "$LOG_FILE" 2>&1
    fi

    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Successfully connected to hotspot: $SSID"
    elif [ $RESULT -eq 124 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Hotspot connection timed out"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to connect to hotspot (error code: $RESULT)"
    fi

} >> "$LOG_FILE" 2>&1
