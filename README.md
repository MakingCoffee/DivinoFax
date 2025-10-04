# 🔮 Divinofax - Your Fortune Awaits! 🔮

A mystical fortune-telling fax machine that reads RFID tags, generates haikus using AI, and prints your destiny on a thermal printer.

## Overview

Divinofax is an interactive fortune-telling system that combines:
- **RFID Reading**: Place any tagged item on the reader
- **AI-Powered Poetry**: Local Llama LLM generates personalized haikus  
- **Thermal Printing**: Beautiful fortune receipts with decorative elements
- **LED Feedback**: Visual status indicators via Raspberry Pi Pico
- **Mystical Text Library**: Curated inspirational content mapped to RFID codes

## Hardware Requirements

### Main System
- **Raspberry Pi 4 Model B (4GB)** - Main processing unit
- **MicroSD Card (32GB+)** - For OS and storage
- **Power Supply (5V/3A)** - Official Pi power adapter recommended

### Peripherals  
- **Raspberry Pi Pico** - Handles RFID and LED control
- **RC522 RFID Reader Module** - Reads NFC/RFID tags
- **Maikrt Micro Thermal Printer (5-9V)** - Prints fortune receipts
- **LED Strip or RGB LEDs** - Status indication lights
- **RFID Tags/Cards** - Objects to trigger fortunes
- **Jumper Wires & Breadboard** - For connections

### Optional
- **Enclosure/Case** - Custom housing for the mystical experience
- **External Speaker** - For sound effects (future enhancement)

## Software Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Raspberry Pi   │    │ Pico Board   │    │ Physical Items  │
│                 │◄──►│              │◄──►│                 │
│ • Main App      │USB │ • RFID Reader│    │ • RFID Tags     │
│ • LLM Engine    │    │ • LED Control│    │ • Cards         │  
│ • Text Library  │    │ • Real-time  │    │ • Objects       │
│ • Thermal Print │    │   Hardware   │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## Installation

### Quick Start (Raspberry Pi)

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd divinofax
   ```

2. **Run the installation script:**
   ```bash
   sudo ./install.sh
   ```

3. **Start the service:**
   ```bash
   divinofax start
   ```

### Manual Installation

If you prefer to install manually or need to customize the setup:

#### 1. System Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    build-essential cmake git curl wget gpio wiringpi spi-tools i2c-tools

# Enable hardware interfaces
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial 0
```

#### 2. Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. LLM Model Download
```bash
# Create models directory
mkdir -p models/

# Download quantized Llama model (~4GB)
wget -O models/llama-2-7b-chat.Q4_0.gguf \
    https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.q4_0.bin
```

#### 4. Hardware Setup
Connect your hardware according to the wiring diagrams in `/docs/wiring/`.

#### 5. Configuration
```bash
# Copy and customize configuration
cp config/divinofax.yaml config/divinofax.local.yaml
nano config/divinofax.local.yaml
```

## Hardware Connections

### Raspberry Pi to Pico
- **USB Connection**: Pi USB → Pico USB (for serial communication)

### Pico Connections
- **RC522 RFID Reader:**
  - VCC → 3.3V
  - GND → GND  
  - SDA → GP1
  - SCK → GP2
  - MOSI → GP3
  - MISO → GP4
  - RST → GP5

- **LED Strip:**
  - VCC → VBUS (5V)
  - GND → GND
  - Data → GP15

### Raspberry Pi Connections  
- **Thermal Printer:**
  - VCC → 5V
  - GND → GND
  - TX → GPIO14 (UART)
  - RX → GPIO15 (UART)

## Usage

### Starting the System
```bash
# Start Divinofax service
divinofax start

# Check status
divinofax status

# View live logs
divinofax logs
```

### Operation Flow
1. **Startup**: System initializes, runs LED sequence, prints welcome banner
2. **Waiting**: Blue LED indicates ready state
3. **RFID Detection**: Place tagged item on reader (LED turns blue)
4. **Processing**: Purple LED while generating haiku (~10-30 seconds)
5. **Printing**: Green LED during thermal printing
6. **Complete**: Returns to waiting state

### Management Commands
```bash
divinofax start      # Start the service
divinofax stop       # Stop the service  
divinofax restart    # Restart the service
divinofax status     # Check service status
divinofax logs       # View live logs
divinofax test       # Run system tests
divinofax config     # Edit configuration
```

## Configuration

The main configuration file is `config/divinofax.yaml`. Key settings:

### System Settings
```yaml
system:
  simulation_mode: false  # Enable for testing without hardware
  debug_mode: false       # Extra logging for development
  log_level: INFO         # DEBUG, INFO, WARNING, ERROR
```

### Hardware Settings
```yaml
pico:
  port: /dev/ttyACM0     # Pico USB serial port
  lights_enabled: true    # Enable LED feedback
  
printer:
  port: /dev/ttyS0       # Thermal printer UART port
  use_decorations: true   # Fancy fortune formatting
  
llm:
  model_path: models/llama-2-7b-chat.Q4_0.gguf
  temperature: 0.8       # Creativity level (0.0-1.0)
```

## Customizing Your Divinofax

### Adding New Text Themes
1. Create a new text file in `data/texts/`:
   ```bash
   # Example: data/texts/ocean_wisdom.txt
   echo "The waves whisper ancient secrets..." > data/texts/ocean_wisdom.txt
   ```

2. Map RFID codes to themes in `data/rfid_mappings.json`:
   ```json
   {
     "123456789012": "ocean_wisdom",
     "987654321098": "mountain_spirits"
   }
   ```

### Custom LED Colors
Edit the Pico configuration:
```yaml
pico:
  reading_light_color: blue
  processing_light_color: purple  
  success_light_color: green
  error_light_color: red
```

### Printer Customization
```yaml
printer:
  fortune_header: "✨ YOUR DESTINY ✨"
  line_width: 32
  use_decorations: true
```

## Pico Firmware

The Pico board runs custom firmware to handle real-time hardware tasks. Key features:

- **JSON Communication Protocol** over USB serial
- **Non-blocking RFID Reading** with debouncing
- **WS2812 LED Control** with smooth transitions  
- **Watchdog Protection** and error recovery

### Pico Commands
```json
{"command": "read_rfid"}
{"command": "set_light", "color": "blue", "brightness": 100}
{"command": "get_status"}
```

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs for errors
divinofax logs

# Test components individually  
divinofax test-manual

# Verify configuration
divinofax config
```

**RFID not reading:**
- Check Pico connection: `ls /dev/ttyACM*`
- Verify RFID wiring to Pico
- Test with: `python3 src/pico_controller.py`

**LLM too slow/memory issues:**
- Try smaller model: `llama-2-7b.Q2_K.gguf`
- Reduce context: `n_ctx: 512`
- Enable simulation: `simulation_mode: true`

**Thermal printer not working:**
- Check UART enabled: `sudo raspi-config`
- Verify wiring and power supply
- Test with: `python3 src/thermal_printer.py`

### Log Locations
- **Service Logs**: `journalctl -u divinofax -f`  
- **Application Logs**: `/opt/divinofax/divinofax.log`
- **Test Outputs**: `thermal_output.txt` (simulation mode)

## Development

### Running in Simulation Mode
```bash
# Edit config to enable simulation
nano config/divinofax.yaml
# Set: simulation_mode: true

# Or override via environment
SIMULATION_MODE=true python3 src/divinofax.py
```

### Testing Individual Components
```bash
cd src/

# Test text library
python3 text_library.py

# Test LLM engine  
python3 llm_engine.py

# Test thermal printer
python3 thermal_printer.py

# Test Pico controller
python3 pico_controller.py
```

### Code Structure
```
src/
├── divinofax.py         # Main application orchestrator
├── config.py            # Configuration management
├── pico_controller.py   # Pico board communication
├── rfid_reader.py       # RFID reading (legacy/fallback)
├── text_library.py     # Text management and indexing
├── llm_engine.py        # Llama LLM integration
└── thermal_printer.py   # Thermal printing with formatting

data/
├── texts/               # Text collections by theme
├── text_index.json      # Text library index
└── rfid_mappings.json   # RFID to theme mappings

config/
└── divinofax.yaml       # Main configuration file
```

## Future Enhancements

- [ ] **Web Interface**: Remote management and monitoring
- [ ] **Voice Output**: Spoken fortunes with TTS
- [ ] **Sound Effects**: Mystical audio feedback
- [ ] **Multiple Languages**: International fortune support
- [ ] **Database Storage**: Historical fortune tracking
- [ ] **API Integration**: Online tarot/astrology services
- [ ] **Mobile App**: Smartphone companion
- [ ] **Custom Enclosure**: 3D printable mystical housing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, issues, or questions:
- **GitHub Issues**: Create an issue in the repository
- **Logs**: Always include relevant log output
- **Configuration**: Share your `divinofax.yaml` (remove sensitive info)

## Acknowledgments

- **Llama 2**: Meta's open-source language model
- **Raspberry Pi Foundation**: For amazing hardware platforms
- **Open Source Community**: For the incredible Python ecosystem

---

*May your fortunes be favorable and your haikus profound!* ✨🔮✨
