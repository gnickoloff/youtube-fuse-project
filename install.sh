#!/bin/bash

# YouTube FUSE Filesystem Installation Script
# This script sets up the YouTube FUSE filesystem as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_MOUNT_POINT="/srv/youtube"
SERVICE_NAME="youtube-fuse"

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}    YouTube FUSE Filesystem Installer${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_step "Checking requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root!"
        print_info "Run as your regular user. sudo will be used when needed."
        exit 1
    fi
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check if we're in the project directory
    if [[ ! -f "youtube_api_fuse.py" ]]; then
        print_error "Please run this script from the youtube-fuse-project directory."
        exit 1
    fi
    
    print_info "Requirements check passed!"
}

setup_python_environment() {
    print_step "Setting up Python virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        print_info "Created virtual environment"
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_info "Installed Python dependencies"
}

get_user_input() {
    print_step "Getting configuration..."
    
    # Get current user
    CURRENT_USER=$(whoami)
    echo -e "Current user: ${GREEN}$CURRENT_USER${NC}"
    
    # Get project directory
    PROJECT_DIR=$(pwd)
    echo -e "Project directory: ${GREEN}$PROJECT_DIR${NC}"
    
    # Get home directory
    HOME_DIR=$(eval echo ~$CURRENT_USER)
    echo -e "Home directory: ${GREEN}$HOME_DIR${NC}"
    
    # Ask for mount point
    echo
    read -p "Mount point [$DEFAULT_MOUNT_POINT]: " MOUNT_POINT
    MOUNT_POINT=${MOUNT_POINT:-$DEFAULT_MOUNT_POINT}
    echo -e "Mount point: ${GREEN}$MOUNT_POINT${NC}"
    
    echo
}

create_mount_point() {
    print_step "Creating mount point..."
    
    if [[ ! -d "$MOUNT_POINT" ]]; then
        sudo mkdir -p "$MOUNT_POINT"
        sudo chown "$CURRENT_USER:$CURRENT_USER" "$MOUNT_POINT"
        print_info "Created mount point: $MOUNT_POINT"
    else
        print_info "Mount point already exists: $MOUNT_POINT"
    fi
}

generate_service_file() {
    print_step "Generating systemd service file..."
    
    # Replace placeholders in template
    sed -e "s|%USER%|$CURRENT_USER|g" \
        -e "s|%PROJECT_DIR%|$PROJECT_DIR|g" \
        -e "s|%MOUNT_POINT%|$MOUNT_POINT|g" \
        -e "s|%HOME_DIR%|$HOME_DIR|g" \
        youtube-fuse.service.template > youtube-fuse.service.generated
    
    print_info "Generated service file"
}

install_service() {
    print_step "Installing systemd service..."
    
    # Copy service file
    sudo cp youtube-fuse.service.generated "/etc/systemd/system/$SERVICE_NAME.service"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable "$SERVICE_NAME"
    
    print_info "Service installed and enabled"
}

check_credentials() {
    print_step "Checking credentials..."
    
    if [[ ! -f "client_secrets.json" ]]; then
        print_error "client_secrets.json not found!"
        echo
        echo "Please set up your OAuth credentials first:"
        echo "1. Go to https://console.cloud.google.com/apis/credentials"
        echo "2. Create OAuth 2.0 Client ID (Desktop application)"
        echo "3. Download the JSON file as 'client_secrets.json'"
        echo "4. Run this installer again"
        exit 1
    fi
    
    # Secure the credentials file
    chmod 600 client_secrets.json
    print_info "Secured client_secrets.json permissions"
    
    if [[ ! -f "youtube_config.json" ]]; then
        print_info "Creating default configuration..."
        cat > youtube_config.json << EOF
{
  "api_key": "",
  "client_secrets_file": "client_secrets.json",
  "use_oauth": true,
  "playlists": {
    "auto_discover": true,
    "watch_later": false,
    "custom_playlists": []
  },
  "refresh_interval": 300,
  "video_quality": "best[ext=mp4]/best"
}
EOF
        chmod 600 youtube_config.json
        print_info "Created and secured youtube_config.json"
    else
        chmod 600 youtube_config.json
        print_info "Secured youtube_config.json permissions"
    fi
    
    # Secure token file if it exists
    if [[ -f "token.json" ]]; then
        chmod 600 token.json
        print_info "Secured token.json permissions"
    fi
    
    print_info "Credentials check passed"
}

start_service() {
    print_step "Starting service..."
    
    # Stop existing service if running
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    
    # Unmount if already mounted
    fusermount -u "$MOUNT_POINT" 2>/dev/null || sudo fusermount -u "$MOUNT_POINT" 2>/dev/null || true
    
    # Start service
    sudo systemctl start "$SERVICE_NAME"
    
    # Wait a moment for startup
    sleep 3
    
    # Check status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        print_info "Service started successfully!"
    else
        print_error "Service failed to start. Check status with: sudo systemctl status $SERVICE_NAME"
        exit 1
    fi
}

test_mount() {
    print_step "Testing mount..."
    
    # Wait for mount to be ready
    sleep 5
    
    if mountpoint -q "$MOUNT_POINT"; then
        PLAYLIST_COUNT=$(ls "$MOUNT_POINT" 2>/dev/null | wc -l)
        if [[ $PLAYLIST_COUNT -gt 0 ]]; then
            print_info "✓ Mount successful! Found $PLAYLIST_COUNT playlists"
            echo -e "Your YouTube playlists are now available at: ${GREEN}$MOUNT_POINT${NC}"
        else
            print_error "Mount point is empty. Check service logs: sudo journalctl -u $SERVICE_NAME -f"
        fi
    else
        print_error "Mount failed. Check service logs: sudo journalctl -u $SERVICE_NAME -f"
    fi
}

show_usage() {
    echo
    echo -e "${GREEN}Installation complete!${NC}"
    echo
    echo "Your YouTube FUSE filesystem is now:"
    echo -e "  📁 Mounted at: ${GREEN}$MOUNT_POINT${NC}"
    echo -e "  🔄 Auto-starts on boot"
    echo -e "  🔍 Auto-discovers all your playlists"
    echo
    echo "Useful commands:"
    echo "  sudo systemctl status $SERVICE_NAME     # Check service status"
    echo "  sudo systemctl stop $SERVICE_NAME       # Stop the service"
    echo "  sudo systemctl start $SERVICE_NAME      # Start the service"
    echo "  sudo systemctl restart $SERVICE_NAME    # Restart the service"
    echo "  sudo journalctl -u $SERVICE_NAME -f     # View service logs"
    echo
    echo -e "Browse your YouTube library: ${GREEN}ls '$MOUNT_POINT'${NC}"
    echo
}

cleanup() {
    # Clean up generated files
    rm -f youtube-fuse.service.generated
}

# Main installation flow
main() {
    print_header
    check_requirements
    setup_python_environment
    get_user_input
    check_credentials
    create_mount_point
    generate_service_file
    install_service
    start_service
    test_mount
    show_usage
    cleanup
}

# Run main function
main "$@"
