# 🔮 Divinofax Raspberry Pi Deployment Checklist

## ✅ Ready for Production!

Your Divinofax system is now **fully ready** for deployment on the Raspberry Pi. Here's what you need to do:

## 📋 Pre-Deployment Checklist

### 🔧 Hardware Requirements
- [ ] Raspberry Pi 4 Model B (4GB recommended)
- [ ] RFID reader (RC522 or compatible) connected via SPI
- [ ] Thermal printer (Maikrt Micro 5-9V) connected via UART
- [ ] Your 75 programmed RFID cards with numbers `001` through `075`
- [ ] MicroSD card (32GB+) with fresh Raspberry Pi OS

### 📦 Software Stack  
- [ ] Python 3.9+ installed on Pi
- [ ] Git installed for repository cloning
- [ ] Hardware libraries (included in requirements.txt)

## 🚀 Deployment Steps

### 1. Clone Repository on Pi
```bash
git clone https://github.com/MakingCoffee/DivinoFax.git
cd DivinoFax
```

### 2. Run Installation Script  
```bash
sudo ./install.sh
```
This automatically:
- Creates Python virtual environment
- Installs all dependencies  
- Downloads LLM model (if needed)
- Sets up systemd service
- Configures hardware permissions

### 3. Configure for Production
```bash
# Edit configuration for your hardware setup
sudo nano config/divinofax.yaml

# Key settings to verify:
# - simulation_mode: false
# - UART/SPI port settings
# - Thermal printer configuration
```

### 4. Test Individual Components
```bash
# Test each component before full system
cd src/

# Test oracle card loading
python3 text_library.py

# Test thermal printer (check connections)
python3 thermal_printer.py  

# Test RFID reader (check SPI connections)
python3 rfid_reader.py

# Test LLM generation (may take time to load model)
python3 llm_engine.py
```

### 5. Start Production System
```bash
# Manual start for testing
python3 src/divinofax.py

# Or use the systemd service
sudo systemctl start divinofax
sudo systemctl enable divinofax  # Auto-start on boot
```

## 🔍 Verification Tests

### Oracle Card Schema Test
Place test cards and verify:
- [ ] RFID `001` → **Crystal Sync** card loads correctly
- [ ] RFID `046` → **The Glitch Witch** card loads correctly  
- [ ] RFID `069` → **Vaporwave Oracle** card loads correctly
- [ ] All 75 cards map properly (check logs)

### Thermal Output Test
Verify printed receipts contain:
- [ ] "🔮 ORACLE FORTUNE 🔮" header
- [ ] Card title in uppercase
- [ ] Full card description with proper wrapping
- [ ] Generated haiku (3 lines, centered)
- [ ] Keywords line
- [ ] Timestamp and card number
- [ ] "DIVINOFAX ORACLE" footer

### System Monitoring
```bash
# Monitor system logs
sudo journalctl -u divinofax -f

# Check application logs  
tail -f /opt/divinofax/divinofax.log

# Monitor performance
htop  # Watch memory usage during LLM generation
```

## 🛠️ Hardware Connection Verification

### RFID Reader (RC522)
```bash
# Verify SPI is enabled
sudo raspi-config  # Interface Options → SPI → Enable

# Test SPI detection
lsmod | grep spi
```

### Thermal Printer
```bash
# Verify UART is enabled  
sudo raspi-config  # Interface Options → Serial → Enable

# Check UART device
ls -la /dev/ttyS0   # Should exist and be accessible
```

## 📊 Expected Performance

### Timing Benchmarks
- **RFID Detection**: ~500ms
- **Oracle Card Loading**: ~50ms  
- **Haiku Generation**: 2-10 seconds (depending on model)
- **Thermal Printing**: 15-30 seconds (full receipt)
- **Total Fortune Time**: ~20-45 seconds end-to-end

### Memory Usage
- **Base System**: ~200MB
- **With LLM Loaded**: ~4.5GB (during generation)
- **Peak Usage**: ~5GB (ensure 8GB Pi or swap enabled)

## 🎯 Oracle Card Mapping

Your system now supports:
- ✅ **75 Oracle Cards** (tel:001 through tel:075)
- ✅ **RFID Normalization** (001 → tel:001 automatically)
- ✅ **Complete Card Data** (Title, Description, Keywords)  
- ✅ **Enhanced Thermal Output** (Professional receipt format)
- ✅ **Contextual Haikus** (Generated from card descriptions)

## 🆘 Troubleshooting

### Common Issues
```bash  
# RFID not reading
sudo dmesg | grep spi         # Check SPI detection
python3 src/pico_controller.py  # Test Pico connection

# Thermal printer not working
sudo dmesg | grep tty         # Check UART detection  
echo "test" > /dev/ttyS0      # Direct printer test

# LLM out of memory
# Enable swap or use smaller model in config
sudo dphys-swapfile swapoff
sudo dphys-swapfile swapon
```

### Get System Status
```bash
# Quick system check
divinofax status
divinofax logs
divinofax config
```

## 🎉 You're All Set!

Your Divinofax oracle card fortune-telling machine is ready to bring cyberpunk mysticism to life! Place any of your 75 oracle cards on the reader and watch the magic happen. ✨🔮✨

---

**Happy Fortune Telling!** 🌟

*May your haikus be profound and your thermal paper never run out!*
