"""
Moon Phase Module for Divinofax
================================

Calculates current moon phase and provides astrological context
for haiku generation. Uses ephem (PyEphemerris) for accurate
astronomical calculations optimized for Raspberry Pi.

Author: Kathryn Bennett
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Tuple
from enum import Enum

try:
    import ephem
    HAS_EPHEM = True
except ImportError:
    HAS_EPHEM = False
    print("Warning: ephem library not available. Install with: pip install ephem")

logger = logging.getLogger(__name__)


class MoonPhase(Enum):
    """Enumeration of moon phases."""
    NEW_MOON = "new"
    WAXING_CRESCENT = "waxing_crescent"
    FIRST_QUARTER = "first_quarter"
    WAXING_GIBBOUS = "waxing_gibbous"
    FULL_MOON = "full"
    WANING_GIBBOUS = "waning_gibbous"
    LAST_QUARTER = "last_quarter"
    WANING_CRESCENT = "waning_crescent"


class MoonPhaseCalculator:
    """Calculate moon phase and provide astrological guidance."""

    def __init__(self):
        self.is_initialized = HAS_EPHEM

    def get_current_phase(self) -> Dict[str, str]:
        """Get current moon phase with full guidance dictionary (synchronous)."""
        phase, illumination = self._get_phase_tuple()
        guidance = self.get_phase_guidance(phase)
        guidance['illumination'] = illumination
        return guidance

    def _get_phase_tuple(self) -> Tuple[MoonPhase, float]:
        """Get current moon phase as tuple. Internal method."""
        if not HAS_EPHEM:
            return self._calculate_phase_fallback()

        try:
            return self._calculate_phase_ephem()
        except Exception as e:
            logger.error(f"Error calculating moon phase: {e}")
            return self._calculate_phase_fallback()

    async def get_current_phase_async(self) -> Tuple[MoonPhase, float]:
        """Get current moon phase. Returns (MoonPhase enum, illumination %)"""
        if not HAS_EPHEM:
            return self._calculate_phase_fallback()

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._calculate_phase_ephem)
        except Exception as e:
            logger.error(f"Error calculating moon phase: {e}")
            return self._calculate_phase_fallback()

    def _calculate_phase_ephem(self) -> Tuple[MoonPhase, float]:
        """Calculate moon phase using ephem library."""
        now = datetime.now()
        observer = ephem.Observer()
        observer.date = now
        moon = ephem.Moon(observer)
        illumination = moon.phase

        next_new = ephem.next_new_moon(now)
        next_first = ephem.next_first_quarter_moon(now)
        next_full = ephem.next_full_moon(now)
        next_last = ephem.next_last_quarter_moon(now)
        prev_new = ephem.previous_new_moon(now)
        prev_first = ephem.previous_first_quarter_moon(now)
        prev_full = ephem.previous_full_moon(now)
        prev_last = ephem.previous_last_quarter_moon(now)

        now_datetime = ephem.Date(now)

        if now_datetime < next_first and now_datetime >= prev_new:
            phase = MoonPhase.WAXING_CRESCENT
        elif now_datetime < next_full and now_datetime >= prev_first:
            phase = MoonPhase.WAXING_GIBBOUS
        elif now_datetime < next_last and now_datetime >= prev_full:
            phase = MoonPhase.WANING_GIBBOUS
        elif now_datetime < next_new and now_datetime >= prev_last:
            phase = MoonPhase.WANING_CRESCENT
        else:
            phase = MoonPhase.WAXING_CRESCENT

        return phase, illumination

    def _calculate_phase_fallback(self) -> Tuple[MoonPhase, float]:
        """Fallback moon phase calculation using simple algorithm."""
        known_new_moon = datetime(2025, 1, 29)
        lunar_cycle = 29.53058867

        days_since = (datetime.now() - known_new_moon).days
        position_in_cycle = (days_since % lunar_cycle) / lunar_cycle
        illumination = 100 * (1 - abs(1 - 2 * position_in_cycle)) / 2

        if position_in_cycle < 0.0625:
            phase = MoonPhase.NEW_MOON
        elif position_in_cycle < 0.1875:
            phase = MoonPhase.WAXING_CRESCENT
        elif position_in_cycle < 0.3125:
            phase = MoonPhase.FIRST_QUARTER
        elif position_in_cycle < 0.4375:
            phase = MoonPhase.WAXING_GIBBOUS
        elif position_in_cycle < 0.5625:
            phase = MoonPhase.FULL_MOON
        elif position_in_cycle < 0.6875:
            phase = MoonPhase.WANING_GIBBOUS
        elif position_in_cycle < 0.8125:
            phase = MoonPhase.LAST_QUARTER
        else:
            phase = MoonPhase.WANING_CRESCENT

        return phase, illumination

    @staticmethod
    def get_phase_guidance(phase: MoonPhase) -> Dict[str, str]:
        """Get thematic guidance and context for a moon phase."""
        guidance_map = {
            MoonPhase.NEW_MOON: {
                "name": "New Moon",
                "theme": "Beginnings, intentions, darkness pregnant with possibility",
                "guidance": "A time of new intentions and fresh starts. What are you calling into being?",
                "prompt_addition": "under a new moon of fresh beginnings",
                "keywords": ["initiation", "intention", "potential", "renewal"]
            },
            MoonPhase.WAXING_CRESCENT: {
                "name": "Waxing Crescent",
                "theme": "Growth, intention-setting, early momentum",
                "guidance": "Energy is building. Plant your seeds and nurture your intentions.",
                "prompt_addition": "as the moon grows toward fullness",
                "keywords": ["growth", "momentum", "action", "manifestation"]
            },
            MoonPhase.FIRST_QUARTER: {
                "name": "First Quarter",
                "theme": "Challenge, decision, overcoming obstacles",
                "guidance": "Time to push through obstacles. What decisions are you facing?",
                "prompt_addition": "at the first quarter moon of challenge and decision",
                "keywords": ["challenge", "decision", "strength", "breakthrough"]
            },
            MoonPhase.WAXING_GIBBOUS: {
                "name": "Waxing Gibbous",
                "theme": "Refinement, improvement, fine-tuning",
                "guidance": "Almost there. Refine and perfect what you're building.",
                "prompt_addition": "as the moon nearly reaches fullness",
                "keywords": ["refinement", "completion", "detail", "polish"]
            },
            MoonPhase.FULL_MOON: {
                "name": "Full Moon",
                "theme": "Culmination, illumination, revelation, power",
                "guidance": "Everything is illuminated. What truth is being revealed?",
                "prompt_addition": "under the full moon's revealing light",
                "keywords": ["fullness", "illumination", "power", "truth"]
            },
            MoonPhase.WANING_GIBBOUS: {
                "name": "Waning Gibbous",
                "theme": "Gratitude, sharing, wisdom, harvest",
                "guidance": "Share your gifts and wisdom. Reap what you've sown.",
                "prompt_addition": "as the moon begins to wane in gratitude",
                "keywords": ["gratitude", "sharing", "wisdom", "harvest"]
            },
            MoonPhase.LAST_QUARTER: {
                "name": "Last Quarter",
                "theme": "Release, reflection, rest, letting go",
                "guidance": "Time to release what no longer serves. What must you let go of?",
                "prompt_addition": "at the last quarter moon of release and reflection",
                "keywords": ["release", "reflection", "rest", "closure"]
            },
            MoonPhase.WANING_CRESCENT: {
                "name": "Waning Crescent",
                "theme": "Surrender, dreams, intuition, endings",
                "guidance": "Surrender to what is ending. Listen to your intuition.",
                "prompt_addition": "under a waning crescent of dreams and surrender",
                "keywords": ["surrender", "dreams", "intuition", "transition"]
            }
        }

        return guidance_map.get(phase, {
            "name": "Unknown Phase",
            "theme": "Mystery",
            "guidance": "Trust the cosmic timing.",
            "prompt_addition": "",
            "keywords": []
        })
