#!/usr/bin/env python3
"""
Test script for Claude API integration with Divinofax
Tests haiku generation with all context (moon phase, zodiac, etc.)
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_engine import LlamaConfig, LlamaEngine
from moon_phase import MoonPhaseCalculator
from astrology import AstrologyCalculator


async def test_claude_haiku_generation():
    """Test Claude API haiku generation with full context."""

    # Check for API key
    api_key = os.environ.get('CLAUDE_API_KEY', '')
    if not api_key:
        print("❌ CLAUDE_API_KEY not set in environment")
        print("   Set it with: export CLAUDE_API_KEY=sk-...")
        return False

    print("\n=== Divinofax Claude API Integration Test ===\n")

    # Configure Claude API engine
    config = LlamaConfig(
        use_claude_api=True,
        claude_api_key=api_key,
        claude_model="claude-3-5-sonnet-20241022",
        claude_temperature=0.8,
        claude_max_tokens=150
    )

    print(f"✓ Configuration loaded")
    print(f"  - Using Claude API: True")
    print(f"  - Model: {config.claude_model}")
    print(f"  - API Key: {api_key[:7]}...{api_key[-4:] if len(api_key) > 11 else ''}\n")

    # Initialize LLM engine
    llm_engine = LlamaEngine(config)
    print(f"✓ LLM Engine initialized\n")

    # Get celestial context
    moon_calc = MoonPhaseCalculator()
    astro_calc = AstrologyCalculator()

    moon_context = moon_calc.get_moon_phase_context()
    astro_context = astro_calc.get_current_astrology_context()

    print("=== Generating test haikus with context ===\n")

    # Test prompts
    test_cases = [
        {
            "name": "Transformation",
            "text": "The Phoenix Card: A symbol of rebirth, transformation, and rising from the ashes of what came before. This card speaks of metamorphosis, of shedding old skin and emerging renewed. It is the promise that from every ending comes a new beginning."
        },
        {
            "name": "Communication",
            "text": "The Signal Card: Clear communication and voice. A card of signals piercing through the darkness, of voices finally being heard. It speaks to speaking your truth and having your message received and understood."
        },
        {
            "name": "Grounding",
            "text": "The Circuit Card: Embodiment and connection. This card represents being fully present in your body and connected to the earth. It speaks of sensation, of feeling fully alive in this moment, grounded in the present."
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 40}")

        start_time = time.time()

        try:
            haiku = await llm_engine.generate_haiku(
                inspiration_text=test['text'],
                rfid_code=f"test_{i:03d}",
                moon_context=moon_context,
                astro_context=astro_context
            )

            elapsed = time.time() - start_time

            if haiku:
                print(f"⏱️  Generation time: {elapsed:.2f}s")
                print(f"✓ Generated haiku:")
                print(f"\n{haiku}\n")

                results.append({
                    "name": test['name'],
                    "success": True,
                    "time": elapsed,
                    "haiku": haiku
                })
            else:
                print(f"❌ Failed to generate haiku\n")
                results.append({
                    "name": test['name'],
                    "success": False,
                    "time": elapsed
                })

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error: {e}\n")
            results.append({
                "name": test['name'],
                "success": False,
                "error": str(e),
                "time": elapsed
            })

    # Shutdown
    await llm_engine.shutdown()

    # Summary
    print("=== Test Summary ===\n")
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    avg_time = sum(r.get('time', 0) for r in results if r.get('success')) / successful if successful > 0 else 0

    print(f"Success rate: {successful}/{total} ({100*successful/total:.0f}%)")
    print(f"Average generation time: {avg_time:.2f}s")

    if successful == total:
        print("\n✅ All tests passed! Claude API integration is working.")
        return True
    else:
        print(f"\n⚠️  {total - successful} test(s) failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_claude_haiku_generation())
    sys.exit(0 if success else 1)
