"""
Configuration Module for Divinofax
==================================

Centralized configuration management for all Divinofax components.
Supports YAML configuration files with validation and defaults.

Author: Kathryn Bennett
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("Warning: PyYAML not available, using JSON fallback for config")

from rfid_reader import RFIDConfig
from text_library import TextLibraryConfig
from llm_engine import LlamaConfig
from thermal_printer import ThermalPrinterConfig

logger = logging.getLogger(__name__)


@dataclass
class PicoConfig:
    """Configuration for Raspberry Pi Pico board communication."""
    # Serial connection to Pico
    port: str = "/dev/ttyACM0"  # USB serial port for Pico
    baudrate: int = 115200
    timeout: float = 2.0
    
    # Communication protocol
    command_timeout: float = 5.0
    heartbeat_interval: float = 10.0
    retry_count: int = 3
    
    # RFID settings (handled by Pico)
    rfid_enabled: bool = True
    rfid_read_interval: float = 0.5  # How often to check for cards
    
    # LED/Light settings
    lights_enabled: bool = True
    startup_light_sequence: bool = True
    reading_light_color: str = "blue"     # Light when reading RFID
    processing_light_color: str = "purple"  # Light when generating haiku
    success_light_color: str = "green"    # Light when printing
    error_light_color: str = "red"       # Light on error
    
    # Simulation mode for development
    simulation_mode: bool = False


@dataclass
class SystemConfig:
    """General system configuration."""
    # Logging
    log_level: str = "INFO"
    log_file: str = "divinofax.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    
    # Performance
    startup_timeout: float = 30.0
    shutdown_timeout: float = 10.0
    
    # Development
    debug_mode: bool = False
    simulation_mode: bool = False  # Global simulation override
    
    # Data persistence
    save_rfid_history: bool = True
    max_history_entries: int = 1000


@dataclass
class DivinofaxConfig:
    """Main configuration class containing all component configurations."""
    
    # Component configurations
    system: SystemConfig = field(default_factory=SystemConfig)
    pico: PicoConfig = field(default_factory=PicoConfig)
    rfid: RFIDConfig = field(default_factory=RFIDConfig)
    text_library: TextLibraryConfig = field(default_factory=TextLibraryConfig)
    llm: LlamaConfig = field(default_factory=LlamaConfig)
    printer: ThermalPrinterConfig = field(default_factory=ThermalPrinterConfig)
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or defaults."""
        # Set defaults first
        self.system = SystemConfig()
        self.pico = PicoConfig()
        self.rfid = RFIDConfig()
        self.text_library = TextLibraryConfig()
        self.llm = LlamaConfig()
        self.printer = ThermalPrinterConfig()
        
        # Load from file if provided
        if config_path:
            self.load_from_file(config_path)
        
        # Apply global simulation mode if set
        if self.system.simulation_mode:
            self._enable_simulation_mode()
    
    def load_from_file(self, config_path: str):
        """Load configuration from YAML or JSON file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return
        
        try:
            with open(config_file, 'r') as f:
                if HAS_YAML and config_path.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self._update_from_dict(config_data)
            logger.info(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
    
    def save_to_file(self, config_path: str):
        """Save current configuration to file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = self._to_dict()
        
        try:
            with open(config_file, 'w') as f:
                if HAS_YAML and config_path.endswith(('.yaml', '.yml')):
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary."""
        
        # Update system config
        if 'system' in config_data:
            self._update_dataclass(self.system, config_data['system'])
        
        # Update pico config
        if 'pico' in config_data:
            self._update_dataclass(self.pico, config_data['pico'])
        
        # Update RFID config
        if 'rfid' in config_data:
            self._update_dataclass(self.rfid, config_data['rfid'])
        
        # Update text library config
        if 'text_library' in config_data:
            self._update_dataclass(self.text_library, config_data['text_library'])
        
        # Update LLM config
        if 'llm' in config_data:
            self._update_dataclass(self.llm, config_data['llm'])
        
        # Update printer config
        if 'printer' in config_data:
            self._update_dataclass(self.printer, config_data['printer'])
    
    def _update_dataclass(self, obj, data: Dict[str, Any]):
        """Update dataclass fields from dictionary."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'system': self._dataclass_to_dict(self.system),
            'pico': self._dataclass_to_dict(self.pico),
            'rfid': self._dataclass_to_dict(self.rfid),
            'text_library': self._dataclass_to_dict(self.text_library),
            'llm': self._dataclass_to_dict(self.llm),
            'printer': self._dataclass_to_dict(self.printer)
        }
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        result = {}
        for field_name in obj.__dataclass_fields__:
            result[field_name] = getattr(obj, field_name)
        return result
    
    def _enable_simulation_mode(self):
        """Enable simulation mode for all components."""
        self.pico.simulation_mode = True
        self.rfid.simulation_mode = True
        self.llm.simulation_mode = True
        self.printer.simulation_mode = True
        logger.info("Global simulation mode enabled")
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        # Validate system config
        if self.system.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append(f"Invalid log level: {self.system.log_level}")
        
        # Validate pico config
        if self.pico.baudrate not in [9600, 19200, 38400, 57600, 115200]:
            errors.append(f"Invalid Pico baudrate: {self.pico.baudrate}")
        
        # Validate LLM config
        if not self.llm.simulation_mode:
            model_path = Path(self.llm.model_path)
            if not model_path.exists():
                backup_path = Path(self.llm.backup_model_path) if self.llm.backup_model_path else None
                if not backup_path or not backup_path.exists():
                    errors.append(f"LLM model file not found: {self.llm.model_path}")
        
        # Validate printer config
        if self.printer.line_width < 16 or self.printer.line_width > 48:
            errors.append(f"Invalid printer line width: {self.printer.line_width}")
        
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging/debugging."""
        return {
            'system': {
                'debug_mode': self.system.debug_mode,
                'simulation_mode': self.system.simulation_mode,
                'log_level': self.system.log_level
            },
            'pico': {
                'port': self.pico.port,
                'simulation_mode': self.pico.simulation_mode,
                'lights_enabled': self.pico.lights_enabled
            },
            'components_simulation': {
                'rfid': self.rfid.simulation_mode,
                'llm': self.llm.simulation_mode,
                'printer': self.printer.simulation_mode
            }
        }


def create_default_config_file(config_path: str = "config/divinofax.yaml"):
    """Create a default configuration file with documentation."""
    config = DivinofaxConfig()
    
    # Add some example customizations
    config.system.debug_mode = False
    config.pico.lights_enabled = True
    config.printer.use_decorations = True
    
    config.save_to_file(config_path)
    
    # Add comments if YAML
    if HAS_YAML and config_path.endswith(('.yaml', '.yml')):
        _add_yaml_comments(config_path)
    
    logger.info(f"Default configuration file created: {config_path}")


def _add_yaml_comments(config_path: str):
    """Add helpful comments to YAML configuration file."""
    comments = """# Divinofax Configuration File
# =============================
# 
# This file configures all aspects of the Divinofax fortune-telling system.
# Modify these settings to customize your installation.

"""
    
    try:
        # Read existing file
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Add comments at the top
        with open(config_path, 'w') as f:
            f.write(comments + content)
            
    except Exception as e:
        logger.error(f"Failed to add YAML comments: {e}")


# Test function
def test_config():
    """Test configuration loading and saving."""
    print("Testing configuration system...")
    
    # Create default config
    config = DivinofaxConfig()
    print(f"Default config summary: {config.get_summary()}")
    
    # Test validation
    is_valid = config.validate()
    print(f"Configuration valid: {is_valid}")
    
    # Test saving and loading
    test_config_path = "test_config.yaml"
    config.save_to_file(test_config_path)
    
    # Load it back
    config2 = DivinofaxConfig(test_config_path)
    print(f"Loaded config summary: {config2.get_summary()}")
    
    # Cleanup
    Path(test_config_path).unlink(missing_ok=True)
    print("Configuration test complete!")


if __name__ == "__main__":
    test_config()
