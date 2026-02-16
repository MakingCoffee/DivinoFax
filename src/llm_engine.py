"""
LLM Engine Module for Divinofax
===============================

Claude API engine for fast haiku generation on Raspberry Pi.
Optimized for low-latency responses with internet connectivity.

Author: Kathryn Bennett
"""

import asyncio
import logging
import re
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LlamaConfig:
    """Configuration for Claude API haiku generation."""
    # Claude API settings
    claude_api_key: str = ""  # Claude API key (loaded from environment or config)
    claude_model: str = "claude-3-5-sonnet-20241022"  # Model selection
    claude_temperature: float = 0.8  # Generation temperature (creativity)
    claude_max_tokens: int = 50  # Max tokens for haiku (optimized for speed)

    # Haiku validation
    strict_haiku_format: bool = True  # Always require 3-line format
    allow_near_haiku: bool = True  # Allow ±1 syllable tolerance (e.g., 4-7-5 or 6-7-5)


class ClaudeAPIEngine:
    """Claude API engine for fast, reliable haiku generation."""

    def __init__(self, config: LlamaConfig):
        self.config = config
        self.is_loaded = False
        self._prompt_template = None

        # Validate API key
        if not self.config.claude_api_key or not self.config.claude_api_key.strip():
            logger.warning("Claude API key not configured")
        else:
            self.is_loaded = True
            logger.info(f"Claude API engine initialized with model: {self.config.claude_model}")
            # Pre-compile prompt template for efficiency
            self._prompt_template = "Generate a haiku (5-7-5 syllables) that is a mystical oracle reading.\n\nOracle Message: {context}\n\nWrite only the haiku, nothing else. Each line should contain exactly the correct number of syllables."

    async def generate_haiku(
        self,
        inspiration_text: str,
        context: str = "",
        moon_context: dict = None,
        astro_context: dict = None
    ) -> Optional[str]:
        """Generate haiku using Claude API."""
        if not self.is_loaded or not self.config.claude_api_key:
            logger.error("Claude API key not configured")
            return None

        # Create haiku generation prompt
        prompt = self._create_haiku_prompt(inspiration_text, moon_context, astro_context)

        try:
            # Run API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._make_blocking_request, prompt)

            if response:
                haiku = self._extract_haiku(response)
                if self._validate_haiku(haiku):
                    logger.info(f"Generated valid haiku: {haiku}")
                    return haiku
                else:
                    logger.warning(f"Generated invalid haiku: {haiku}")

        except Exception as e:
            logger.error(f"Error generating haiku via Claude API: {e}")

        return None

    def _make_blocking_request(self, prompt: str) -> str:
        """Make blocking HTTP request to Claude API."""
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=self.config.claude_api_key)
            message = client.messages.create(
                model=self.config.claude_model,
                max_tokens=self.config.claude_max_tokens,
                temperature=self.config.claude_temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            if message.content and len(message.content) > 0:
                return message.content[0].text
            return ""

        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
            raise

    def _create_haiku_prompt(
        self,
        inspiration_text: str,
        moon_context: dict = None,
        astro_context: dict = None
    ) -> str:
        """Create an optimized haiku prompt for Claude API."""
        # Build context string minimally
        context_parts = [inspiration_text]

        if moon_context and moon_context.get('prompt_addition'):
            context_parts.append(moon_context['prompt_addition'])

        if astro_context and astro_context.get('prompt_addition'):
            context_parts.append(astro_context['prompt_addition'])

        context_str = " ".join(context_parts)

        # Use pre-compiled template for efficiency
        return self._prompt_template.format(context=context_str)

    def _extract_haiku(self, text: str) -> str:
        """Extract haiku from generated text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Take first 3 lines (haiku format)
        if len(lines) >= 3:
            return '\n'.join(lines[:3])
        elif len(lines) == 1:
            # Try to split on common separators
            for sep in [' / ', '/', ' | ', '|']:
                if sep in lines[0]:
                    parts = lines[0].split(sep)
                    if len(parts) >= 3:
                        return '\n'.join(part.strip() for part in parts[:3])

        # Return what we have
        return '\n'.join(lines) if lines else ""

    def _validate_haiku(self, haiku: str) -> bool:
        """Validate haiku structure (3 lines with 5-7-5 syllables)."""
        if not haiku:
            return False

        lines = [line.strip() for line in haiku.split('\n') if line.strip()]

        # Require exactly 3 lines (haiku format)
        if len(lines) != 3:
            return False

        # Check syllable counts
        syllable_counts = [self._estimate_syllables(line) for line in lines]
        target = [5, 7, 5]

        if self.config.allow_near_haiku:
            # Allow ±1 syllable tolerance
            tolerance = 1
            for i, (actual, expected) in enumerate(zip(syllable_counts, target)):
                if abs(actual - expected) > tolerance:
                    return False
        else:
            # Require exact match
            if syllable_counts != target:
                return False

        return True

    def _estimate_syllables(self, text: str) -> int:
        """Estimate syllable count for haiku validation."""
        # Simple vowel-based syllable counting
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False

        for char in text:
            if char in vowels:
                if not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False

        # Adjust for common patterns
        if text.endswith('e'):
            syllables -= 1
        if text.endswith('le') and len(text) > 2:
            syllables += 1

        # Ensure at least 1 syllable
        return max(1, syllables)

    def cleanup(self):
        """Cleanup resources (no-op for API engine)."""
        pass


class LlamaEngine:
    """Legacy class for backward compatibility - redirects to Claude API."""

    def __init__(self, config: LlamaConfig):
        self.config = config
        self.claude_engine = ClaudeAPIEngine(config)
        logger.info("LlamaEngine instance created (using Claude API backend)")

    async def generate_haiku(self, *args, **kwargs) -> Optional[str]:
        """Generate haiku using Claude API backend."""
        return await self.claude_engine.generate_haiku(*args, **kwargs)

    def cleanup(self):
        """Cleanup resources."""
        self.claude_engine.cleanup()


def create_engine(config: LlamaConfig) -> LlamaEngine:
    """Factory function to create LLM engine."""
    return LlamaEngine(config)
