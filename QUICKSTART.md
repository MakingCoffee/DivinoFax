# 🚀 DivinoFax Quick Start Guide

## SSH Access (No Password Required!)

```bash
ssh divinofax
```

That's it! You're now in your Pi.

---

## Start the System

```bash
# SSH into your Pi
ssh divinofax

# Navigate to project
cd /home/oracle/divinofax

# Start the fortune-telling system
python3 src/divinofax.py
```

The system is now running and waiting for RFID card scans!

---

## Test Individual Components

```bash
# SSH and run tests
ssh divinofax

# Test astrology (check current zodiac)
python3 src/astrology.py

# Test moon phases
python3 src/moon_phase.py

# Test with a sample RFID card (Card 62: Moonbeam Modem)
python3 test_rfid_card.py

# Run complete thermal printer test
python3 test_printer_output.py
```

---

## Deploy New Code

When you make updates locally:

```bash
cd /Users/kathrynbennett/divinofax

# Commit your changes
git add .
git commit -m "Your changes here"
git push origin main

# Sync to Pi (using secure script with password)
bash deploy_to_pi_secure.sh divinofax.local oracle Oracle123!

# Or pull directly on Pi
ssh divinofax "cd /home/oracle/divinofax && git pull origin main"
```

---

## What's Running on Your Pi

✅ **Location**: /home/oracle/divinofax/
✅ **Python**: 3.13.5
✅ **Zodiac Detection**: Working (currently Aquarius)
✅ **Moon Phases**: 8 phases calculated
✅ **Oracle Cards**: All 75 mapped
✅ **Suits**: 5 suits with essence quotes
✅ **Thermal Printer**: Ready for serial output
✅ **RFID Reader**: Ready for RC522 input

---

## Monitoring

Watch logs in real-time:

```bash
ssh divinofax "tail -f /home/oracle/divinofax/divinofax.log"
```

Check system resources:

```bash
ssh divinofax "free -h && df -h"
```

---

## Troubleshooting

### Can't SSH?
```bash
# Test connection
ping divinofax.local

# Check SSH config
cat ~/.ssh/config | grep -A 5 "Host divinofax"
```

### Module import errors?
```bash
ssh divinofax "cd /home/oracle/divinofax && python3 -m pip install -r requirements.txt"
```

### Printer not working?
```bash
ssh divinofax "python3 src/thermal_printer.py"
```

### RFID reader not responding?
```bash
ssh divinofax "python3 -c 'from src.rfid_reader import RFIDReader; print(\"RFID initialized\")'"
```

---

## Quick Commands

Check zodiac and moon phase:
```bash
ssh divinofax "cd /home/oracle/divinofax && python3 src/astrology.py && python3 src/moon_phase.py"
```

View system status:
```bash
ssh divinofax "uname -a && df -h / && free -h"
```

View recent git changes:
```bash
ssh divinofax "cd /home/oracle/divinofax && git log --oneline -5"
```

Test specific card:
```bash
ssh divinofax "cd /home/oracle/divinofax && python3 test_rfid_card.py"
```

---

## Security Notes

- SSH Key: `~/.ssh/id_rsa` (local machine only, never committed)
- Password: Use environment variables or config files locally
- Never commit credentials to git or code repositories

To regenerate SSH key if needed:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
ssh-copy-id -i ~/.ssh/id_rsa.pub oracle@divinofax.local
```

---

## Next Steps

1. ✅ Code deployed to Pi
2. ✅ SSH key-based auth configured
3. ⏭️ Connect RC522 RFID reader to Pi (SPI pins)
4. ⏭️ Connect thermal printer to Pi (UART pins)
5. ⏭️ Place RFID card on reader
6. ⏭️ Watch the fortune slip print!

---

🔮 **Your DivinoFax is ready!** 🔮

Place an RFID card on the reader and watch the magic happen!
