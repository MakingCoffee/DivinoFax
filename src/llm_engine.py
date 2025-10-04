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
    
    async def generate_haiku(self, inspiration_text: str, context: str = "") -> Optional[str]:
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
    
    async def generate_haiku(self, inspiration_text: str, context: str = "") -> Optional[str]:
        """Generate haiku using Llama model."""
        if not self.is_loaded:
            return None
        
        # Create haiku generation prompt
        prompt = self._create_haiku_prompt(inspiration_text, context)
        
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
    
    def _create_haiku_prompt(self, inspiration_text: str, context: str) -> str:
        """Create a prompt for haiku generation."""
        prompt = f"""You are a mystical fortune teller creating poetic haikus that reveal the future. 

Write a haiku (exactly 3 lines, 5-7-5 syllables) inspired by this text:
"{inspiration_text[:200]}..."

The haiku should be:
- Mystical and fortune-telling in nature
- Exactly 5 syllables, then 7 syllables, then 5 syllables
- About destiny, future, or spiritual guidance
- Beautiful and meaningful

Haiku:"""
        
        return prompt
    
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
        """Extract haiku from generated text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for 3-line structure
        if len(lines) >= 3:
            # Take first 3 non-empty lines
            haiku_lines = lines[:3]
            return '\n'.join(haiku_lines)
        elif len(lines) == 1:
            # Try to split on common separators
            for sep in [' / ', '/', ' | ', '|']:
                if sep in lines[0]:
                    parts = lines[0].split(sep)
                    if len(parts) >= 3:
                        return '\n'.join(part.strip() for part in parts[:3])
        
        # Return what we have, even if not perfect
        return '\n'.join(lines) if lines else ""
    
    def _validate_haiku(self, haiku: str) -> bool:
        """Validate haiku structure."""
        if not haiku or haiku.count('\n') != 2:
            return False
        
        lines = haiku.split('\n')
        if len(lines) != 3:
            return False
        
        # Check for reasonable line lengths (syllable estimation)
        if self.config.strict_haiku_format:
            syllable_counts = [self._estimate_syllables(line) for line in lines]
            target = [5, 7, 5]
            
            # Allow some variation if configured
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
    
    async def generate_haiku(self, inspiration_text: str, rfid_code: str = "") -> Optional[str]:
        """Generate a haiku based on inspiration text."""
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        self.generation_stats["total_requests"] += 1
        
        try:
            logger.info(f"Generating haiku for RFID {rfid_code}")
            haiku = await self.engine.generate_haiku(inspiration_text, rfid_code)
            
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
