#!/usr/bin/env python3
"""
RFID Tag Discovery Tool for Divinofax
=====================================

This script helps you discover and map RFID tag numbers to your oracle cards.

Usage:
    python3 discover_rfid_tags.py

Author: Kathryn Bennett
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

# Add src to path
import sys
sys.path.append('src')

from rfid_reader import RFIDReader, RFIDConfig
from pico_controller import PicoController, PicoConfig

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class RFIDDiscovery:
    """Tool to discover RFID tag numbers for oracle cards."""
    
    def __init__(self):
        self.discovered_tags = {}
        self.discovery_log = []
        self.output_file = Path("discovered_rfid_tags.json")
        self.mapping_file = Path("rfid_tag_mapping.txt")
        
    async def start_discovery(self):
        """Start the RFID discovery process."""
        print("🔮 RFID Tag Discovery Tool")
        print("=" * 50)
        print("This tool will help you map your physical oracle cards to RFID numbers.")
        print()
        print("Instructions:")
        print("1. Place each oracle card on the RFID reader")
        print("2. When prompted, enter the card ID and name")
        print("3. Press Ctrl+C when done")
        print()
        
        # Initialize RFID reader
        rfid_config = RFIDConfig()
        rfid_config.simulation_mode = False  # Use real hardware
        
        try:
            rfid_reader = RFIDReader(rfid_config)
            await rfid_reader.initialize()
            
            print("✅ RFID reader initialized. Place cards on reader now...")
            print()
            
            card_count = 0
            while True:
                try:
                    # Read RFID
                    rfid_code = await rfid_reader.read_next()
                    
                    if rfid_code and rfid_code not in self.discovered_tags:
                        card_count += 1
                        print(f"📱 NEW RFID DETECTED: {rfid_code}")
                        
                        # Get user input for card details
                        card_id = input("Enter oracle card ID (1-75): ").strip()
                        card_name = input("Enter oracle card name: ").strip()
                        
                        if card_id and card_name:
                            self.discovered_tags[rfid_code] = {
                                "card_id": int(card_id),
                                "card_name": card_name,
                                "discovered_at": datetime.now().isoformat(),
                                "discovery_order": card_count
                            }
                            
                            print(f"✅ Mapped RFID {rfid_code} → Card #{card_id}: {card_name}")
                            print(f"📊 Total cards mapped: {len(self.discovered_tags)}")
                            print("-" * 50)
                            
                            # Save after each discovery
                            self.save_progress()
                    
                    elif rfid_code:
                        # Already discovered
                        existing = self.discovered_tags[rfid_code]
                        print(f"🔄 Known card: {existing['card_name']} (ID: {existing['card_id']})")
                    
                    await asyncio.sleep(0.5)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Discovery stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error during discovery: {e}")
                    await asyncio.sleep(1)
            
            await rfid_reader.shutdown()
            
        except Exception as e:
            logger.error(f"Failed to initialize RFID reader: {e}")
            print("❌ Could not start RFID reader. Make sure hardware is connected.")
            return
        
        self.generate_final_output()
    
    def save_progress(self):
        """Save current progress."""
        try:
            # Save JSON format
            with open(self.output_file, 'w') as f:
                json.dump(self.discovered_tags, f, indent=2)
            
            # Save mapping format for bulk import
            with open(self.mapping_file, 'w') as f:
                f.write("# RFID Tag Mapping File\n")
                f.write("# Format: card_id,rfid_tag\n")
                f.write("# Use with: python3 manage_oracle_cards.py bulk-rfid --file rfid_tag_mapping.txt\n\n")
                
                for rfid, data in sorted(self.discovered_tags.items(), key=lambda x: x[1]['card_id']):
                    f.write(f"{data['card_id']},{rfid}\n")
            
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def generate_final_output(self):
        """Generate final summary and import instructions."""
        print(f"\n🎉 RFID Discovery Complete!")
        print(f"📊 Total cards mapped: {len(self.discovered_tags)}")
        print(f"💾 Data saved to: {self.output_file}")
        print(f"📝 Mapping file: {self.mapping_file}")
        print()
        
        if self.discovered_tags:
            print("📋 Summary:")
            for rfid, data in sorted(self.discovered_tags.items(), key=lambda x: x[1]['card_id']):
                print(f"  Card #{data['card_id']:2d}: {data['card_name']:<25} → {rfid}")
            
            print(f"\n🚀 Next Steps:")
            print(f"1. Import your complete oracle card CSV first:")
            print(f"   python3 manage_oracle_cards.py import --csv your_cards.csv")
            print()
            print(f"2. Bulk add all RFID mappings:")
            print(f"   python3 manage_oracle_cards.py bulk-rfid --file {self.mapping_file}")
            print()
            print(f"3. Deploy to Divinofax:")
            print(f"   python3 manage_oracle_cards.py deploy")

async def main():
    """Main entry point."""
    discovery = RFIDDiscovery()
    await discovery.start_discovery()

if __name__ == "__main__":
    print("🔮 Starting RFID Discovery Tool...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 RFID discovery tool stopped.")
    except Exception as e:
        logger.error(f"Discovery tool error: {e}")
