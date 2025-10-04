"""
RFID Reader Module for Divinofax
================================

Handles RFID chip reading using RC522 module on Raspberry Pi.
Supports both blocking and async reading modes.

Hardware Setup:
- RC522 RFID Reader connected via SPI
- Standard pinout for Raspberry Pi

Author: Kathryn Bennett
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import spidev
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
    HAS_HARDWARE = True
except ImportError:
    # For development/testing on non-Pi systems
    HAS_HARDWARE = False
    print("Warning: RFID hardware libraries not available. Running in simulation mode.")

logger = logging.getLogger(__name__)


@dataclass
class RFIDConfig:
    """Configuration for RFID reader."""
    # GPIO pins for RC522
    reset_pin: int = 22
    
    # Reading behavior
    read_timeout: float = 1.0  # Seconds to wait for a card
    debounce_time: float = 2.0  # Seconds to wait before reading same card again
    retry_count: int = 3
    
    # Simulation mode settings (for testing without hardware)
    simulation_mode: bool = False
    simulation_cards: list = None


class MockRFIDReader:
    """Mock RFID reader for testing without hardware."""
    
    def __init__(self, config: RFIDConfig):
        self.config = config
        self.simulation_cards = config.simulation_cards or [
            "123456789012",  # Fortune cards
            "987654321098",
            "111222333444",
            "555666777888"
        ]
        self.current_card_index = 0
        logger.info("Mock RFID reader initialized")
    
    async def read(self) -> Optional[str]:
        """Simulate reading an RFID card."""
        # Wait a bit to simulate reading time
        await asyncio.sleep(0.5)
        
        # Randomly return a card or None
        import random
        if random.random() > 0.7:  # 30% chance of reading a card
            card = self.simulation_cards[self.current_card_index]
            self.current_card_index = (self.current_card_index + 1) % len(self.simulation_cards)
            logger.info(f"Mock RFID read: {card}")
            return card
        
        return None
    
    def cleanup(self):
        """Cleanup mock reader."""
        pass


class RealRFIDReader:
    """Real RFID reader using RC522 hardware."""
    
    def __init__(self, config: RFIDConfig):
        self.config = config
        self.reader = None
        self.setup_gpio()
        logger.info("Real RFID reader initialized")
    
    def setup_gpio(self):
        """Setup GPIO pins for RC522."""
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.config.reset_pin, GPIO.OUT)
            GPIO.output(self.config.reset_pin, GPIO.HIGH)
            
            # Initialize the MFRC522 reader
            self.reader = SimpleMFRC522()
            logger.info("RC522 RFID reader setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup RFID reader: {e}")
            raise
    
    async def read(self) -> Optional[str]:
        """Read an RFID card with timeout."""
        try:
            # Run the blocking read in a thread pool
            loop = asyncio.get_event_loop()
            
            # Use asyncio.wait_for to add timeout
            try:
                id_val, text = await asyncio.wait_for(
                    loop.run_in_executor(None, self._blocking_read),
                    timeout=self.config.read_timeout
                )
                
                if id_val:
                    rfid_code = str(id_val)
                    logger.info(f"RFID card read: {rfid_code}")
                    return rfid_code
                    
            except asyncio.TimeoutError:
                # No card detected within timeout
                pass
            except Exception as e:
                logger.error(f"Error reading RFID: {e}")
                
        except Exception as e:
            logger.error(f"RFID read error: {e}")
            
        return None
    
    def _blocking_read(self):
        """Blocking RFID read operation."""
        try:
            return self.reader.read_no_block()
        except Exception as e:
            logger.error(f"Blocking read error: {e}")
            return None, None
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        try:
            GPIO.cleanup()
            logger.info("RFID GPIO cleanup complete")
        except Exception as e:
            logger.error(f"GPIO cleanup error: {e}")


class RFIDReader:
    """Main RFID reader class with debouncing and async support."""
    
    def __init__(self, config: RFIDConfig):
        self.config = config
        self.last_read_time = {}  # Track last read time per card for debouncing
        self.is_initialized = False
        
        # Choose implementation based on hardware availability and config
        if not HAS_HARDWARE or config.simulation_mode:
            self.reader = MockRFIDReader(config)
        else:
            self.reader = RealRFIDReader(config)
        
        logger.info(f"RFID reader created ({'mock' if not HAS_HARDWARE or config.simulation_mode else 'real'})")
    
    async def initialize(self):
        """Initialize the RFID reader."""
        if not self.is_initialized:
            logger.info("Initializing RFID reader...")
            # Any additional initialization can go here
            self.is_initialized = True
            logger.info("RFID reader initialized successfully")
    
    async def shutdown(self):
        """Shutdown the RFID reader."""
        if self.is_initialized:
            logger.info("Shutting down RFID reader...")
            self.reader.cleanup()
            self.is_initialized = False
            logger.info("RFID reader shutdown complete")
    
    def _should_process_card(self, rfid_code: str) -> bool:
        """Check if enough time has passed since last read of this card."""
        now = datetime.now()
        
        if rfid_code in self.last_read_time:
            time_since_last = now - self.last_read_time[rfid_code]
            if time_since_last.total_seconds() < self.config.debounce_time:
                return False
        
        self.last_read_time[rfid_code] = now
        return True
    
    async def read_next(self) -> Optional[str]:
        """Read the next RFID card with debouncing."""
        if not self.is_initialized:
            await self.initialize()
        
        for attempt in range(self.config.retry_count):
            try:
                rfid_code = await self.reader.read()
                
                if rfid_code and self._should_process_card(rfid_code):
                    logger.info(f"New RFID reading accepted: {rfid_code}")
                    return rfid_code
                elif rfid_code:
                    logger.debug(f"RFID reading debounced: {rfid_code}")
                
            except Exception as e:
                logger.error(f"RFID read attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(0.1)  # Brief delay before retry
        
        return None
    
    async def wait_for_card(self, timeout: float = None) -> Optional[str]:
        """Wait for a card to be presented, with optional timeout."""
        start_time = time.time()
        
        while True:
            rfid_code = await self.read_next()
            if rfid_code:
                return rfid_code
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                logger.debug(f"Card wait timeout after {timeout} seconds")
                return None
            
            # Brief sleep to prevent busy waiting
            await asyncio.sleep(0.1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get reader status information."""
        return {
            "initialized": self.is_initialized,
            "hardware_available": HAS_HARDWARE,
            "simulation_mode": self.config.simulation_mode,
            "debounce_time": self.config.debounce_time,
            "cards_read_recently": len(self.last_read_time)
        }


# Test function for development
async def test_rfid_reader():
    """Test the RFID reader functionality."""
    config = RFIDConfig(simulation_mode=True)
    reader = RFIDReader(config)
    
    print("Testing RFID reader...")
    print(f"Status: {reader.get_status()}")
    
    # Test reading cards
    for i in range(5):
        print(f"\nRead attempt {i + 1}:")
        rfid_code = await reader.read_next()
        if rfid_code:
            print(f"Card detected: {rfid_code}")
        else:
            print("No card detected")
        
        await asyncio.sleep(1)
    
    await reader.shutdown()
    print("Test complete!")


if __name__ == "__main__":
    # Run the test if this module is executed directly
    asyncio.run(test_rfid_reader())
