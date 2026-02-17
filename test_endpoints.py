#!/usr/bin/env python3
"""Test script to verify Flask endpoints are registered."""
import sys
import os

print("=" * 60)
print("Flask Route Registration Test")
print("=" * 60)

try:
    # Add src to path
    sys.path.insert(0, os.path.dirname(__file__))

    # Import Flask app
    from web_dashboard import app

    # Get all routes
    all_routes = {str(rule): list(rule.methods - {'HEAD', 'OPTIONS'}) for rule in app.url_map.iter_rules()}

    # Filter for hotspot endpoints
    hotspot_routes = {k: v for k, v in all_routes.items() if 'hotspot' in k}
    print(f"\nHotspot routes found: {len(hotspot_routes)}")
    for route, methods in hotspot_routes.items():
        print(f"  {route} {methods}")

    # Check if hotspot endpoints exist
    if not hotspot_routes:
        print("\n❌ ERROR: No hotspot endpoints found!")
        print("\nAll /api routes:")
        for route, methods in all_routes.items():
            if '/api' in route:
                print(f"  {route} {methods}")
        sys.exit(1)
    else:
        print("\n✅ Hotspot endpoints are registered!")
        sys.exit(0)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(2)
