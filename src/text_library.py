"""
Text Library Module for Divinofax
=================================

Manages collections of inspirational text used for haiku generation.
Maps RFID codes to specific text themes and provides relevant excerpts.

Author: Kathryn Bennett
"""

import asyncio
import json
import logging
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TextCollection:
    """A collection of related texts for a specific theme."""
    name: str
    theme: str
    texts: List[str]
    keywords: List[str]
    created_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class TextLibraryConfig:
    """Configuration for text library."""
    data_directory: str = "data/texts"
    index_file: str = "data/text_index.json"
    rfid_mappings_file: str = "data/rfid_mappings.json"
    
    # Text selection behavior
    max_text_length: int = 500  # Maximum length for inspiration text
    min_text_length: int = 50   # Minimum length for useful text
    random_selection: bool = True
    
    # Default mappings
    default_theme: str = "cosmic_wisdom"


class TextLibrary:
    """Main text library manager."""
    
    def __init__(self, config: TextLibraryConfig):
        self.config = config
        self.collections: Dict[str, TextCollection] = {}
        self.rfid_mappings: Dict[str, str] = {}  # RFID code -> theme
        self.is_initialized = False
        
        # Ensure directories exist
        Path(config.data_directory).mkdir(parents=True, exist_ok=True)
        Path(config.index_file).parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the text library by loading all collections."""
        if not self.is_initialized:
            logger.info("Initializing text library...")
            
            await self._create_sample_texts()
            await self._load_collections()
            await self._load_rfid_mappings()
            
            self.is_initialized = True
            logger.info(f"Text library initialized with {len(self.collections)} collections")
    
    async def shutdown(self):
        """Clean shutdown of text library."""
        if self.is_initialized:
            logger.info("Shutting down text library...")
            await self._save_index()
            await self._save_rfid_mappings()
            self.is_initialized = False
            logger.info("Text library shutdown complete")
    
    async def _create_sample_texts(self):
        """Create sample text collections if they don't exist."""
        data_dir = Path(self.config.data_directory)
        
        # Sample text collections with mystical themes
        sample_collections = {
            "cosmic_wisdom": {
                "texts": [
                    "In the vast cosmos, every star whispers ancient secrets to those who dare to listen. The universe conspires in your favor, aligning celestial bodies to illuminate the path ahead.",
                    "Cosmic energies flow through all living beings, connecting us to the infinite tapestry of existence. Your soul resonates with frequencies beyond mortal comprehension.",
                    "The moon's silver light carries messages from distant galaxies, where time flows differently and wisdom transcends physical form.",
                    "Among the constellation of possibilities, your destiny sparkles brightest when aligned with universal truth.",
                    "Stellar winds carry the essence of creation itself, breathing life into dreams that seemed impossible moments before."
                ],
                "keywords": ["cosmos", "stars", "universe", "celestial", "infinite", "energy"]
            },
            "nature_spirits": {
                "texts": [
                    "Ancient trees hold memories of countless seasons, their roots intertwined with the very essence of earth's wisdom.",
                    "Mountain streams sing melodies that only the pure of heart can truly understand, carrying secrets from source to sea.",
                    "The wind whispers through autumn leaves, each rustling note a message from spirits who dance between worlds.",
                    "Ocean tides mirror the rhythm of your heartbeat, connecting you to the primal pulse of all existence.",
                    "Forest shadows hide doorways to realms where time moves like honey and magic flows freely."
                ],
                "keywords": ["trees", "nature", "spirits", "wind", "ocean", "forest"]
            },
            "mystical_journey": {
                "texts": [
                    "Every step on the spiritual path reveals new layers of understanding, like peeling back veils that separate the mundane from the magical.",
                    "The labyrinth of life leads not to a destination, but to a deeper knowing of the eternal self that exists beyond time.",
                    "In dreams, we travel to places where the impossible becomes inevitable and the heart remembers its true home.",
                    "Sacred geometry underlies all existence, revealing patterns that connect the microcosm to the macrocosm in perfect harmony.",
                    "The seeker finds that what they searched for externally was always present within, waiting patiently for recognition."
                ],
                "keywords": ["journey", "spiritual", "dreams", "sacred", "wisdom", "truth"]
            },
            "elemental_forces": {
                "texts": [
                    "Fire transforms all it touches, burning away illusion to reveal the gold hidden within base metal of ordinary experience.",
                    "Water flows around obstacles with patient persistence, teaching us that gentleness can overcome the hardest resistance.",
                    "Earth provides stable foundation for growth, reminding us that even the mightiest oak begins as a humble seed.",
                    "Air carries prayers across vast distances, delivering hopes and dreams to the realm where all possibilities await manifestation.",
                    "Lightning illuminates the sky for brief moments, offering glimpses of truth that change our perspective forever."
                ],
                "keywords": ["fire", "water", "earth", "air", "elements", "transformation"]
            }
        }
        
        for theme, content in sample_collections.items():
            file_path = data_dir / f"{theme}.txt"
            if not file_path.exists():
                logger.info(f"Creating sample text collection: {theme}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    for text in content["texts"]:
                        f.write(f"{text}\n\n")
    
    async def _load_collections(self):
        """Load all text collections from files."""
        data_dir = Path(self.config.data_directory)
        
        for text_file in data_dir.glob("*.txt"):
            theme = text_file.stem
            logger.info(f"Loading text collection: {theme}")
            
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Split content into individual texts
                texts = [
                    text.strip() 
                    for text in content.split('\n\n') 
                    if len(text.strip()) >= self.config.min_text_length
                ]
                
                if texts:
                    # Extract keywords from the theme name and content
                    keywords = self._extract_keywords(theme, texts)
                    
                    collection = TextCollection(
                        name=theme,
                        theme=theme,
                        texts=texts,
                        keywords=keywords
                    )
                    
                    self.collections[theme] = collection
                    logger.info(f"Loaded {len(texts)} texts for theme '{theme}'")
                else:
                    logger.warning(f"No valid texts found in {text_file}")
                    
            except Exception as e:
                logger.error(f"Failed to load text collection {text_file}: {e}")
    
    def _extract_keywords(self, theme: str, texts: List[str]) -> List[str]:
        """Extract keywords from theme and text content."""
        keywords = [theme]
        
        # Add words from theme name
        keywords.extend(theme.replace('_', ' ').split())
        
        # Simple keyword extraction from texts
        common_mystical_words = {
            'cosmic', 'spiritual', 'wisdom', 'energy', 'ancient', 'sacred',
            'mystical', 'divine', 'ethereal', 'celestial', 'universal',
            'infinite', 'eternal', 'transcendent', 'enlightened'
        }
        
        for text in texts[:3]:  # Sample first few texts
            words = set(word.lower().strip('.,!?;:"()') for word in text.split())
            keywords.extend(words.intersection(common_mystical_words))
        
        return list(set(keywords))  # Remove duplicates
    
    async def _load_rfid_mappings(self):
        """Load RFID code to theme mappings."""
        mappings_file = Path(self.config.rfid_mappings_file)
        
        if mappings_file.exists():
            try:
                with open(mappings_file, 'r') as f:
                    self.rfid_mappings = json.load(f)
                logger.info(f"Loaded {len(self.rfid_mappings)} RFID mappings")
            except Exception as e:
                logger.error(f"Failed to load RFID mappings: {e}")
        
        # Create default mappings for sample RFID codes
        if not self.rfid_mappings and self.collections:
            themes = list(self.collections.keys())
            sample_rfids = ["123456789012", "987654321098", "111222333444", "555666777888"]
            
            for i, rfid in enumerate(sample_rfids):
                if i < len(themes):
                    self.rfid_mappings[rfid] = themes[i]
            
            logger.info("Created default RFID mappings for sample cards")
    
    async def _save_index(self):
        """Save text collections index."""
        index_data = {
            "collections": {
                theme: {
                    "name": collection.name,
                    "theme": collection.theme,
                    "text_count": len(collection.texts),
                    "keywords": collection.keywords,
                    "created_at": collection.created_at
                }
                for theme, collection in self.collections.items()
            },
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            logger.debug("Text index saved")
        except Exception as e:
            logger.error(f"Failed to save text index: {e}")
    
    async def _save_rfid_mappings(self):
        """Save RFID mappings to file."""
        try:
            with open(self.config.rfid_mappings_file, 'w') as f:
                json.dump(self.rfid_mappings, f, indent=2)
            logger.debug("RFID mappings saved")
        except Exception as e:
            logger.error(f"Failed to save RFID mappings: {e}")
    
    async def get_inspiration(self, rfid_code: str) -> Optional[str]:
        """Get inspiration text for a specific RFID code."""
        if not self.is_initialized:
            await self.initialize()
        
        # Get theme for this RFID code
        theme = self.rfid_mappings.get(rfid_code, self.config.default_theme)
        
        # If theme doesn't exist, use default or random
        if theme not in self.collections:
            if self.collections:
                theme = random.choice(list(self.collections.keys()))
                logger.info(f"Theme '{theme}' not found for RFID {rfid_code}, using random theme: {theme}")
            else:
                logger.error("No text collections available")
                return None
        
        collection = self.collections[theme]
        
        # Select text from collection
        if self.config.random_selection:
            text = random.choice(collection.texts)
        else:
            # Use RFID code as seed for consistent selection
            seed = int(hashlib.md5(rfid_code.encode()).hexdigest()[:8], 16)
            random.seed(seed)
            text = random.choice(collection.texts)
            random.seed()  # Reset seed
        
        # Truncate if too long
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length] + "..."
        
        logger.info(f"Selected text from theme '{theme}' for RFID {rfid_code}")
        return text
    
    def add_rfid_mapping(self, rfid_code: str, theme: str):
        """Add or update RFID code to theme mapping."""
        if theme in self.collections:
            self.rfid_mappings[rfid_code] = theme
            logger.info(f"Mapped RFID {rfid_code} to theme '{theme}'")
        else:
            logger.warning(f"Theme '{theme}' not found, cannot map RFID {rfid_code}")
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return list(self.collections.keys())
    
    def get_collection_info(self, theme: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific collection."""
        if theme in self.collections:
            collection = self.collections[theme]
            return {
                "name": collection.name,
                "theme": collection.theme,
                "text_count": len(collection.texts),
                "keywords": collection.keywords,
                "created_at": collection.created_at
            }
        return None
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        total_texts = sum(len(collection.texts) for collection in self.collections.values())
        
        return {
            "collections": len(self.collections),
            "total_texts": total_texts,
            "rfid_mappings": len(self.rfid_mappings),
            "themes": list(self.collections.keys()),
            "initialized": self.is_initialized
        }


# Test function
async def test_text_library():
    """Test the text library functionality."""
    config = TextLibraryConfig()
    library = TextLibrary(config)
    
    print("Testing text library...")
    await library.initialize()
    
    print(f"\nLibrary stats: {library.get_library_stats()}")
    print(f"Available themes: {library.get_available_themes()}")
    
    # Test getting inspiration for different RFID codes
    test_codes = ["123456789012", "987654321098", "unknown_code"]
    
    for rfid_code in test_codes:
        print(f"\n--- Testing RFID: {rfid_code} ---")
        inspiration = await library.get_inspiration(rfid_code)
        if inspiration:
            print(f"Inspiration text: {inspiration[:100]}...")
        else:
            print("No inspiration found")
    
    await library.shutdown()
    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test_text_library())
