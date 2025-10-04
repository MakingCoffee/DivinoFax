#!/usr/bin/env python3
"""
Divinofax - A Fortune-Telling Fax Machine
==========================================

Main application that coordinates RFID reading, text indexing, LLM-powered haiku generation,
and thermal printing on a Raspberry Pi.

Hardware Requirements:
- Raspberry Pi 4 Model B (4GB)
- RFID reader (RC522 or similar)
- Maikrt Micro Thermal Printer (5-9V)

Author: Kathryn Bennett
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional, Dict

from rfid_reader import RFIDReader
from text_library import TextLibrary
from llm_engine import LlamaEngine
from thermal_printer import ThermalPrinter
from config import DivinofaxConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('divinofax.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Divinofax:
    """Main Divinofax application class."""
    
    def __init__(self, config_path: str = "config/divinofax.yaml"):
        """Initialize the Divinofax system."""
        self.config = DivinofaxConfig(config_path)
        self.running = False
        
        # Initialize components
        self.rfid_reader = RFIDReader(self.config.rfid)
        self.text_library = TextLibrary(self.config.text_library)
        self.llm_engine = LlamaEngine(self.config.llm)
        self.thermal_printer = ThermalPrinter(self.config.printer)
        
        logger.info("Divinofax initialized successfully")
    
    async def startup(self):
        """Initialize all system components."""
        logger.info("Starting up Divinofax system...")
        
        try:
            # Initialize components in order
            await self.text_library.initialize()
            await self.llm_engine.initialize()
            await self.thermal_printer.initialize()
            await self.rfid_reader.initialize()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def shutdown(self):
        """Clean shutdown of all components."""
        logger.info("Shutting down Divinofax system...")
        self.running = False
        
        # Shutdown in reverse order
        await self.rfid_reader.shutdown()
        await self.thermal_printer.shutdown()
        await self.llm_engine.shutdown()
        await self.text_library.shutdown()
        
        logger.info("Shutdown complete")
    
    async def process_rfid_reading(self, rfid_code: str) -> Optional[Dict[str, str]]:
        """Process an RFID reading and generate a haiku with card info."""
        logger.info(f"Processing RFID code: {rfid_code}")
        
        try:
            # Get oracle card information
            card_info = await self.text_library.get_oracle_card_info(rfid_code)
            if not card_info:
                logger.warning(f"No oracle card info found for RFID: {rfid_code}")
                return None
            
            # Get inspiration text for haiku generation
            inspiration_text = await self.text_library.get_inspiration(rfid_code)
            if not inspiration_text:
                logger.warning(f"No inspiration text found for RFID: {rfid_code}")
                return None
            
            # Generate haiku using LLM
            haiku = await self.llm_engine.generate_haiku(inspiration_text, rfid_code)
            
            if haiku:
                result = {
                    'haiku': haiku,
                    'title': card_info['title'],
                    'description': card_info['description'],
                    'keywords': card_info['keywords'],
                    'theme': card_info['theme']
                }
                logger.info(f"Generated fortune for {rfid_code}: {card_info['title']}")
                return result
            else:
                logger.error(f"Failed to generate haiku for {rfid_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing RFID {rfid_code}: {e}")
            return None
    
    async def print_fortune(self, fortune_data: Dict[str, str], rfid_code: str):
        """Print the oracle card fortune to thermal printer."""
        try:
            await self.thermal_printer.print_oracle_fortune(fortune_data, rfid_code)
            logger.info(f"Oracle card '{fortune_data['title']}' printed successfully for {rfid_code}")
        except Exception as e:
            logger.error(f"Failed to print fortune for {rfid_code}: {e}")
    
    async def main_loop(self):
        """Main application loop."""
        logger.info("Divinofax is ready and waiting for RFID readings...")
        self.running = True
        
        # Print startup message
        startup_message = "🔮 DIVINOFAX ONLINE 🔮\nPlace your item on the reader\nto receive your fortune..."
        await self.thermal_printer.print_message(startup_message)
        
        while self.running:
            try:
                # Wait for RFID reading
                rfid_code = await self.rfid_reader.read_next()
                
                if rfid_code:
                    logger.info(f"RFID detected: {rfid_code}")
                    
                    # Print "thinking" message
                    await self.thermal_printer.print_message("🌟 Consulting the cosmic energies... 🌟")
                    
                    # Process the reading and generate oracle card fortune
                    fortune_data = await self.process_rfid_reading(rfid_code)
                    
                    if fortune_data:
                        # Print the oracle card fortune
                        await self.print_fortune(fortune_data, rfid_code)
                    else:
                        # Print error message
                        error_msg = "The spirits are unclear today.\nPlease try again later."
                        await self.thermal_printer.print_message(error_msg)
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def run(self):
        """Run the complete Divinofax application."""
        try:
            await self.startup()
            await self.main_loop()
        finally:
            await self.shutdown()


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger.info(f"Received signal {signum}")
    # Set a flag or use asyncio to stop the main loop
    sys.exit(0)


async def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and run Divinofax
        divinofax = Divinofax()
        await divinofax.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🔮 Welcome to Divinofax - Your Fortune Awaits! 🔮")
    asyncio.run(main())
