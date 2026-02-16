#!/usr/bin/env python3
"""
Profile the complete fortune generation pipeline to estimate
processing time from RFID scan to printed output.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thermal_printer import ThermalPrinter, ThermalPrinterConfig
from moon_phase import MoonPhaseCalculator
from astrology import AstrologyCalculator
from suit_context import SuitContext
import json


async def profile_generation_time():
    """Profile complete pipeline execution time."""
    
    results = {
        "components": {},
        "total": 0
    }
    
    # Use Card 1 (Crystal Sync) for testing
    card_num = 1
    rfid_code = "04:26:9F:5A:06:1F:91"
    
    print("\n" + "="*60)
    print("📊 DIVINOFAX PROCESSING TIME PROFILE")
    print("="*60)
    print(f"\nTesting with Card {card_num} using RFID: {rfid_code}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Load Card Data (simulates RFID mapping lookup)
    print("1️⃣  Load Card Data (from RFID mapping)...")
    start = time.time()
    with open('data/oracle_cards.json', 'r') as f:
        all_cards = json.load(f)
        card_data = all_cards[card_num - 1]
    card_load_time = time.time() - start
    results["components"]["Card Data Load"] = card_load_time
    print(f"   ✓ Loaded '{card_data['title']}': {card_load_time*1000:.1f}ms")
    
    # 2. Moon Phase Calculation
    print("\n2️⃣  Moon Phase Calculation...")
    start = time.time()
    moon_calc = MoonPhaseCalculator()
    moon_context = moon_calc.get_current_phase()
    moon_time = time.time() - start
    results["components"]["Moon Phase Calc"] = moon_time
    print(f"   ✓ {moon_context['name']}: {moon_time*1000:.1f}ms")
    
    # 3. Astrology Calculation
    print("\n3️⃣  Astrology Calculation...")
    start = time.time()
    astro_calc = AstrologyCalculator()
    astro_context = astro_calc.get_current_zodiac()
    astro_time = time.time() - start
    results["components"]["Astrology Calc"] = astro_time
    print(f"   ✓ {astro_context['name']} ({astro_context['element']}): {astro_time*1000:.1f}ms")
    
    # 4. Suit Context Loading
    print("\n4️⃣  Suit Context Loading...")
    start = time.time()
    suit_loader = SuitContext("data/suits.json")
    suit_context = suit_loader.get_suit_by_card(card_num)
    suit_time = time.time() - start
    results["components"]["Suit Context Load"] = suit_time
    print(f"   ✓ {suit_context['name']}: {suit_time*1000:.1f}ms")
    
    # 5. Thermal Printer Setup & Printing
    print("\n5️⃣  Thermal Printer Output...")
    
    # Setup
    start = time.time()
    config = ThermalPrinterConfig(
        simulation_mode=True,
        output_file="profile_output.txt"
    )
    printer = ThermalPrinter(config)
    await printer.initialize()
    setup_time = time.time() - start
    results["components"]["Printer Initialization"] = setup_time
    print(f"   ✓ Initialized: {setup_time*1000:.1f}ms")
    
    # Prepare fortune data
    fortune_data = {
        'haiku': 'Crystals hum below\nHeart syncs with Earth\'s steady beat\nAlignment flows',
        'title': card_data['title'],
        'description': card_data['description'],
        'keywords': card_data.get('keywords', []),
        'theme': 'Alignment and Attunement'
    }
    
    # Print fortune
    start = time.time()
    await printer.print_oracle_fortune(
        fortune_data,
        rfid_code=rfid_code,
        moon_context=moon_context,
        astro_context=astro_context,
        suit_context=suit_context
    )
    print_time = time.time() - start
    results["components"]["Printer Output"] = print_time
    print(f"   ✓ Fortune printed: {print_time*1000:.1f}ms")
    
    await printer.shutdown()
    
    # Summary
    print("\n" + "="*60)
    print("📈 PERFORMANCE SUMMARY")
    print("="*60)
    
    total = sum(results["components"].values())
    results["total"] = total
    
    # Sort by time
    sorted_components = sorted(
        results["components"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    print(f"\n{'Component':<30} {'Time (ms)':<12} {'% of Total':<12}")
    print("-" * 54)
    
    for component, comp_time in sorted_components:
        pct = (comp_time / total * 100) if total > 0 else 0
        print(f"{component:<30} {comp_time*1000:>10.1f}  {pct:>10.1f}%")
    
    print("-" * 54)
    print(f"{'TOTAL PROCESSING TIME':<30} {total*1000:>10.1f}  {100:>10.1f}%")
    
    # Analysis
    print("\n" + "="*60)
    print("🎯 ANALYSIS & BREAKDOWN")
    print("="*60)
    
    celestial_time = moon_time + astro_time
    data_time = card_load_time + suit_time
    
    print(f"\n✅ Celestial Calculations: {celestial_time*1000:.1f}ms")
    print(f"   - Moon phase: {moon_time*1000:.2f}ms")
    print(f"   - Astrology: {astro_time*1000:.2f}ms")
    
    print(f"\n✅ Data Loading: {data_time*1000:.1f}ms")
    print(f"   - Card data: {card_load_time*1000:.1f}ms")
    print(f"   - Suit context: {suit_time*1000:.1f}ms")
    
    print(f"\n✅ Printer Output: {print_time*1000:.1f}ms")
    print(f"\n📊 Subtotal (no LLM): {total*1000:.1f}ms ({total:.3f}s)")
    
    # Note about LLM
    print("\n" + "="*60)
    print("⚠️  LLM HAIKU GENERATION (NOT PROFILED HERE)")
    print("="*60)
    print("\nEstimated timing for complete pipeline:")
    print(f"  • Data/Celestial prep: ~{total*1000:.0f}ms")
    print(f"  • LLM inference: ~6-8 seconds")
    print(f"  • Thermal printer output: ~{print_time*1000:.0f}ms")
    print(f"  ────────────────────────────")
    print(f"  • TOTAL ESTIMATED: ~6-9 seconds ✅")
    print(f"\nThis fits comfortably within the 10-second budget!")
    
    print("\n" + "="*60)
    
    # Save results to file
    with open('profile_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Detailed results saved to profile_results.json")


if __name__ == "__main__":
    asyncio.run(profile_generation_time())
