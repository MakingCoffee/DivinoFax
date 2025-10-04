"""
Thermal Printer Module for Divinofax
====================================

Handles thermal printing using Maikrt Micro Thermal Printer (5-9V).
Formats and prints haikus with decorative elements for fortune telling.

Hardware Requirements:
- Maikrt Micro Thermal Printer
- Serial/UART connection to Raspberry Pi
- 5-9V power supply

Author: Kathryn Bennett
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

try:
    import serial
    from PIL import Image, ImageDraw, ImageFont
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False
    print("Warning: Thermal printer hardware libraries not available. Running in simulation mode.")

logger = logging.getLogger(__name__)


@dataclass
class ThermalPrinterConfig:
    """Configuration for thermal printer."""
    # Serial connection
    port: str = "/dev/ttyS0"  # Default UART port on Pi
    baudrate: int = 9600
    timeout: float = 3.0
    
    # Printer settings
    heat_time: int = 80        # Heat time for darker printing
    heat_interval: int = 12    # Time between heating cycles
    print_density: int = 15    # Print darkness (0-31)
    
    # Formatting
    line_width: int = 32       # Characters per line
    font_size: str = "normal"  # normal, small, large
    
    # Decorative elements
    use_decorations: bool = True
    fortune_header: str = "🔮 YOUR FORTUNE 🔮"
    divider: str = "═" * 32
    
    # Simulation mode
    simulation_mode: bool = False
    output_file: str = "thermal_output.txt"


class MockThermalPrinter:
    """Mock thermal printer for testing without hardware."""
    
    def __init__(self, config: ThermalPrinterConfig):
        self.config = config
        self.output_file = Path(config.output_file)
        logger.info("Mock thermal printer initialized")
    
    async def print_text(self, text: str, **kwargs):
        """Simulate printing text."""
        await asyncio.sleep(0.5)  # Simulate print time
        
        # Write to file for testing
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(text + "\n\n")
        
        logger.info(f"Mock print: {text[:50]}...")
    
    async def print_line(self, char: str = None, width: int = None):
        """Print a decorative line."""
        if char is None:
            char = "═"
        if width is None:
            width = self.config.line_width
        line = char * width
        await self.print_text(line)
    
    async def feed_lines(self, lines: int = 3):
        """Feed paper forward."""
        await asyncio.sleep(0.2)
        logger.debug(f"Mock feed: {lines} lines")
    
    def cleanup(self):
        """Cleanup mock printer."""
        pass


class RealThermalPrinter:
    """Real thermal printer using serial connection."""
    
    # ESC/POS commands for thermal printer
    ESC = b'\\x1b'
    GS = b'\\x1d'
    
    def __init__(self, config: ThermalPrinterConfig):
        self.config = config
        self.serial_conn = None
        self.is_connected = False
    
    def connect(self):
        """Connect to thermal printer via serial."""
        try:
            self.serial_conn = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            # Initialize printer settings
            self._initialize_printer()
            
            self.is_connected = True
            logger.info(f"Connected to thermal printer on {self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to thermal printer: {e}")
            raise
    
    def _initialize_printer(self):
        """Initialize printer with optimal settings."""
        if not self.serial_conn:
            return
        
        try:
            # Reset printer
            self.serial_conn.write(self.ESC + b'@')
            time.sleep(0.1)
            
            # Set print density and heat settings
            self.serial_conn.write(self.ESC + b'7')  # Heating dots
            self.serial_conn.write(bytes([self.config.heat_time]))
            self.serial_conn.write(bytes([self.config.heat_interval]))
            
            # Set print density
            self.serial_conn.write(self.GS + b'(K')
            self.serial_conn.write(b'\\x02\\x00')
            self.serial_conn.write(bytes([self.config.print_density]))
            self.serial_conn.write(b'\\x00')
            
            logger.info("Thermal printer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize printer: {e}")
    
    async def print_text(self, text: str, center: bool = False, bold: bool = False, 
                        large: bool = False, underline: bool = False):
        """Print text with formatting options."""
        if not self.is_connected:
            return
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._blocking_print, text, center, bold, large, underline)
            
        except Exception as e:
            logger.error(f"Error printing text: {e}")
    
    def _blocking_print(self, text: str, center: bool, bold: bool, large: bool, underline: bool):
        """Blocking print operation."""
        if not self.serial_conn:
            return
        
        try:
            # Set formatting
            if center:
                self.serial_conn.write(self.ESC + b'a\\x01')  # Center align
            else:
                self.serial_conn.write(self.ESC + b'a\\x00')  # Left align
            
            if bold:
                self.serial_conn.write(self.ESC + b'E\\x01')  # Bold on
            
            if large:
                self.serial_conn.write(self.GS + b'!\\x11')  # Double size
            else:
                self.serial_conn.write(self.GS + b'!\\x00')  # Normal size
            
            if underline:
                self.serial_conn.write(self.ESC + b'-\\x01')  # Underline on
            
            # Print text
            self.serial_conn.write(text.encode('utf-8', errors='replace'))
            self.serial_conn.write(b'\\n')
            
            # Reset formatting
            self.serial_conn.write(self.ESC + b'E\\x00')  # Bold off
            self.serial_conn.write(self.ESC + b'-\\x00')  # Underline off
            self.serial_conn.write(self.GS + b'!\\x00')   # Normal size
            self.serial_conn.write(self.ESC + b'a\\x00')  # Left align
            
            # Ensure data is sent
            self.serial_conn.flush()
            
        except Exception as e:
            logger.error(f"Blocking print error: {e}")
    
    async def print_line(self, char: str = "=", width: int = None):
        """Print a decorative line."""
        if width is None:
            width = self.config.line_width
        
        line = char * width
        await self.print_text(line, center=True)
    
    async def feed_lines(self, lines: int = 3):
        """Feed paper forward."""
        if not self.is_connected:
            return
        
        try:
            for _ in range(lines):
                self.serial_conn.write(b'\\n')
            self.serial_conn.flush()
            
            # Wait for mechanical movement
            await asyncio.sleep(lines * 0.1)
            
        except Exception as e:
            logger.error(f"Error feeding paper: {e}")
    
    def cleanup(self):
        """Cleanup serial connection."""
        if self.serial_conn and self.is_connected:
            try:
                # Reset printer before closing
                self.serial_conn.write(self.ESC + b'@')
                self.serial_conn.close()
                self.is_connected = False
                logger.info("Thermal printer disconnected")
            except Exception as e:
                logger.error(f"Error during printer cleanup: {e}")


class ThermalPrinter:
    """Main thermal printer class with formatting and decoration."""
    
    def __init__(self, config: ThermalPrinterConfig):
        self.config = config
        self.is_initialized = False
        self.print_stats = {
            "total_prints": 0,
            "successful_prints": 0,
            "failed_prints": 0
        }
        
        # Choose implementation
        if not HAS_HARDWARE or config.simulation_mode:
            self.printer = MockThermalPrinter(config)
            logger.info("Using mock thermal printer")
        else:
            self.printer = RealThermalPrinter(config)
            logger.info("Using real thermal printer")
    
    async def initialize(self):
        """Initialize the thermal printer."""
        if not self.is_initialized:
            logger.info("Initializing thermal printer...")
            
            try:
                if hasattr(self.printer, 'connect'):
                    # Connect to real printer
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.printer.connect)
                
                self.is_initialized = True
                logger.info("Thermal printer initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize thermal printer: {e}")
                # Fallback to mock printer
                if not isinstance(self.printer, MockThermalPrinter):
                    logger.info("Falling back to mock printer")
                    self.printer = MockThermalPrinter(self.config)
                    self.is_initialized = True
    
    async def shutdown(self):
        """Shutdown the thermal printer."""
        if self.is_initialized:
            logger.info("Shutting down thermal printer...")
            self.printer.cleanup()
            self.is_initialized = False
            logger.info("Thermal printer shutdown complete")
    
    async def print_message(self, message: str):
        """Print a simple message."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.print_stats["total_prints"] += 1
            
            await self.printer.print_text(message, center=True)
            await self.printer.feed_lines(2)
            
            self.print_stats["successful_prints"] += 1
            logger.info(f"Message printed: {message[:30]}...")
            
        except Exception as e:
            logger.error(f"Failed to print message: {e}")
            self.print_stats["failed_prints"] += 1
    
    async def print_fortune(self, haiku: str, rfid_code: str = ""):
        """Print a formatted fortune with haiku."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.print_stats["total_prints"] += 1
            
            # Print header
            if self.config.use_decorations:
                await self.printer.print_line("═", self.config.line_width)
                await self.printer.print_text(self.config.fortune_header, center=True, bold=True)
                await self.printer.print_line("═", self.config.line_width)
                await self.printer.feed_lines(1)
            
            # Print timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            await self.printer.print_text(f"Divined: {timestamp}", center=True)
            
            if rfid_code:
                await self.printer.print_text(f"Token: {rfid_code[-6:]}", center=True)  # Last 6 digits
            
            await self.printer.feed_lines(2)
            
            # Print haiku with special formatting
            haiku_lines = haiku.split('\\n')
            for i, line in enumerate(haiku_lines):
                line = line.strip()
                if line:
                    # Center each line of the haiku
                    await self.printer.print_text(line, center=True, bold=(i == 1))  # Middle line bold
                    await asyncio.sleep(0.2)  # Small delay between lines
            
            await self.printer.feed_lines(2)
            
            # Print footer
            if self.config.use_decorations:
                await self.printer.print_text("✨ Trust in the journey ✨", center=True)
                await self.printer.print_line("─", self.config.line_width)
                await self.printer.print_text("DIVINOFAX", center=True, bold=True)
                await self.printer.print_line("═", self.config.line_width)
            
            # Final paper feed
            await self.printer.feed_lines(4)
            
            self.print_stats["successful_prints"] += 1
            logger.info(f"Fortune printed successfully for RFID {rfid_code}")
            
        except Exception as e:
            logger.error(f"Failed to print fortune: {e}")
            self.print_stats["failed_prints"] += 1
            raise
    
    async def print_oracle_fortune(self, fortune_data: dict, rfid_code: str = ""):
        """Print a formatted oracle card fortune with title, description, and haiku."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.print_stats["total_prints"] += 1
            
            # Print header
            if self.config.use_decorations:
                await self.printer.print_line("═", self.config.line_width)
                await self.printer.print_text("🔮 ORACLE FORTUNE 🔮", center=True, bold=True, large=True)
                await self.printer.print_line("═", self.config.line_width)
                await self.printer.feed_lines(1)
            
            # Print oracle card title
            await self.printer.print_text(fortune_data['title'].upper(), center=True, bold=True)
            await self.printer.feed_lines(1)
            
            # Print description with proper text wrapping
            description = fortune_data['description']
            # Simple word wrap for thermal printer
            words = description.split()
            lines = []
            current_line = []
            current_length = 0
            max_length = self.config.line_width - 2  # Leave margin
            
            for word in words:
                if current_length + len(word) + 1 <= max_length:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                await self.printer.print_text(line, center=True)
            
            await self.printer.feed_lines(2)
            
            # Print decorative separator
            await self.printer.print_line("~", self.config.line_width)
            await self.printer.feed_lines(1)
            
            # Print haiku with special formatting
            haiku_lines = fortune_data['haiku'].split('\n')
            for i, line in enumerate(haiku_lines):
                line = line.strip()
                if line:
                    # Center each line of the haiku
                    await self.printer.print_text(line, center=True, bold=(i == 1))  # Middle line bold
                    await asyncio.sleep(0.2)  # Small delay between lines
            
            await self.printer.feed_lines(2)
            await self.printer.print_line("~", self.config.line_width)
            
            # Print keywords if available
            if fortune_data['keywords']:
                await self.printer.feed_lines(1)
                keywords_text = f"Keywords: {fortune_data['keywords']}"
                await self.printer.print_text(keywords_text, center=True)
            
            await self.printer.feed_lines(1)
            
            # Print timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            await self.printer.print_text(f"Divined: {timestamp}", center=True)
            
            if rfid_code:
                # Show a readable form of the RFID for tel: URIs
                display_code = rfid_code if len(rfid_code) <= 8 else rfid_code[-8:]
                await self.printer.print_text(f"Card: {display_code}", center=True)
            
            await self.printer.feed_lines(1)
            
            # Print footer
            if self.config.use_decorations:
                await self.printer.print_text("✨ Trust in the journey ✨", center=True)
                await self.printer.print_line("─", self.config.line_width)
                await self.printer.print_text("DIVINOFAX ORACLE", center=True, bold=True)
                await self.printer.print_line("═", self.config.line_width)
            
            # Final paper feed
            await self.printer.feed_lines(4)
            
            self.print_stats["successful_prints"] += 1
            logger.info(f"Oracle fortune '{fortune_data['title']}' printed successfully for RFID {rfid_code}")
            
        except Exception as e:
            logger.error(f"Failed to print oracle fortune: {e}")
            self.print_stats["failed_prints"] += 1
            raise
    
    async def print_startup_banner(self):
        """Print startup banner when system starts."""
        if not self.is_initialized:
            await self.initialize()
        
        banner = f"""
{self.config.divider}
    🔮 DIVINOFAX ONLINE 🔮
{self.config.divider}

    The cosmic energies
    are aligned and ready
    to reveal your fate

    Place your sacred item
    upon the reader to
    receive your fortune

{self.config.divider}
        """
        
        try:
            for line in banner.strip().split('\\n'):
                if line.strip():
                    await self.printer.print_text(line.strip(), center=True)
                else:
                    await self.printer.feed_lines(1)
            
            await self.printer.feed_lines(3)
            logger.info("Startup banner printed")
            
        except Exception as e:
            logger.error(f"Failed to print startup banner: {e}")
    
    async def print_error_message(self, error_msg: str = None):
        """Print error message."""
        if not error_msg:
            error_msg = "The cosmic energies\\nare disrupted.\\nPlease try again."
        
        try:
            await self.printer.print_line("~", self.config.line_width)
            await self.printer.print_text("⚠️  DIVINATION ERROR  ⚠️", center=True, bold=True)
            await self.printer.print_line("~", self.config.line_width)
            await self.printer.feed_lines(1)
            
            for line in error_msg.split('\\n'):
                if line.strip():
                    await self.printer.print_text(line.strip(), center=True)
            
            await self.printer.feed_lines(1)
            await self.printer.print_text("The spirits will return...", center=True)
            await self.printer.print_line("~", self.config.line_width)
            await self.printer.feed_lines(3)
            
            logger.info("Error message printed")
            
        except Exception as e:
            logger.error(f"Failed to print error message: {e}")
    
    def _wrap_text(self, text: str, width: int = None) -> List[str]:
        """Wrap text to fit printer width."""
        if width is None:
            width = self.config.line_width
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def get_stats(self) -> Dict[str, Any]:
        """Get printer statistics."""
        return {
            "initialized": self.is_initialized,
            "using_mock": isinstance(self.printer, MockThermalPrinter),
            "connected": getattr(self.printer, 'is_connected', False),
            **self.print_stats
        }


# Test function
async def test_thermal_printer():
    """Test the thermal printer functionality."""
    config = ThermalPrinterConfig(simulation_mode=True)
    printer = ThermalPrinter(config)
    
    print("Testing thermal printer...")
    print(f"Initial stats: {printer.get_stats()}")
    
    await printer.initialize()
    
    # Test different print functions
    print("\\n--- Testing startup banner ---")
    await printer.print_startup_banner()
    
    print("\\n--- Testing fortune printing ---")
    test_haiku = "Stars whisper secrets\\nCosmic winds carry your dreams\\nDestiny awaits"
    await printer.print_fortune(test_haiku, "123456789012")
    
    print("\\n--- Testing error message ---")
    await printer.print_error_message("Test error message\\nfor debugging")
    
    print(f"\\nFinal stats: {printer.get_stats()}")
    await printer.shutdown()
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_thermal_printer())
