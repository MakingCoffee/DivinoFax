# 🔮 Divinofax - Your Fortune Awaits! 🔮

A mystical fortune-telling fax machine that reads RFID tags, generates haikus using AI, and prints your destiny on a thermal printer.

## Overview

Divinofax is an interactive fortune-telling system that combines:
- **RFID Reading**: Place any tagged item on the reader
- **AI-Powered Poetry**: Local Llama LLM generates personalized haikus with celestial context
- **Thermal Printing**: Beautiful fortune receipts with card, suit, moon phase, zodiac sign, and poem
- **LED Feedback**: Visual status indicators via Raspberry Pi Pico
- **Mystical Text Library**: Curated inspirational content mapped to RFID codes
- **Celestial Context**: Moon phases and astrological signs influence fortune generation
- **Oracle Deck System**: 75-card Protocol Drift oracle with 5 mystical suits

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
┌─────────────────────────────────────┐
│      Raspberry Pi 4 (Main App)      │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │  RFID Reading Pipeline      │   │
│  │  ├─ RC522 RFID Reader       │   │
│  │  └─ RFIDCardMapper (75 cards│   │
│  └─────────────────────────────┘   │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │  Celestial Context          │   │
│  │  ├─ MoonPhaseCalculator     │   │
│  │  ├─ AstrologyCalculator     │   │
│  │  └─ SuitContext (5 suits)   │   │
│  └─────────────────────────────┘   │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │  LLM Engine (Llama 2 7B)    │   │
│  │  ├─ Enhanced Prompts        │   │
│  │  ├─ Flexible Poem Forms     │   │
│  │  └─ Celestial Injection     │   │
│  └─────────────────────────────┘   │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │  Thermal Printer Output     │   │
│  │  ├─ Card Title & Description│   │
│  │  ├─ Suit with Essence Quote │   │
│  │  ├─ Moon Phase Theme        │   │
│  │  ├─ Zodiac Sign & Element   │   │
│  │  ├─ Generated Poem (2-4 ln) │   │
│  │  └─ Keywords                │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
       ↕ USB                    ↕ UART
       │                         │
    ┌──────────┐          ┌─────────────┐
    │ Pico     │          │ Thermal     │
    │ Board    │          │ Printer     │
    │ • LED    │          │ 32 char/ln  │
    │ • RFID   │          │ 5-9V supply │
    └──────────┘          └─────────────┘
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
- **Thermal Printer (Maikrt Micro USB Thermal Printer):**
  - VCC → 5V power supply
  - GND → GND
  - TX → GPIO14 (UART TX, pins 8)
  - RX → GPIO15 (UART RX, pins 10)

  **Specifications:**
  - Print Width: 32 characters per line
  - Paper: 58mm thermal paper roll
  - Power: 5-9V DC
  - Interface: UART serial (9600 baud)
  - Speed: ~100mm/s
  - Print Density: Configurable (0-31)

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

## The Oracle Card System

### 75-Card Protocol Drift Deck

Divinofax uses the Protocol Drift oracle system with 75 unique cards organized into 5 mystical suits:

**Suit 1: The Signal** (Cards 1-15)
- *Essence*: "Every message is a mirror"
- *Theme*: Transmission, communication, visibility, identity, broadcast
- *Guidance*: Speak your truth, locate yourself in the noise

**Suit 2: The Circuit** (Cards 16-30)
- *Essence*: "Every ache is a message"
- *Theme*: Embodiment, transformation, sensation, body, feeling
- *Guidance*: Feel your truth, let transformation unfold through sensation

**Suit 3: The Archive** (Cards 31-45)
- *Essence*: "Every card is a file left open"
- *Theme*: Memory, lineage, preservation, witness, history
- *Guidance*: Hold what came before, remember, build from erased truths

**Suit 4: The Glitch** (Cards 46-60)
- *Essence*: "Every disruption is a door"
- *Theme*: Interruption, rebellion, error, malfunction, truth
- *Guidance*: Embrace uncertainty, find magic in what's broken

**Suit 5: The Sync** (Cards 61-75)
- *Essence*: "Every heartbeat is a bridge"
- *Theme*: Resonance, alignment, rhythm, harmony, connection
- *Guidance*: Align with the rhythm of becoming, flow with kinship

### RFID Mapping

All 75 cards are mapped to their physical RFID UIDs in `data/rfid_mappings.json`:
```json
{
  "mapping": {
    "04:26:9F:5A:06:1F:91": 1,
    "04:26:A0:5A:06:1F:91": 2,
    ...
    "04:26:65:5A:06:1F:91": 75
  },
  "total_cards": 75
}
```

## Celestial Integration

### Moon Phase Context

The system calculates the current moon phase and injects it into the haiku generation prompt:

```
CELESTIAL TIMING: The seeker draws this card under a {moon_phase} of {moon_theme}.
```

**8 Moon Phases**:
- New Moon: Fresh beginnings
- Waxing Crescent: Growing intentions
- First Quarter: Building momentum
- Waxing Gibbous: Manifestation
- Full Moon: Illumination and culmination
- Waning Gibbous: Release and reflection
- Last Quarter: Completion and wisdom
- Waning Crescent: Rest and renewal

### Astrological Sign Context

The system determines the current zodiac sign and injects it into the haiku generation prompt:

```
ASTROLOGICAL INFLUENCE: {Zodiac_sign} channels {element} wisdom and {thematic_guidance}.
```

**12 Zodiac Signs** with element associations:
- Fire: Aries, Leo, Sagittarius
- Earth: Taurus, Virgo, Capricorn
- Air: Gemini, Libra, Aquarius
- Water: Cancer, Scorpio, Pisces

### How They Influence the Poem

The LLM receives instructions: *"Let the card, the moon, and the stars guide your words."*

This causes the AI to weave celestial themes into the fortune:
- Moon phases suggest emotional timing and cycles
- Zodiac elements suggest the quality of energy (fire=action, earth=grounding, air=thinking, water=feeling)
- Combined with the card's essence, this creates rich, contextual poetry

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
     "04:26:9F:5A:06:1F:91": 1,
     "04:26:A0:5A:06:1F:91": 2
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
  heat_time: 80
  print_density: 15
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

## Output Format

### Thermal Printer Fortune Slip

When an RFID card is read, the printer outputs a beautifully formatted slip:

```
═══════════════════════════════
   🔮 YOUR FORTUNE 🔮
═══════════════════════════════

2026-02-16

   THE SIGNAL (CARD 1)
 Declaration that you exist

   Suit: THE SIGNAL
   ✦ Every message is a mirror

   🌙 FULL MOON
   ✦ Illumination and culmination

   ♈ PISCES (Water)
   ✦ Intuitive wisdom and dreamlike compassion

   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Signals pierce the dark
   Lost voices find their echo
   You are finally heard

   Keywords: transmission, communication,
   visibility, identity, broadcast,
   recognition
═══════════════════════════════
```

**Components:**
- **Card Title**: Name and card number
- **Card Description**: Brief meaning
- **Suit Information**: Suit name + essence quote
- **Moon Phase**: Current phase + thematic guidance
- **Zodiac Sign**: Current sign + element + thematic guidance
- **Generated Poem**: 2-4 line verse (haiku, couplet, tercet, or free verse)
- **Keywords**: Associated concepts for deeper reflection

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
- Verify wiring and power supply (5-9V)
- Check baud rate: `9600`
- Test with: `python3 src/thermal_printer.py`

**Celestial context not appearing in poem:**
- Verify moon_context and astro_context are passed to LLM
- Check LLM prompt includes CELESTIAL TIMING and ASTROLOGICAL INFLUENCE sections
- Ensure MoonPhaseCalculator and AstrologyCalculator are initialized
- Check divinofax.py process_rfid_reading() method passes contexts

### Log Locations
- **Service Logs**: `journalctl -u divinofax -f`
- **Application Logs**: `/opt/divinofax/divinofax.log`
- **Test Outputs**: `thermal_output.txt` (simulation mode)

### Printer Communication
If printer not responding:
```bash
# Check serial connection
stty -F /dev/ttyS0 9600 -a

# Test with simple output
echo -e "Test\n\n\n\n\n" > /dev/ttyS0

# Monitor UART traffic
cat /dev/ttyS0
```

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
├── divinofax.py             # Main application orchestrator
├── config.py                # Configuration management
├── pico_controller.py       # Pico board communication
├── rfid_reader.py           # RFID reading (legacy/fallback)
├── rfid_mapper.py           # RFID UID to card number mapping
├── text_library.py          # Text management and indexing
├── llm_engine.py            # Llama LLM integration (with celestial context)
├── thermal_printer.py       # Thermal printing with rich formatting
├── moon_phase.py            # Moon phase calculation & context
├── astrology.py             # Zodiac sign calculation & context
└── suit_context.py          # Oracle suit information loader

data/
├── texts/                   # Text collections by theme
├── text_index.json          # Text library index
├── rfid_mappings.json       # RFID UID to card number (all 75 cards)
└── suits.json               # Oracle suit definitions with essence quotes

config/
└── divinofax.yaml           # Main configuration file

docs/
├── INTEGRATION_FLOW.md      # Complete celestial integration documentation
└── wiring/                  # Hardware connection diagrams
```

## Recent Enhancements (Latest Release)

### ✨ Celestial Context Integration
- **Moon Phase Injection**: 8-phase lunar calendar influences poem generation
- **Astrological Signs**: 12 zodiac signs with element associations guide the LLM
- **Oracle Deck Expansion**: Complete 75-card Protocol Drift system with rich descriptions
- **Suit System**: 5 mystical suits with essence quotes and thematic guidance
- **Enhanced Thermal Output**: Displays card, suit, moon phase, zodiac, and poem

### 📊 Performance & Validation
- **Processing Speed**: ~7 seconds average (within 10-second budget)
- **Complete Coverage**: All 75 oracle cards mapped to unique RFID UIDs
- **No Constraints**: Pi 4 (4GB) has plenty of resources for enrichment
- **Flexible Poetry**: Supports haiku, couplet, tercet, and free verse forms

### 📝 Technical Details
- Enhanced LLM prompts with layered contextual guidance
- MoonPhaseCalculator with accurate 29.53-day cycle
- AstrologyCalculator with date-based zodiac determination
- RFIDCardMapper for efficient UID-to-card-number lookup
- SuitContext for oracle deck information management

## Future Enhancements

- [ ] **Web Interface**: Remote management and monitoring
- [ ] **Voice Output**: Spoken fortunes with TTS
- [ ] **Sound Effects**: Mystical audio feedback
- [ ] **Multiple Languages**: International fortune support
- [ ] **Database Storage**: Historical fortune tracking
- [ ] **API Integration**: Online tarot/astrology services
- [ ] **Mobile App**: Smartphone companion
- [ ] **Custom Enclosure**: 3D printable mystical housing
- [ ] **Card Image Display**: LED matrix or small screen for visual cards
- [ ] **Advanced Astrology**: Natal chart integration

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
