"""
RFID UID to Card Mapper for Divinofax
======================================

Maps RC522-read RFID UIDs to oracle card numbers (1-75).
Supports multiple UID formats for flexibility.

Author: Kathryn Bennett
"""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class RFIDCardMapper:
    """Maps RFID UIDs to oracle card numbers."""

    def __init__(self, mappings_file: str = "data/rfid_mappings.json"):
        """Initialize the mapper with RFID mappings file."""
        self.mappings_file = Path(mappings_file)
        self.uid_to_card = {}  # UID (hex string) -> card number
        self.is_loaded = False
        self.total_cards = 0

        self._load_mappings()

    def _load_mappings(self):
        """Load RFID mappings from JSON file."""
        try:
            if not self.mappings_file.exists():
                logger.warning(f"RFID mappings file not found: {self.mappings_file}")
                return

            with open(self.mappings_file, 'r') as f:
                data = json.load(f)

            # Extract mapping from the JSON
            if 'mapping' in data:
                self.uid_to_card = data['mapping']
                self.total_cards = data.get('total_cards', 0)
                self.is_loaded = True
                logger.info(f"Loaded {len(self.uid_to_card)} RFID mappings")
            else:
                logger.error("Invalid RFID mappings file format")

        except Exception as e:
            logger.error(f"Failed to load RFID mappings: {e}")

    def uid_hex_to_card(self, uid_hex: str) -> Optional[int]:
        """
        Convert UID hex string to card number.

        Args:
            uid_hex: UID as hex string (e.g., "04:26:9F:5A:06:1F:91")

        Returns:
            Card number (1-75) or None if not found
        """
        if not self.is_loaded:
            logger.warning("RFID mapper not loaded")
            return None

        # Try exact match first
        if uid_hex in self.uid_to_card:
            return self.uid_to_card[uid_hex]

        # Try without colons
        uid_no_colon = uid_hex.replace(':', '').replace(' ', '')
        uid_with_colon = ':'.join(uid_no_colon[i:i+2] for i in range(0, len(uid_no_colon), 2))

        if uid_with_colon in self.uid_to_card:
            return self.uid_to_card[uid_with_colon]

        # Try uppercase
        uid_upper = uid_hex.upper()
        if uid_upper in self.uid_to_card:
            return self.uid_to_card[uid_upper]

        logger.warning(f"UID not found in mappings: {uid_hex}")
        return None

    def uid_bytes_to_card(self, uid_bytes: list) -> Optional[int]:
        """
        Convert UID byte array to card number.

        Args:
            uid_bytes: UID as list of integers (e.g., [0x04, 0x26, 0x9F, 0x5A, 0x06, 0x1F, 0x91])

        Returns:
            Card number (1-75) or None if not found
        """
        # Convert bytes to hex string
        uid_hex = ':'.join(f"{b:02X}" for b in uid_bytes)
        return self.uid_hex_to_card(uid_hex)

    def card_to_uid_hex(self, card_number: int) -> Optional[str]:
        """
        Get UID hex string for a card number (reverse lookup).

        Args:
            card_number: Card number (1-75)

        Returns:
            UID hex string or None if not found
        """
        if not self.is_loaded:
            return None

        for uid_hex, card in self.uid_to_card.items():
            if card == card_number:
                return uid_hex

        logger.warning(f"Card number not found: {card_number}")
        return None

    def get_all_cards(self) -> dict:
        """Get all RFID mappings (UID -> card number)."""
        return self.uid_to_card.copy()

    def is_valid_card(self, card_number: int) -> bool:
        """Check if a card number is valid (1-75)."""
        return 1 <= card_number <= 75

    def is_valid_uid(self, uid_hex: str) -> bool:
        """Check if a UID is in the mappings."""
        return uid_hex in self.uid_to_card or uid_hex.upper() in self.uid_to_card


async def test_rfid_mapper():
    """Test the RFID mapper."""
    mapper = RFIDCardMapper("data/rfid_mappings.json")

    print("Testing RFID Card Mapper\n")
    print(f"Mapper loaded: {mapper.is_loaded}")
    print(f"Total cards: {mapper.total_cards}\n")

    # Test some lookups
    test_uids = [
        "04:26:9F:5A:06:1F:91",  # Card 1
        "04:26:A0:5A:06:1F:91",  # Card 2
        "04:26:65:5A:06:1F:91",  # Card 75
    ]

    print("UID → Card lookups:")
    for uid in test_uids:
        card = mapper.uid_hex_to_card(uid)
        print(f"  {uid} → Card {card}")

    # Test reverse lookup
    print("\nCard → UID reverse lookups:")
    for card in [1, 2, 75]:
        uid = mapper.card_to_uid_hex(card)
        print(f"  Card {card} → {uid}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_rfid_mapper())
