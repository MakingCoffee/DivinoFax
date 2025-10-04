"""
Pico Controller Module for Divinofax
====================================

Handles communication with Raspberry Pi Pico board that manages:
- RFID reader hardware
- LED/lighting effects  
- Real-time hardware interactions

Communication Protocol:
- Serial communication over USB
- JSON-based command/response protocol
- Async/await support with proper error handling

Author: Kathryn Bennett
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    print("Warning: pyserial not available. Pico controller running in simulation mode.")

from config import PicoConfig

logger = logging.getLogger(__name__)


@dataclass
class PicoStatus:
    """Status information from Pico board."""
    connected: bool = False
    firmware_version: str = ""
    uptime: float = 0.0
    rfid_enabled: bool = False
    lights_enabled: bool = False
    last_heartbeat: float = 0.0
    error_count: int = 0


class MockPicoController:
    """Mock Pico controller for testing without hardware."""
    
    def __init__(self, config: PicoConfig):
        self.config = config
        self.status = PicoStatus(connected=True, firmware_version="1.0.0-mock")
        self.rfid_callback = None
        self.simulation_rfids = ["123456789012", "987654321098", "111222333444", "555666777888"]
        self.current_rfid_index = 0
        self.light_state = {"color": "off", "brightness": 0}
        logger.info("Mock Pico controller initialized")
    
    async def connect(self) -> bool:
        """Simulate connection to Pico."""
        await asyncio.sleep(0.5)
        self.status.connected = True
        logger.info("Mock Pico connected")
        return True
    
    async def disconnect(self):
        """Simulate disconnection."""
        self.status.connected = False
        logger.info("Mock Pico disconnected")
    
    async def send_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Simulate command execution."""
        await asyncio.sleep(0.1)  # Simulate network latency
        
        if command == "get_status":
            return {
                "status": "ok",
                "data": {
                    "firmware_version": self.status.firmware_version,
                    "uptime": time.time() - 1000,  # Mock uptime
                    "rfid_enabled": True,
                    "lights_enabled": True
                }
            }
        
        elif command == "set_light":
            color = kwargs.get("color", "off")
            brightness = kwargs.get("brightness", 100)
            self.light_state = {"color": color, "brightness": brightness}
            logger.info(f"Mock light set: {color} at {brightness}%")
            return {"status": "ok"}
        
        elif command == "read_rfid":
            # Simulate occasional RFID reads
            import random
            if random.random() > 0.8:  # 20% chance of reading
                rfid = self.simulation_rfids[self.current_rfid_index]
                self.current_rfid_index = (self.current_rfid_index + 1) % len(self.simulation_rfids)
                return {"status": "ok", "data": {"rfid": rfid}}
            else:
                return {"status": "ok", "data": {"rfid": None}}
        
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    
    async def start_monitoring(self, rfid_callback: Callable[[str], None]):
        """Start monitoring for RFID events."""
        self.rfid_callback = rfid_callback
        logger.info("Mock RFID monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring."""
        self.rfid_callback = None
        logger.info("Mock RFID monitoring stopped")


class RealPicoController:
    """Real Pico controller using serial communication."""
    
    def __init__(self, config: PicoConfig):
        self.config = config
        self.serial_conn = None
        self.status = PicoStatus()
        self.monitoring_task = None
        self.rfid_callback = None
        self._command_lock = asyncio.Lock()
        
    async def connect(self) -> bool:
        """Connect to Pico board via serial."""
        try:
            # Auto-detect Pico if port not specified or doesn't exist
            port = await self._find_pico_port()
            if not port:
                logger.error("No Pico board found")
                return False
            
            # Open serial connection
            loop = asyncio.get_event_loop()
            self.serial_conn = await loop.run_in_executor(
                None, 
                lambda: serial.Serial(
                    port=port,
                    baudrate=self.config.baudrate,
                    timeout=self.config.timeout
                )
            )
            
            # Wait for board to initialize
            await asyncio.sleep(2)
            
            # Test connection with status command
            status_response = await self.send_command("get_status")
            if status_response.get("status") == "ok":
                data = status_response.get("data", {})
                self.status.connected = True
                self.status.firmware_version = data.get("firmware_version", "unknown")
                self.status.rfid_enabled = data.get("rfid_enabled", False)
                self.status.lights_enabled = data.get("lights_enabled", False)
                
                logger.info(f"Connected to Pico on {port} - firmware v{self.status.firmware_version}")
                return True
            else:
                logger.error("Pico connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Pico: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Pico."""
        if self.monitoring_task:
            await self.stop_monitoring()
        
        if self.serial_conn:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.serial_conn.close)
                self.status.connected = False
                logger.info("Pico disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting Pico: {e}")
    
    async def _find_pico_port(self) -> Optional[str]:
        """Auto-detect Pico board port."""
        try:
            # Check configured port first
            if hasattr(self.config, 'port') and self.config.port:
                return self.config.port
            
            # Auto-detect Pico
            ports = serial.tools.list_ports.comports()
            for port in ports:
                # Look for Pico-specific identifiers
                if 'Pico' in port.description or 'Raspberry Pi' in port.description:
                    logger.info(f"Found Pico on {port.device}")
                    return port.device
            
            # Fallback to common USB serial ports
            for port_name in ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/cu.usbmodem*']:
                try:
                    if port_name.endswith('*'):
                        # Handle wildcard ports
                        import glob
                        matches = glob.glob(port_name)
                        if matches:
                            return matches[0]
                    else:
                        return port_name
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Error finding Pico port: {e}")
        
        return None
    
    async def send_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Send command to Pico and wait for response."""
        if not self.serial_conn or not self.status.connected:
            return {"status": "error", "message": "Not connected"}
        
        async with self._command_lock:
            try:
                # Prepare command
                cmd_data = {
                    "command": command,
                    "timestamp": time.time(),
                    **kwargs
                }
                
                cmd_json = json.dumps(cmd_data) + '\\n'
                
                # Send command
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.serial_conn.write, cmd_json.encode())
                
                # Wait for response with timeout
                response = await asyncio.wait_for(
                    self._read_response(),
                    timeout=self.config.command_timeout
                )
                
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"Command timeout: {command}")
                return {"status": "error", "message": "Timeout"}
            except Exception as e:
                logger.error(f"Command error: {e}")
                return {"status": "error", "message": str(e)}
    
    async def _read_response(self) -> Dict[str, Any]:
        """Read response from Pico."""
        loop = asyncio.get_event_loop()
        
        # Read line from serial
        line = await loop.run_in_executor(None, self.serial_conn.readline)
        line = line.decode().strip()
        
        if line:
            try:
                return json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {line}")
                return {"status": "error", "message": "Invalid JSON"}
        
        return {"status": "error", "message": "No response"}
    
    async def start_monitoring(self, rfid_callback: Callable[[str], None]):
        """Start monitoring for RFID events."""
        if self.monitoring_task:
            await self.stop_monitoring()
        
        self.rfid_callback = rfid_callback
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Pico RFID monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        self.rfid_callback = None
        logger.info("Pico monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for RFID events."""
        try:
            while True:
                # Check for RFID
                response = await self.send_command("read_rfid")
                if response.get("status") == "ok":
                    data = response.get("data", {})
                    rfid = data.get("rfid")
                    
                    if rfid and self.rfid_callback:
                        try:
                            await asyncio.get_event_loop().run_in_executor(
                                None, self.rfid_callback, rfid
                            )
                        except Exception as e:
                            logger.error(f"RFID callback error: {e}")
                
                # Wait before next check
                await asyncio.sleep(self.config.rfid_read_interval)
                
        except asyncio.CancelledError:
            logger.debug("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")


class PicoController:
    """Main Pico controller with automatic fallback."""
    
    def __init__(self, config: PicoConfig):
        self.config = config
        self.is_initialized = False
        
        # Choose implementation
        if not HAS_SERIAL or config.simulation_mode:
            self.controller = MockPicoController(config)
            logger.info("Using mock Pico controller")
        else:
            self.controller = RealPicoController(config)
            logger.info("Using real Pico controller")
    
    async def initialize(self) -> bool:
        """Initialize Pico connection."""
        if self.is_initialized:
            return True
        
        logger.info("Initializing Pico controller...")
        
        try:
            success = await self.controller.connect()
            if success:
                self.is_initialized = True
                
                # Run startup light sequence if enabled
                if self.config.lights_enabled and self.config.startup_light_sequence:
                    await self._startup_light_sequence()
                
                logger.info("Pico controller initialized successfully")
                return True
            else:
                # Fallback to mock controller
                if not isinstance(self.controller, MockPicoController):
                    logger.info("Falling back to mock Pico controller")
                    self.controller = MockPicoController(self.config)
                    success = await self.controller.connect()
                    if success:
                        self.is_initialized = True
                        return True
                
                logger.error("Failed to initialize Pico controller")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Pico controller: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown Pico controller."""
        if self.is_initialized:
            logger.info("Shutting down Pico controller...")
            await self.controller.disconnect()
            self.is_initialized = False
            logger.info("Pico controller shutdown complete")
    
    async def set_light(self, color: str, brightness: int = 100):
        """Set LED light color and brightness."""
        if not self.is_initialized or not self.config.lights_enabled:
            return
        
        try:
            response = await self.controller.send_command(
                "set_light", 
                color=color, 
                brightness=brightness
            )
            
            if response.get("status") == "ok":
                logger.debug(f"Light set: {color} at {brightness}%")
            else:
                logger.warning(f"Failed to set light: {response.get('message')}")
                
        except Exception as e:
            logger.error(f"Error setting light: {e}")
    
    async def start_rfid_monitoring(self, callback: Callable[[str], None]):
        """Start monitoring for RFID card reads."""
        if not self.is_initialized:
            logger.error("Pico controller not initialized")
            return
        
        try:
            await self.controller.start_monitoring(callback)
            logger.info("RFID monitoring started")
        except Exception as e:
            logger.error(f"Failed to start RFID monitoring: {e}")
    
    async def stop_rfid_monitoring(self):
        """Stop RFID monitoring."""
        try:
            await self.controller.stop_monitoring()
            logger.info("RFID monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping RFID monitoring: {e}")
    
    async def set_status_light(self, status: str):
        """Set light based on system status."""
        if not self.config.lights_enabled:
            return
        
        color_map = {
            "reading": self.config.reading_light_color,
            "processing": self.config.processing_light_color,
            "success": self.config.success_light_color,
            "error": self.config.error_light_color,
            "idle": "dim_blue",
            "off": "off"
        }
        
        color = color_map.get(status, "white")
        await self.set_light(color)
    
    async def _startup_light_sequence(self):
        """Run startup light sequence."""
        try:
            colors = ["red", "yellow", "green", "blue", "purple"]
            
            for color in colors:
                await self.set_light(color, 50)
                await asyncio.sleep(0.3)
            
            # End with idle color
            await self.set_light("dim_blue", 30)
            logger.info("Startup light sequence complete")
            
        except Exception as e:
            logger.error(f"Startup light sequence error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Pico controller status."""
        if hasattr(self.controller, 'status'):
            status = self.controller.status
            return {
                "initialized": self.is_initialized,
                "connected": status.connected,
                "using_mock": isinstance(self.controller, MockPicoController),
                "firmware_version": status.firmware_version,
                "rfid_enabled": status.rfid_enabled,
                "lights_enabled": status.lights_enabled
            }
        else:
            return {
                "initialized": self.is_initialized,
                "connected": False,
                "using_mock": isinstance(self.controller, MockPicoController)
            }


# Test function
async def test_pico_controller():
    """Test Pico controller functionality."""
    from config import PicoConfig
    
    config = PicoConfig(simulation_mode=True)
    controller = PicoController(config)
    
    print("Testing Pico controller...")
    print(f"Initial status: {controller.get_status()}")
    
    # Test initialization
    success = await controller.initialize()
    print(f"Initialization successful: {success}")
    
    if success:
        print(f"Status after init: {controller.get_status()}")
        
        # Test light control
        print("\\nTesting lights...")
        for color in ["red", "green", "blue", "purple"]:
            await controller.set_light(color)
            await asyncio.sleep(0.5)
        
        # Test status lights
        print("\\nTesting status lights...")
        for status in ["reading", "processing", "success", "error", "idle"]:
            await controller.set_status_light(status)
            await asyncio.sleep(0.5)
        
        # Test RFID monitoring
        print("\\nTesting RFID monitoring...")
        
        def rfid_callback(rfid_code):
            print(f"RFID detected: {rfid_code}")
        
        await controller.start_rfid_monitoring(rfid_callback)
        await asyncio.sleep(3)  # Monitor for 3 seconds
        await controller.stop_rfid_monitoring()
    
    await controller.shutdown()
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_pico_controller())
