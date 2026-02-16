"""
Astrology Module for Divinofax
===============================

Calculates current astrological sun sign and provides thematic guidance
for haiku generation. Lightweight, no external dependencies needed.

Author: Kathryn Bennett
"""

import logging
from datetime import datetime
from typing import Dict, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class AstrologySign(Enum):
    """Enumeration of zodiac signs."""
    ARIES = "aries"
    TAURUS = "taurus"
    GEMINI = "gemini"
    CANCER = "cancer"
    LEO = "leo"
    VIRGO = "virgo"
    LIBRA = "libra"
    SCORPIO = "scorpio"
    SAGITTARIUS = "sagittarius"
    CAPRICORN = "capricorn"
    AQUARIUS = "aquarius"
    PISCES = "pisces"


class AstrologyCalculator:
    """Calculate current astrological sign and provide guidance."""

    # Zodiac dates (month, day) for sign transitions
    ZODIAC_DATES = [
        ((3, 21), (4, 19), AstrologySign.ARIES),
        ((4, 20), (5, 20), AstrologySign.TAURUS),
        ((5, 21), (6, 20), AstrologySign.GEMINI),
        ((6, 21), (7, 22), AstrologySign.CANCER),
        ((7, 23), (8, 22), AstrologySign.LEO),
        ((8, 23), (9, 22), AstrologySign.VIRGO),
        ((9, 23), (10, 22), AstrologySign.LIBRA),
        ((10, 23), (11, 21), AstrologySign.SCORPIO),
        ((11, 22), (12, 21), AstrologySign.SAGITTARIUS),
        ((12, 22), (1, 19), AstrologySign.CAPRICORN),
        ((1, 20), (2, 18), AstrologySign.AQUARIUS),
        ((2, 19), (3, 20), AstrologySign.PISCES),
    ]

    def __init__(self):
        self.is_initialized = True

    def get_current_sign(self) -> AstrologySign:
        """Get the current astrological sun sign."""
        today = datetime.now()
        month, day = today.month, today.day

        for (start_month, start_day), (end_month, end_day), sign in self.ZODIAC_DATES:
            # Handle year-wrapping signs (Capricorn)
            if start_month > end_month:
                if month == start_month and day >= start_day:
                    return sign
                elif month == end_month and day <= end_day:
                    return sign
            else:
                if month == start_month and day >= start_day:
                    if month == end_month and day <= end_day:
                        return sign
                elif month == end_month and day <= end_day:
                    if month == start_month and day >= start_day:
                        return sign
                elif start_month < month < end_month:
                    return sign

        # Fallback (shouldn't reach here)
        return AstrologySign.PISCES

    @staticmethod
    def get_sign_guidance(sign: AstrologySign) -> Dict[str, str]:
        """Get thematic guidance and context for an astrological sign."""
        guidance_map = {
            AstrologySign.ARIES: {
                "name": "Aries",
                "element": "Fire",
                "theme": "Courage, initiation, bold action, pioneering spirit",
                "guidance": "The seeker's energy is charged with courage. What brave first step awaits?",
                "prompt_addition": "as Aries energy fuels courageous action",
                "keywords": ["courage", "pioneer", "action", "initiation", "boldness"]
            },
            AstrologySign.TAURUS: {
                "name": "Taurus",
                "element": "Earth",
                "theme": "Stability, grounding, sensuality, material manifestation",
                "guidance": "The seeker seeks steady ground. What foundation needs building?",
                "prompt_addition": "as Taurus grounds intention into physical reality",
                "keywords": ["stability", "grounding", "manifestation", "sensuality", "abundance"]
            },
            AstrologySign.GEMINI: {
                "name": "Gemini",
                "element": "Air",
                "theme": "Communication, curiosity, connection, duality of truth",
                "guidance": "The seeker's mind is alive with possibility. What needs expressing?",
                "prompt_addition": "as Gemini weaves threads of connection and curiosity",
                "keywords": ["communication", "curiosity", "connection", "learning", "versatility"]
            },
            AstrologySign.CANCER: {
                "name": "Cancer",
                "element": "Water",
                "theme": "Emotional depth, nurturing, intuition, belonging",
                "guidance": "The seeker's heart knows what logic cannot. What needs tending?",
                "prompt_addition": "as Cancer feels deeply into intuitive knowing",
                "keywords": ["emotion", "nurturing", "intuition", "belonging", "protection"]
            },
            AstrologySign.LEO: {
                "name": "Leo",
                "element": "Fire",
                "theme": "Self-expression, radiance, creativity, authentic power",
                "guidance": "The seeker's light wants to shine. How will you glow?",
                "prompt_addition": "as Leo's radiance illuminates authentic self-expression",
                "keywords": ["creativity", "radiance", "power", "authenticity", "celebration"]
            },
            AstrologySign.VIRGO: {
                "name": "Virgo",
                "element": "Earth",
                "theme": "Integration, refinement, wisdom through service, discernment",
                "guidance": "The seeker seeks clarity. What needs refining or healing?",
                "prompt_addition": "as Virgo discerns what serves true healing",
                "keywords": ["refinement", "clarity", "healing", "service", "integration"]
            },
            AstrologySign.LIBRA: {
                "name": "Libra",
                "element": "Air",
                "theme": "Balance, harmony, relationships, choosing consciously",
                "guidance": "The seeker weighs their choices. What needs balancing?",
                "prompt_addition": "as Libra seeks harmony and conscious choice",
                "keywords": ["balance", "harmony", "relationship", "choice", "beauty"]
            },
            AstrologySign.SCORPIO: {
                "name": "Scorpio",
                "element": "Water",
                "theme": "Transformation, intensity, truth-seeking, alchemical power",
                "guidance": "The seeker gazes into shadow. What is being reborn?",
                "prompt_addition": "as Scorpio transforms darkness into alchemical power",
                "keywords": ["transformation", "intensity", "truth", "power", "rebirth"]
            },
            AstrologySign.SAGITTARIUS: {
                "name": "Sagittarius",
                "element": "Fire",
                "theme": "Expansion, exploration, wisdom, visionary hope",
                "guidance": "The seeker's vision expands. What horizon calls?",
                "prompt_addition": "as Sagittarius expands toward distant visions",
                "keywords": ["expansion", "wisdom", "exploration", "hope", "vision"]
            },
            AstrologySign.CAPRICORN: {
                "name": "Capricorn",
                "element": "Earth",
                "theme": "Mastery, responsibility, building legacy, patient ambition",
                "guidance": "The seeker builds something lasting. What are you creating?",
                "prompt_addition": "as Capricorn masters the long climb upward",
                "keywords": ["mastery", "responsibility", "ambition", "legacy", "discipline"]
            },
            AstrologySign.AQUARIUS: {
                "name": "Aquarius",
                "element": "Air",
                "theme": "Revolution, innovation, collective consciousness, liberation",
                "guidance": "The seeker dreams beyond convention. What wants liberating?",
                "prompt_addition": "as Aquarius channels revolutionary innovation",
                "keywords": ["innovation", "liberation", "consciousness", "revolution", "future"]
            },
            AstrologySign.PISCES: {
                "name": "Pisces",
                "element": "Water",
                "theme": "Surrender, flow, mystical connection, boundless compassion",
                "guidance": "The seeker dissolves into the mystery. What do you release?",
                "prompt_addition": "as Pisces flows with mystical compassion",
                "keywords": ["surrender", "flow", "mystery", "compassion", "dissolution"]
            }
        }

        return guidance_map.get(sign, {
            "name": "Unknown Sign",
            "element": "Mystery",
            "theme": "Cosmic alignment",
            "guidance": "Trust the stars.",
            "prompt_addition": "",
            "keywords": []
        })


async def test_astrology_calculator():
    """Test the astrology calculator."""
    calculator = AstrologyCalculator()

    print("Testing Astrology Calculator\n")

    sign = calculator.get_current_sign()
    print(f"Current Astrological Sign: {sign.name.title()}")

    guidance = calculator.get_sign_guidance(sign)
    print(f"\nSign Guidance:")
    print(f"  Element: {guidance['element']}")
    print(f"  Theme: {guidance['theme']}")
    print(f"  Guidance: {guidance['guidance']}")
    print(f"  Prompt Addition: {guidance['prompt_addition']}")
    print(f"  Keywords: {', '.join(guidance['keywords'])}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_astrology_calculator())
