#!/bin/bash

# Divinofax Installation Script for Raspberry Pi
# ==============================================
# 
# This script sets up the Divinofax fortune-telling system on a fresh
# Raspberry Pi 4 Model B with the required dependencies and configuration.
#
# Usage: sudo ./install.sh
#
# Author: Kathryn Bennett

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    log_info "Checking if running on Raspberry Pi..."
    
    if [[ ! -f /proc/cpuinfo ]] || ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        log_warning "This doesn't appear to be a Raspberry Pi"
        log_info "Installation will continue in simulation mode"
        SIMULATION_MODE=true
    else
        log_success "Raspberry Pi detected"
        SIMULATION_MODE=false
    fi
}

# Check for root privileges
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    apt update
    apt upgrade -y
    log_success "System updated"
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    # Essential packages
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        cmake \
        git \
        curl \
        wget
    
    # Hardware-specific packages for Raspberry Pi
    if [[ "$SIMULATION_MODE" == "false" ]]; then
        apt install -y \
            gpio \
            wiringpi \
            spi-tools \
            i2c-tools \
            python3-rpi.gpio
        
        # Enable SPI and I2C
        raspi-config nonint do_spi 0
        raspi-config nonint do_i2c 0
        raspi-config nonint do_serial 0
        
        log_success "Hardware interfaces enabled"
    fi
    
    log_success "System dependencies installed"
}

# Create divinofax user and directories
setup_user() {
    log_info "Setting up divinofax user and directories..."
    
    # Create divinofax user if it doesn't exist
    if ! id "divinofax" &>/dev/null; then
        useradd -m -s /bin/bash divinofax
        usermod -a -G gpio,spi,i2c divinofax 2>/dev/null || true
        log_success "Created divinofax user"
    else
        log_info "User divinofax already exists"
    fi
    
    # Create application directory
    INSTALL_DIR="/opt/divinofax"
    mkdir -p "$INSTALL_DIR"
    
    # Copy application files
    log_info "Copying application files..."
    cp -r src/ "$INSTALL_DIR/"
    cp -r data/ "$INSTALL_DIR/" 2>/dev/null || mkdir -p "$INSTALL_DIR/data"
    cp -r config/ "$INSTALL_DIR/" 2>/dev/null || mkdir -p "$INSTALL_DIR/config"
    cp requirements.txt "$INSTALL_DIR/"
    
    # Set ownership
    chown -R divinofax:divinofax "$INSTALL_DIR"
    chmod +x "$INSTALL_DIR/src/divinofax.py"
    
    log_success "Application files installed to $INSTALL_DIR"
}

# Setup Python virtual environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    INSTALL_DIR="/opt/divinofax"
    VENV_DIR="$INSTALL_DIR/venv"
    
    # Create virtual environment
    sudo -u divinofax python3 -m venv "$VENV_DIR"
    
    # Upgrade pip
    sudo -u divinofax "$VENV_DIR/bin/pip" install --upgrade pip
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    sudo -u divinofax "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    log_success "Python environment configured"
}

# Download and setup LLM models
setup_llm_models() {
    log_info "Setting up LLM models..."
    
    INSTALL_DIR="/opt/divinofax"
    MODELS_DIR="$INSTALL_DIR/models"
    
    mkdir -p "$MODELS_DIR"
    chown divinofax:divinofax "$MODELS_DIR"
    
    if [[ "$SIMULATION_MODE" == "false" ]]; then
        log_info "Downloading quantized Llama model for Raspberry Pi..."
        
        # Download a small quantized model suitable for Pi 4
        MODEL_URL="https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.q4_0.bin"
        MODEL_FILE="$MODELS_DIR/llama-2-7b-chat.Q4_0.gguf"
        
        if [[ ! -f "$MODEL_FILE" ]]; then
            log_info "This may take a while (downloading ~4GB model)..."
            sudo -u divinofax wget -O "$MODEL_FILE" "$MODEL_URL" || {
                log_warning "Failed to download model automatically"
                log_info "You can download it manually later to: $MODEL_FILE"
            }
        else
            log_info "Model already exists"
        fi
    else
        log_info "Simulation mode - skipping model download"
    fi
    
    log_success "LLM models configured"
}

# Create configuration files
create_config() {
    log_info "Creating configuration files..."
    
    INSTALL_DIR="/opt/divinofax"
    CONFIG_FILE="$INSTALL_DIR/config/divinofax.yaml"
    
    mkdir -p "$INSTALL_DIR/config"
    
    cat > "$CONFIG_FILE" << EOF
# Divinofax Configuration
# =======================

system:
  log_level: INFO
  simulation_mode: $SIMULATION_MODE
  debug_mode: false

pico:
  port: /dev/ttyACM0
  simulation_mode: $SIMULATION_MODE
  lights_enabled: true
  startup_light_sequence: true

rfid:
  simulation_mode: $SIMULATION_MODE
  debounce_time: 2.0

llm:
  simulation_mode: $SIMULATION_MODE
  model_path: models/llama-2-7b-chat.Q4_0.gguf
  n_ctx: 512
  n_threads: 4

printer:
  simulation_mode: $SIMULATION_MODE
  port: /dev/ttyS0
  use_decorations: true

text_library:
  data_directory: data/texts
EOF
    
    chown divinofax:divinofax "$CONFIG_FILE"
    log_success "Configuration file created"
}

# Create systemd service
create_service() {
    log_info "Creating systemd service..."
    
    cat > /etc/systemd/system/divinofax.service << EOF
[Unit]
Description=Divinofax Fortune Telling System
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
User=divinofax
ExecStart=/opt/divinofax/venv/bin/python /opt/divinofax/src/divinofax.py
WorkingDirectory=/opt/divinofax
Environment=PYTHONPATH=/opt/divinofax/src

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable divinofax
    
    log_success "Systemd service created and enabled"
}

# Create management script
create_management_script() {
    log_info "Creating management script..."
    
    cat > /usr/local/bin/divinofax << 'EOF'
#!/bin/bash

# Divinofax Management Script

INSTALL_DIR="/opt/divinofax"
SERVICE_NAME="divinofax"

case "$1" in
    start)
        echo "Starting Divinofax..."
        systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "Stopping Divinofax..."
        systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "Restarting Divinofax..."
        systemctl restart $SERVICE_NAME
        ;;
    status)
        systemctl status $SERVICE_NAME
        ;;
    logs)
        journalctl -u $SERVICE_NAME -f
        ;;
    test)
        echo "Testing Divinofax components..."
        cd $INSTALL_DIR
        sudo -u divinofax $INSTALL_DIR/venv/bin/python -m pytest tests/ || echo "Run 'divinofax test-manual' for manual testing"
        ;;
    test-manual)
        echo "Running manual component tests..."
        cd $INSTALL_DIR/src
        echo "Testing text library..."
        sudo -u divinofax $INSTALL_DIR/venv/bin/python text_library.py
        echo "Testing LLM engine..."
        sudo -u divinofax $INSTALL_DIR/venv/bin/python llm_engine.py
        echo "Testing thermal printer..."
        sudo -u divinofax $INSTALL_DIR/venv/bin/python thermal_printer.py
        echo "Testing Pico controller..."
        sudo -u divinofax $INSTALL_DIR/venv/bin/python pico_controller.py
        ;;
    update)
        echo "Updating Divinofax..."
        echo "Pull latest code from git repository and restart service"
        ;;
    config)
        nano $INSTALL_DIR/config/divinofax.yaml
        ;;
    *)
        echo "Usage: divinofax {start|stop|restart|status|logs|test|test-manual|config|update}"
        exit 1
        ;;
esac
EOF
    
    chmod +x /usr/local/bin/divinofax
    log_success "Management script created at /usr/local/bin/divinofax"
}

# Print installation summary
print_summary() {
    log_success "Divinofax installation complete!"
    echo
    echo -e "${GREEN}Installation Summary:${NC}"
    echo -e "  Installation directory: ${BLUE}/opt/divinofax${NC}"
    echo -e "  Configuration file: ${BLUE}/opt/divinofax/config/divinofax.yaml${NC}"
    echo -e "  System user: ${BLUE}divinofax${NC}"
    echo -e "  Simulation mode: ${BLUE}$SIMULATION_MODE${NC}"
    echo
    echo -e "${GREEN}Management Commands:${NC}"
    echo -e "  Start service: ${BLUE}divinofax start${NC}"
    echo -e "  Stop service: ${BLUE}divinofax stop${NC}"
    echo -e "  Check status: ${BLUE}divinofax status${NC}"
    echo -e "  View logs: ${BLUE}divinofax logs${NC}"
    echo -e "  Test system: ${BLUE}divinofax test${NC}"
    echo -e "  Edit config: ${BLUE}divinofax config${NC}"
    echo
    
    if [[ "$SIMULATION_MODE" == "true" ]]; then
        log_info "Running in simulation mode - hardware interfaces disabled"
        log_info "To test: divinofax test-manual"
    else
        log_info "Hardware interfaces enabled for Raspberry Pi"
        log_info "Connect your RFID reader and thermal printer, then: divinofax start"
    fi
    
    echo
    log_info "For support or issues, check the logs with: divinofax logs"
}

# Main installation flow
main() {
    echo -e "${BLUE}"
    echo "🔮 Divinofax Installation Script 🔮"
    echo "===================================="
    echo -e "${NC}"
    
    check_root
    check_raspberry_pi
    
    log_info "Starting Divinofax installation..."
    
    update_system
    install_system_deps
    setup_user
    setup_python_env
    setup_llm_models
    create_config
    create_service
    create_management_script
    
    print_summary
}

# Run main installation
main "$@"
