#!/usr/bin/env python3
"""
Oracle Card Management System for Divinofax
===========================================

This script helps manage your oracle card collection:
1. Import card data (titles, descriptions)
2. Add/update RFID tag numbers
3. Deploy cards to Divinofax system
4. Backup and restore card data

Usage:
    python3 manage_oracle_cards.py import --csv cards.csv
    python3 manage_oracle_cards.py add-rfid --id 1 --rfid "123456789001" 
    python3 manage_oracle_cards.py deploy
    python3 manage_oracle_cards.py list

Author: Kathryn Bennett
"""

import json
import csv
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class OracleCardManager:
    """Manages oracle card data and deployment to Divinofax."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.cards_file = self.data_dir / "oracle_cards.json"
        self.texts_dir = self.data_dir / "texts"
        self.mappings_file = self.data_dir / "rfid_mappings.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.texts_dir.mkdir(exist_ok=True)
    
    def load_cards(self) -> List[Dict[str, Any]]:
        """Load oracle cards from JSON file."""
        if not self.cards_file.exists():
            logger.warning(f"No cards file found at {self.cards_file}")
            return []
        
        try:
            with open(self.cards_file, 'r', encoding='utf-8') as f:
                cards = json.load(f)
            logger.info(f"Loaded {len(cards)} cards from {self.cards_file}")
            return cards
        except Exception as e:
            logger.error(f"Failed to load cards: {e}")
            return []
    
    def save_cards(self, cards: List[Dict[str, Any]]):
        """Save oracle cards to JSON file."""
        try:
            # Create backup
            if self.cards_file.exists():
                backup_file = self.cards_file.with_suffix(f'.backup.{int(datetime.now().timestamp())}.json')
                self.cards_file.rename(backup_file)
                logger.info(f"Backup created: {backup_file}")
            
            with open(self.cards_file, 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(cards)} cards to {self.cards_file}")
        except Exception as e:
            logger.error(f"Failed to save cards: {e}")
    
    def import_from_csv(self, csv_file: str):
        """Import oracle cards from CSV file.
        
        CSV format: id,title,description,keywords
        """
        csv_path = Path(csv_file)
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_file}")
            return
        
        cards = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse keywords if provided
                    keywords = []
                    if row.get('keywords'):
                        keywords = [kw.strip() for kw in row['keywords'].split(',')]
                    
                    card = {
                        "id": int(row['id']),
                        "title": row['title'].strip(),
                        "description": row['description'].strip(),
                        "rfid_tag": None,
                        "keywords": keywords,
                        "active": True
                    }
                    cards.append(card)
            
            self.save_cards(cards)
            logger.info(f"Imported {len(cards)} cards from CSV")
            
        except Exception as e:
            logger.error(f"Failed to import CSV: {e}")
    
    def add_rfid_tag(self, card_id: int, rfid_tag: str):
        """Add or update RFID tag for a specific card."""
        cards = self.load_cards()
        
        # Find the card
        card_found = False
        for card in cards:
            if card['id'] == card_id:
                old_tag = card.get('rfid_tag')
                card['rfid_tag'] = rfid_tag
                card_found = True
                logger.info(f"Updated card {card_id} '{card['title']}': {old_tag} -> {rfid_tag}")
                break
        
        if not card_found:
            logger.error(f"Card with ID {card_id} not found")
            return
        
        self.save_cards(cards)
        logger.info("RFID tag updated successfully")
    
    def bulk_add_rfid(self, rfid_file: str):
        """Bulk add RFID tags from a file.
        
        File format: card_id,rfid_tag
        """
        rfid_path = Path(rfid_file)
        if not rfid_path.exists():
            logger.error(f"RFID file not found: {rfid_file}")
            return
        
        cards = self.load_cards()
        card_lookup = {card['id']: card for card in cards}
        
        updates = 0
        try:
            with open(rfid_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        card_id, rfid_tag = line.split(',')
                        card_id = int(card_id.strip())
                        rfid_tag = rfid_tag.strip()
                        
                        if card_id in card_lookup:
                            card_lookup[card_id]['rfid_tag'] = rfid_tag
                            updates += 1
                            logger.info(f"Line {line_num}: Updated card {card_id} -> {rfid_tag}")
                        else:
                            logger.warning(f"Line {line_num}: Card ID {card_id} not found")
                    
                    except ValueError:
                        logger.warning(f"Line {line_num}: Invalid format: {line}")
            
            self.save_cards(cards)
            logger.info(f"Bulk update complete: {updates} RFID tags added")
            
        except Exception as e:
            logger.error(f"Failed to bulk add RFID tags: {e}")
    
    def deploy_to_divinofax(self):
        """Deploy oracle cards to Divinofax system."""
        cards = self.load_cards()
        active_cards = [card for card in cards if card.get('active', True)]
        
        if not active_cards:
            logger.error("No active cards to deploy")
            return
        
        # Create individual text files for each card
        logger.info("Creating individual text files...")
        for card in active_cards:
            card_filename = f"oracle_{card['id']:03d}_{self._sanitize_filename(card['title'])}.txt"
            card_file = self.texts_dir / card_filename
            
            # Create the card content
            content = f"Title: {card['title']}\n\n{card['description']}"
            if card.get('keywords'):
                content += f"\n\nKeywords: {', '.join(card['keywords'])}"
            
            with open(card_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create RFID mappings for cards with RFID tags
        mappings = {}
        mapped_cards = 0
        
        for card in active_cards:
            if card.get('rfid_tag'):
                card_filename = f"oracle_{card['id']:03d}_{self._sanitize_filename(card['title'])}"
                mappings[card['rfid_tag']] = card_filename
                mapped_cards += 1
        
        # Save RFID mappings
        with open(self.mappings_file, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2)
        
        logger.info(f"Deployment complete!")
        logger.info(f"  - Created {len(active_cards)} text files")
        logger.info(f"  - Mapped {mapped_cards} RFID tags")
        logger.info(f"  - Unmapped cards: {len(active_cards) - mapped_cards}")
    
    def list_cards(self):
        """List all oracle cards with their status."""
        cards = self.load_cards()
        
        if not cards:
            logger.info("No cards loaded")
            return
        
        print(f"\n{'ID':<4} {'Title':<25} {'RFID Tag':<15} {'Status':<8}")
        print("-" * 60)
        
        for card in cards:
            rfid_status = card.get('rfid_tag') or 'None'
            status = "Active" if card.get('active', True) else "Inactive"
            title = card['title'][:24]  # Truncate long titles
            
            print(f"{card['id']:<4} {title:<25} {rfid_status:<15} {status:<8}")
        
        # Summary
        total = len(cards)
        active = len([c for c in cards if c.get('active', True)])
        with_rfid = len([c for c in cards if c.get('rfid_tag')])
        
        print(f"\nSummary: {total} total, {active} active, {with_rfid} with RFID tags")
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert title to safe filename."""
        # Replace spaces and special chars with underscores
        safe = "".join(c if c.isalnum() else "_" for c in name.lower())
        # Remove multiple underscores
        while "__" in safe:
            safe = safe.replace("__", "_")
        return safe.strip("_")

def main():
    parser = argparse.ArgumentParser(description="Oracle Card Management System")
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import cards from CSV')
    import_parser.add_argument('--csv', required=True, help='CSV file path')
    
    # Add RFID command
    rfid_parser = subparsers.add_parser('add-rfid', help='Add RFID tag to card')
    rfid_parser.add_argument('--id', type=int, required=True, help='Card ID')
    rfid_parser.add_argument('--rfid', required=True, help='RFID tag number')
    
    # Bulk RFID command
    bulk_parser = subparsers.add_parser('bulk-rfid', help='Bulk add RFID tags')
    bulk_parser.add_argument('--file', required=True, help='File with card_id,rfid_tag pairs')
    
    # Deploy command
    subparsers.add_parser('deploy', help='Deploy cards to Divinofax')
    
    # List command
    subparsers.add_parser('list', help='List all cards')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = OracleCardManager(args.data_dir)
    
    if args.command == 'import':
        manager.import_from_csv(args.csv)
    elif args.command == 'add-rfid':
        manager.add_rfid_tag(args.id, args.rfid)
    elif args.command == 'bulk-rfid':
        manager.bulk_add_rfid(args.file)
    elif args.command == 'deploy':
        manager.deploy_to_divinofax()
    elif args.command == 'list':
        manager.list_cards()

if __name__ == "__main__":
    main()
