# DivinoFax Setup & Connection Information

## Raspberry Pi Connection Details

### SSH Connection
```bash
ssh oracle@divinofax.local
# or
ssh oracle@raspberrypi.local
```

**Credentials:**
- **Hostname**: `divinofax`
- **Username**: `oracle`
- **Password**: `Oracle123!`

### Network Address
- **IP Address**: 10.0.0.95
- **Hostname**: `divinofax.local` or `raspberrypi.local`

## Quick Connection Test
```bash
# Test connectivity
ping divinofax.local

# Connect via SSH
ssh oracle@divinofax.local

# Check system info
uname -a
```

## Next Steps
1. Clone the repository on the Pi:
   ```bash
   git clone https://github.com/MakingCoffee/DivinoFax.git
   cd DivinoFax
   ```

2. Run the installation script:
   ```bash
   sudo ./install.sh
   ```

3. Configure for your hardware:
   ```bash
   nano config/divinofax.yaml
   ```

4. Start testing:
   ```bash
   SIMULATION_MODE=true python3 src/divinofax.py
   ```

---

**Last Updated**: 2026-02-16
