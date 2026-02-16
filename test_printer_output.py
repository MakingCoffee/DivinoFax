#!/usr/bin/env python3
"""
Test script to verify thermal printer output formatting.
Simulates a complete fortune reading with all celestial context.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thermal_printer import ThermalPrinter, ThermalPrinterConfig
from moon_phase import MoonPhaseCalculator
from astrology import AstrologyCalculator
from suit_context import SuitContext


async def test_printer_output():
    """Test the complete printer output with card, celestial, and suit context."""

    # Configure printer for simulation
    config = ThermalPrinterConfig(
        simulation_mode=True,
        output_file="thermal_output_test.txt"
    )

    # Create printer
    printer = ThermalPrinter(config)
    await printer.initialize()

    # Get celestial context
    moon_calc = MoonPhaseCalculator()
    moon_context = moon_calc.get_current_phase()

    astro_calc = AstrologyCalculator()
    astro_context = astro_calc.get_current_zodiac() or {}

    # Get suit context for Card 1
    suit_loader = SuitContext("data/suits.json")
    suit_context = suit_loader.get_suit_by_card(1)

    # Create fortune data (simulating what would come from text_library)
    fortune_data = {
        'haiku': 'Signals pierce the dark\nLost voices find their echo\nYou are finally heard',
        'title': 'The Signal - Message',
        'description': 'The first pulse of your existence. A declaration that you are here, that you matter. Listen for the quiet ping of recognition in the dark.',
        'keywords': ['transmission', 'communication', 'visibility', 'identity', 'broadcast', 'recognition'],
        'theme': 'Transmission. Recognition. Identity in broadcast.',
        'suit': suit_context,
        'moon': moon_context,
        'zodiac': astro_context
    }

    # Test print
    print(f"\n🔮 Testing Thermal Printer Output 🔮")
    print(f"Current Moon Phase: {moon_context['name']}")
    print(f"Current Zodiac: {astro_context['name']}")
    print(f"Suit: {suit_context['name']}")
    print(f"\nPrinting to: {config.output_file}\n")

    # Print the fortune
    await printer.print_oracle_fortune(
        fortune_data,
        rfid_code="04:26:9F:5A:06:1F:91",
        moon_context=moon_context,
        astro_context=astro_context,
        suit_context=suit_context
    )

    await printer.shutdown()

    # Read and display the output
    output_path = Path(config.output_file)
    if output_path.exists():
        print(f"\n✅ Output file created: {output_path}")
        print(f"\n{'='*50}")
        print("PRINTER OUTPUT:")
        print(f"{'='*50}\n")

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)

        print(f"{'='*50}\n")

        # Check for required fields
        checks = [
            ("Card Title", "THE SIGNAL" in content),
            ("Card Description", "first pulse" in content or "existence" in content),
            ("Suit Name", "THE SIGNAL" in content),
            ("Suit Essence", "Every message is a mirror" in content),
            ("Moon Phase", moon_context['name'] in content),
            ("Zodiac Sign", astro_context['name'] in content),
            ("Poem", "Signals pierce" in content),
        ]

        print("📋 Content Validation:")
        for field, found in checks:
            status = "✅" if found else "❌"
            print(f"  {status} {field}: {'Present' if found else 'MISSING'}")

    else:
        print(f"❌ Output file not created: {output_path}")


if __name__ == "__main__":
    asyncio.run(test_printer_output())
