"""
LLM Engine Module for Divinofax
===============================

Handles local Llama LLM execution on Raspberry Pi for haiku generation.
Optimized for 4GB Pi with efficient model loading and memory management.

Author: Kathryn Bennett
"""

import asyncio
import logging
import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False
    print("Warning: llama-cpp-python not available. Running in simulation mode.")

logger = logging.getLogger(__name__)


@dataclass
class LlamaConfig:
    """Configuration for Llama LLM engine."""
    # Model settings
    model_path: str = "models/llama-2-7b-chat.Q4_0.gguf"  # Quantized for Pi
    backup_model_path: str = "models/llama-2-7b.Q2_K.gguf"  # Even smaller backup
    
    # Performance settings for Raspberry Pi
    n_ctx: int = 1024      # Context window (smaller for Pi)
    n_threads: int = 4      # Pi 4 has 4 cores
    n_gpu_layers: int = 0   # No GPU on Pi
    
    # Generation settings
    max_tokens: int = 150   # Haikus are short
    temperature: float = 0.8
    top_p: float = 0.9
    repeat_penalty: float = 1.1
    
    # Haiku validation
    strict_haiku_format: bool = True
    allow_near_haiku: bool = True  # Allow 5-7-5 syllable variations
    
    # Simulation mode
    simulation_mode: bool = False


class MockLlamaEngine:
    """Mock LLM engine for testing without actual model."""
    
    def __init__(self, config: LlamaConfig):
        self.config = config
        self.sample_haikus = [
            "Stars whisper secrets\nCosmic winds carry your dreams\nDestiny awaits",
            "Ancient trees hold truth\nRoots deep in earth's sacred soil\nWisdom grows within",
            "Rivers of time flow\nPast and future merge as one\nPresent moment shines",
            "Fire transforms all\nBurning away old patterns\nPhoenix soul rises",
            "Mountain peaks reach high\nTouching clouds of possibility\nSummit calls to you"
        ]
        logger.info("Mock Llama engine initialized")
    
    async def generate_haiku(self, inspiration_text: str, context: str = "", moon_context: dict = None, astro_context: dict = None) -> Optional[str]:
        """Generate a mock haiku."""
        await asyncio.sleep(2)  # Simulate processing time

        import random
        haiku = random.choice(self.sample_haikus)
        logger.info(f"Mock haiku generated: {haiku}")
        return haiku
    
    def cleanup(self):
        """Cleanup mock engine."""
        pass


class RealLlamaEngine:
    """Real Llama engine using llama-cpp-python."""
    
    def __init__(self, config: LlamaConfig):
        self.config = config
        self.model = None
        self.is_loaded = False
        
    def load_model(self):
        """Load the Llama model with error handling."""
        model_paths = [self.config.model_path]
        if self.config.backup_model_path:
            model_paths.append(self.config.backup_model_path)
        
        for model_path in model_paths:
            try:
                if Path(model_path).exists():
                    logger.info(f"Loading Llama model from: {model_path}")
                    
                    self.model = Llama(
                        model_path=model_path,
                        n_ctx=self.config.n_ctx,
                        n_threads=self.config.n_threads,
                        n_gpu_layers=self.config.n_gpu_layers,
                        verbose=False  # Reduce logging for Pi
                    )
                    
                    self.is_loaded = True
                    logger.info("Llama model loaded successfully")
                    return
                else:
                    logger.warning(f"Model not found: {model_path}")
                    
            except Exception as e:
                logger.error(f"Failed to load model {model_path}: {e}")
                continue
        
        raise RuntimeError("Failed to load any Llama model")
    
    async def generate_haiku(self, inspiration_text: str, context: str = "", moon_context: dict = None, astro_context: dict = None) -> Optional[str]:
        """Generate haiku using Llama model."""
        if not self.is_loaded:
            return None

        # Create haiku generation prompt
        prompt = self._create_haiku_prompt(inspiration_text, context, moon_context, astro_context)
        
        try:
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._generate_text, prompt)
            
            if response:
                haiku = self._extract_haiku(response)
                if self._validate_haiku(haiku):
                    logger.info(f"Generated valid haiku: {haiku}")
                    return haiku
                else:
                    logger.warning(f"Generated invalid haiku: {haiku}")
            
        except Exception as e:
            logger.error(f"Error generating haiku: {e}")
        
        return None
    
    def _create_haiku_prompt(self, inspiration_text: str, context: str, moon_context: dict = None, astro_context: dict = None) -> str:
        """Create an enhanced prompt for haiku generation with richer context."""

        # Parse context to extract card information if available
        card_context = self._parse_card_context(context)

        # Add moon context if provided
        moon_addition = ""
        if moon_context and moon_context.get('prompt_addition'):
            moon_addition = f"\nCELESTIAL TIMING: The seeker draws this card {moon_context['prompt_addition']}."

        # Add astrological context if provided
        astro_addition = ""
        if astro_context and astro_context.get('prompt_addition'):
            astro_addition = f"\nASTROLOGICAL INFLUENCE: {astro_context['prompt_addition']}."

        # Build the prompt with layered guidance
        prompt = f"""You are a mystical oracle, channeling profound wisdom through the art of poetry. Your words reveal hidden truths and guide seekers toward their destiny.

ORACLE CARD GUIDANCE:
{inspiration_text}{moon_addition}{astro_addition}

INSTRUCTIONS FOR YOUR POEM:
1. Form: Choose what fits best - haiku (5-7-5), couplet (2 lines), tercet (3 lines), or free verse
2. Essence: Capture the deep truth within the oracle card's meaning
3. Tone: {card_context.get('tone', 'mystical and prophetic')}
4. Focus: Speak to the seeker's current transformation or revelation
5. Language: Use vivid, poetic imagery; avoid clichés
6. Length: Keep it concise (2-4 lines ideally) for a fortune slip

POETIC FORM EXAMPLES:

HAIKU (if it fits naturally):
- "Signals pierce the dark / Lost voices find their echo / You are finally heard"

COUPLET (2 lines):
- "Your truth pierces the silence / Recognition floods in"

TERCET (3 lines):
- "What was hidden calls to you / Your signal grows stronger / The world begins to hear"

FREE VERSE (2-4 lines):
- "In the dark, a signal blazes forth— / your voice, finally reaching"

Choose the form that best captures this seeker's oracle message. Let the card, the moon, and the stars guide your words.

POEM:"""

        return prompt

    def _parse_card_context(self, context: str) -> dict:
        """Parse RFID context to extract suit/card information."""
        card_info = {
            'tone': 'mystical and prophetic',
            'suit': None,
            'card_number': None
        }

        # Try to extract card number from context
        if context and isinstance(context, str):
            # If context looks like a card number (001-075)
            try:
                # Extract number from context string
                import re
                match = re.search(r'(\d+)', context)
                if match:
                    num = int(match.group(1))
                    card_info['card_number'] = num

                    # Determine suit based on card number (1-15, 16-30, etc.)
                    suit_num = (num - 1) // 15 + 1
                    suits = {
                        1: ('The Signal', 'transmission and communication - speak your truth with clarity'),
                        2: ('The Circuit', 'embodiment and sensation - feel your transformation deeply'),
                        3: ('The Archive', 'memory and witness - hold the wisdom of what came before'),
                        4: ('The Glitch', 'disruption and revelation - embrace the beauty in breaking'),
                        5: ('The Sync', 'resonance and harmony - align with the rhythm of becoming')
                    }

                    if suit_num in suits:
                        suit_name, tone = suits[suit_num]
                        card_info['suit'] = suit_name
                        card_info['tone'] = tone
            except:
                pass

        return card_info
    
    def _generate_text(self, prompt: str) -> str:
        """Generate text using Llama model (blocking call)."""
        try:
            response = self.model(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                repeat_penalty=self.config.repeat_penalty,
                stop=["\n\n", "---", "Context:", "Inspiration:"],
                echo=False
            )
            
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["text"].strip()
                
        except Exception as e:
            logger.error(f"Model generation error: {e}")
        
        return ""
    
    def _extract_haiku(self, text: str) -> str:
        """Extract poem from generated text - supports multiple poetic forms."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Try to get 2-4 lines (flexible poem form)
        if len(lines) >= 2:
            # Take first 2-4 non-empty lines
            poem_lines = lines[:4] if len(lines) >= 4 else lines
            return '\n'.join(poem_lines)
        elif len(lines) == 1:
            # Try to split on common separators
            for sep in [' / ', '/', ' | ', '|']:
                if sep in lines[0]:
                    parts = lines[0].split(sep)
                    if len(parts) >= 2:
                        return '\n'.join(part.strip() for part in parts[:4])

        # Return what we have, even if not perfect
        return '\n'.join(lines) if lines else ""
    
    def _validate_haiku(self, haiku: str) -> bool:
        """Validate poem structure - flexible across multiple forms."""
        if not haiku:
            return False

        lines = [line.strip() for line in haiku.split('\n') if line.strip()]

        # Accept any poem with 2-4 lines (couplet, tercet, haiku, or short verse)
        if len(lines) < 2 or len(lines) > 4:
            return False

        # For strict haiku format validation (only if config requires it)
        if self.config.strict_haiku_format and len(lines) == 3:
            syllable_counts = [self._estimate_syllables(line) for line in lines]
            target = [5, 7, 5]

            if self.config.allow_near_haiku:
                tolerance = 1
                for i, (actual, expected) in enumerate(zip(syllable_counts, target)):
                    if abs(actual - expected) > tolerance:
                        return False
            else:
                if syllable_counts != target:
                    return False

        return True
    
    def _estimate_syllables(self, text: str) -> int:
        """Rough syllable estimation for haiku validation."""
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
        
        return max(1, syllables)  # Every word has at least 1 syllable
    
    def cleanup(self):
        """Cleanup model resources."""
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("Llama model unloaded")


class LlamaEngine:
    """Main LLM engine with fallback support."""
    
    def __init__(self, config: LlamaConfig):
        self.config = config
        self.is_initialized = False
        self.generation_stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_time": 0.0
        }
        
        # Choose implementation
        if not HAS_LLAMA_CPP or config.simulation_mode:
            self.engine = MockLlamaEngine(config)
            logger.info("Using mock LLM engine")
        else:
            self.engine = RealLlamaEngine(config)
            logger.info("Using real Llama engine")
    
    async def initialize(self):
        """Initialize the LLM engine."""
        if not self.is_initialized:
            logger.info("Initializing LLM engine...")
            
            try:
                if hasattr(self.engine, 'load_model'):
                    # Run model loading in thread pool for real engine
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.engine.load_model)
                
                self.is_initialized = True
                logger.info("LLM engine initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize LLM engine: {e}")
                # Fallback to mock engine
                if not isinstance(self.engine, MockLlamaEngine):
                    logger.info("Falling back to mock engine")
                    self.engine = MockLlamaEngine(self.config)
                    self.is_initialized = True
    
    async def shutdown(self):
        """Shutdown the LLM engine."""
        if self.is_initialized:
            logger.info("Shutting down LLM engine...")
            self.engine.cleanup()
            self.is_initialized = False
            logger.info("LLM engine shutdown complete")
    
    async def generate_haiku(self, inspiration_text: str, rfid_code: str = "", moon_context: dict = None, astro_context: dict = None) -> Optional[str]:
        """Generate a haiku based on inspiration text and optional celestial context."""
        if not self.is_initialized:
            await self.initialize()

        start_time = time.time()
        self.generation_stats["total_requests"] += 1

        try:
            logger.info(f"Generating haiku for RFID {rfid_code}")
            haiku = await self.engine.generate_haiku(inspiration_text, rfid_code, moon_context, astro_context)
            
            if haiku:
                self.generation_stats["successful_generations"] += 1
                logger.info(f"Successfully generated haiku: {haiku.replace(chr(10), ' / ')}")
            else:
                self.generation_stats["failed_generations"] += 1
                logger.warning("Failed to generate haiku")
            
            # Update timing stats
            generation_time = time.time() - start_time
            total_time = (self.generation_stats["average_time"] * 
                         (self.generation_stats["total_requests"] - 1) + generation_time)
            self.generation_stats["average_time"] = total_time / self.generation_stats["total_requests"]
            
            return haiku
            
        except Exception as e:
            logger.error(f"Error in haiku generation: {e}")
            self.generation_stats["failed_generations"] += 1
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "initialized": self.is_initialized,
            "using_mock": isinstance(self.engine, MockLlamaEngine),
            "model_loaded": getattr(self.engine, 'is_loaded', False),
            **self.generation_stats
        }


# Test function
async def test_llm_engine():
    """Test the LLM engine functionality."""
    config = LlamaConfig(simulation_mode=True)
    engine = LlamaEngine(config)
    
    print("Testing LLM engine...")
    print(f"Initial stats: {engine.get_stats()}")
    
    await engine.initialize()
    
    # Test haiku generation
    test_texts = [
        "The stars align in mysterious ways, revealing paths unknown to mortal minds.",
        "Ancient wisdom flows through sacred trees, their roots touching the very soul of earth.",
        "Fire transforms all in its cosmic dance, burning away illusion to reveal truth."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Inspiration: {text[:50]}...")
        
        haiku = await engine.generate_haiku(text, f"test_{i}")
        if haiku:
            print(f"Generated haiku:\n{haiku}")
        else:
            print("Failed to generate haiku")
    
    print(f"\nFinal stats: {engine.get_stats()}")
    await engine.shutdown()
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_llm_engine())
