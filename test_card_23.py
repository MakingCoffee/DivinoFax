#!/usr/bin/env python3
"""
Generate a sample thermal printer output for Card 23: Biotech Braid
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thermal_printer import ThermalPrinter, ThermalPrinterConfig
from moon_phase import MoonPhaseCalculator
from astrology import AstrologyCalculator
from suit_context import SuitContext


async def test_card_23():
    """Generate output for Card 23: Biotech Braid"""

    # Configure printer for simulation
    config = ThermalPrinterConfig(
        simulation_mode=True,
        output_file="card_23_output.txt"
    )

    # Create printer
    printer = ThermalPrinter(config)
    await printer.initialize()

    # Get celestial context
    moon_calc = MoonPhaseCalculator()
    moon_context = moon_calc.get_current_phase()

    astro_calc = AstrologyCalculator()
    astro_context = astro_calc.get_current_zodiac() or {}

    # Card 23 is in range 16-30, so it belongs to Suit 2: The Circuit
    suit_loader = SuitContext("data/suits.json")
    suit_context = suit_loader.get_suit_by_card(23)

    # Load Card 23 data from oracle_cards.json
    with open('data/oracle_cards.json', 'r') as f:
        all_cards = json.load(f)
        card_23_data = all_cards[22]  # Card 23 is index 22 (0-indexed)

    # Create fortune data with actual card information
    fortune_data = {
        'haiku': 'Strands weave together\nMany threads make one strong whole\nHarmony in all',
        'title': card_23_data['title'],
        'description': card_23_data['description'],
        'keywords': card_23_data['keywords'],
        'theme': 'Integration and collaboration',
        'suit': suit_context,
        'moon': moon_context,
        'zodiac': astro_context
    }

    # Test print
    print(f"\n🔮 Divinofax Thermal Printer Output - Card 23 🔮")
    print(f"Card: {card_23_data['title']}")
    print(f"Suit: {suit_context['name']} (Cards 16-30)")
    print(f"Current Moon Phase: {moon_context['name']}")
    print(f"Current Zodiac: {astro_context['name']}")
    print(f"\nGenerating thermal printer output to: {config.output_file}\n")

    # Print the fortune
    await printer.print_oracle_fortune(
        fortune_data,
        rfid_code="04:26:B5:5A:06:1F:91",  # Real RFID UID for Card 23
        moon_context=moon_context,
        astro_context=astro_context,
        suit_context=suit_context
    )

    await printer.shutdown()

    # Read and display the output
    output_path = Path(config.output_file)
    if output_path.exists():
        print(f"\n✅ Output file created: {output_path}")
        print(f"\n{'='*60}")
        print("THERMAL PRINTER OUTPUT FOR CARD 23:")
        print(f"{'='*60}\n")

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)

        print(f"{'='*60}\n")

        # Check for required fields
        checks = [
            ("Card Title", "BIOTECH BRAID" in content),
            ("Card Description", "Integration" in content or "collaborative" in content),
            ("Suit Name", "THE CIRCUIT" in content or "The Circuit" in content),
            ("Suit Essence", "Every ache is a message" in content),
            ("Moon Phase", moon_context['name'] in content),
            ("Zodiac Sign", astro_context['name'] in content),
            ("Poem", "Strands weave" in content or "threads make" in content),
            ("Keywords", "integration" in content or "synergy" in content),
        ]

        print("📋 Content Validation:")
        all_pass = True
        for field, found in checks:
            status = "✅" if found else "❌"
            print(f"  {status} {field}: {'Present' if found else 'MISSING'}")
            if not found:
                all_pass = False

        if all_pass:
            print("\n🎉 All elements present and correct!")
        else:
            print("\n⚠️ Some elements missing from output")

    else:
        print(f"❌ Output file not created: {output_path}")


if __name__ == "__main__":
    asyncio.run(test_card_23())
