"""
Suit Context Module for Divinofax
==================================

Loads and provides rich suit information including essence, description, and guidance.
Maps card numbers to suits and provides all contextual information.

Author: Kathryn Bennett
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SuitContext:
    """Manage suit information and provide contextual guidance."""

    def __init__(self, suits_file: str = "data/suits.json"):
        """Initialize suit context loader."""
        self.suits_file = Path(suits_file)
        self.suits = {}
        self.is_loaded = False
        self._load_suits()

    def _load_suits(self):
        """Load suit definitions from JSON file."""
        try:
            if not self.suits_file.exists():
                logger.warning(f"Suits file not found: {self.suits_file}")
                return

            with open(self.suits_file, 'r') as f:
                data = json.load(f)

            self.suits = data.get('suits', {})
            self.is_loaded = True
            logger.info(f"Loaded {len(self.suits)} suits")

        except Exception as e:
            logger.error(f"Failed to load suits: {e}")

    def get_suit_by_card(self, card_number: int) -> Optional[Dict[str, Any]]:
        """
        Get suit information for a given card number (1-75).

        Args:
            card_number: Card number (1-75)

        Returns:
            Dictionary with suit information or None if not found
        """
        if not self.is_loaded:
            return None

        if not (1 <= card_number <= 75):
            logger.warning(f"Invalid card number: {card_number}")
            return None

        # Determine suit (1-15 → Suit 1, 16-30 → Suit 2, etc.)
        suit_num = (card_number - 1) // 15 + 1

        suit_key = str(suit_num)
        if suit_key in self.suits:
            return self.suits[suit_key].copy()

        logger.warning(f"Suit not found for card {card_number}")
        return None

    def get_suit_essence(self, card_number: int) -> str:
        """Get the essence quote for a card's suit."""
        suit = self.get_suit_by_card(card_number)
        return suit.get('essence', '') if suit else ''

    def get_suit_name(self, card_number: int) -> str:
        """Get the suit name for a card."""
        suit = self.get_suit_by_card(card_number)
        return suit.get('name', '') if suit else ''

    def get_all_suits(self) -> Dict[str, Dict[str, Any]]:
        """Get all suit information."""
        return self.suits.copy()


async def test_suit_context():
    """Test the suit context loader."""
    context = SuitContext("data/suits.json")

    print("Testing Suit Context\n")
    print(f"Loader initialized: {context.is_loaded}")
    print(f"Total suits: {len(context.suits)}\n")

    # Test for cards from each suit
    for card_num in [1, 16, 31, 46, 61]:
        suit = context.get_suit_by_card(card_num)
        if suit:
            print(f"Card {card_num}:")
            print(f"  Suit: {suit['name']}")
            print(f"  Essence: {suit['essence']}")
            print(f"  Theme: {suit['theme']}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_suit_context())
