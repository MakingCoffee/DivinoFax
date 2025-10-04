# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Divinofax is a mystical fortune-telling fax machine that combines hardware and AI to create an interactive experience. It uses RFID tags to trigger AI-generated haiku fortunes printed on thermal paper, with LED feedback throughout the process.

## Common Development Commands

### Running the System
```bash
# Start the full system (requires hardware or simulation mode)
python3 src/divinofax.py

# Run in simulation mode for development
SIMULATION_MODE=true python3 src/divinofax.py

# Use the management script (after installation)
divinofax start
divinofax logs
divinofax status
```

### Testing Individual Components
```bash
cd src/

# Test each module independently
python3 text_library.py      # Test text loading and theme mapping
python3 llm_engine.py         # Test haiku generation (simulation or real)
python3 thermal_printer.py   # Test printing (outputs to thermal_output.txt in sim mode)
python3 pico_controller.py   # Test hardware communication
python3 rfid_reader.py        # Test RFID reading
python3 config.py             # Test configuration loading
```

### Installation and Setup
```bash
# Clone the repository
git clone https://github.com/MakingCoffee/DivinoFax.git
cd DivinoFax

# Quick setup on Raspberry Pi
sudo ./install.sh

# Manual Python environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration management
cp config/divinofax.yaml config/divinofax.local.yaml
# Edit your local config, then run with: CONFIG_PATH=config/divinofax.local.yaml python3 src/divinofax.py
```

### Model Management
```bash
# Download LLM model for Pi (requires ~4GB)
mkdir -p models/
wget -O models/llama-2-7b-chat.Q4_0.gguf \
    https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.q4_0.bin
```

## High-Level Architecture

### Multi-Layer Hardware Integration
The system operates across three physical layers:
- **Raspberry Pi 4**: Main application, LLM processing, configuration management, thermal printing
- **Raspberry Pi Pico**: Real-time hardware control (RFID reading, LED effects), JSON over USB serial
- **Physical Objects**: RFID-tagged items that users interact with

### Component Communication Flow
```
User places RFID object → Pico reads tag → Pi processes via text library → 
LLM generates haiku → Thermal printer outputs fortune → LED feedback throughout
```

### Key Architectural Decisions

**Async/Await Throughout**: The entire system uses Python's asyncio for non-blocking operations, allowing smooth hardware coordination while LLM generation runs in background threads.

**Simulation Mode Architecture**: Every component has dual implementations (Real/Mock) controlled by configuration flags. This enables development without hardware and testing of complex interaction flows.

**Hardware Abstraction Layer**: The Pico board handles all real-time hardware (RFID, LEDs) and communicates via JSON protocol over USB serial. This keeps the Pi focused on AI processing while ensuring reliable hardware response times.

**Component Isolation**: Each major subsystem (text_library, llm_engine, thermal_printer, pico_controller, rfid_reader) is a self-contained module with its own config class and initialization/shutdown lifecycle.

### Configuration Management
Centralized YAML configuration with dataclass validation. Each component has its own config dataclass that gets populated from the main divinofax.yaml file. The system supports:
- Global simulation mode override
- Per-component simulation toggles  
- Hardware-specific settings (ports, timing, formatting)
- Development vs production profiles

### Text Processing Pipeline
1. **Text Library**: Manages themed text collections (cosmic_wisdom, nature_spirits, etc.) mapped to specific RFID codes
2. **LLM Engine**: Uses local Llama models (quantized for Pi 4) with prompt engineering for haiku generation
3. **Validation**: Generated haikus undergo format validation before printing

### Hardware Integration Patterns
- **Serial Communication**: Both Pico (USB) and thermal printer (UART) use serial with different protocols
- **Error Recovery**: Automatic retry logic, connection monitoring, graceful degradation when hardware fails
- **Timing Coordination**: LED sequences sync with processing stages (blue=reading, purple=thinking, green=printing)

## Development Notes

### Working with Simulation Mode
Set `simulation_mode: true` in config or use environment variable `SIMULATION_MODE=true`. In simulation:
- RFID reader cycles through preset card IDs
- LLM engine returns sample haikus instead of generating
- Thermal printer writes to `thermal_output.txt`
- Pico controller simulates LED states and hardware responses

### Adding New Text Themes
1. Create new `.txt` file in `data/texts/` directory
2. Add RFID mapping in `data/rfid_mappings.json` (format: `{"RFID_CODE": "theme_name"}`)
3. Text library automatically indexes on startup

### LLM Model Considerations
- Quantized models required for Pi 4 memory constraints
- Context window (`n_ctx`) tuned for haiku generation (~1024 tokens)
- Temperature settings balance creativity vs. coherent output
- Backup model path for fallback if primary model fails

### Pico Firmware Protocol
Communication uses JSON commands over serial:
```json
{"command": "read_rfid"}
{"command": "set_light", "color": "blue", "brightness": 100}
{"command": "get_status"}
```

### Error Handling Patterns
- Component-level initialization with graceful failure
- Hardware timeouts and retry logic
- Async exception handling preserves main loop operation
- Comprehensive logging throughout for debugging

### Testing Strategy
Each module has standalone test capability by running directly. The mock implementations enable end-to-end testing without hardware. Integration testing possible through simulation mode with controlled RFID sequence injection.

## Configuration Priority
1. Environment variables (e.g., `SIMULATION_MODE=true`)
2. Local config file (`config/divinofax.local.yaml`)  
3. Default config file (`config/divinofax.yaml`)
4. Component defaults in code

## Troubleshooting Development Issues

### LLM Generation Problems
- Check model file exists and has correct permissions
- Monitor memory usage (`htop` - model loading requires ~4GB)
- Try backup/smaller model if primary fails
- Enable `debug_mode: true` for detailed generation logging

### Hardware Connection Issues
- Use `ls /dev/tty*` to verify ports
- Check `dmesg` for USB device recognition
- Test components individually before running full system
- Pico auto-detection looks for "Raspberry Pi" in device description

### Performance Optimization
- Reduce LLM context size for faster generation
- Adjust thermal printer heat settings for speed vs quality
- Use smaller quantized models for faster response
- Increase debounce times to prevent accidental re-triggers
