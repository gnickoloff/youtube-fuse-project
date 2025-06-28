#!/bin/bash

# YouTube FUSE Filesystem Uninstaller
# This script removes the YouTube FUSE filesystem service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="youtube-fuse"
DEFAULT_MOUNT_POINT="/srv/youtube"

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   YouTube FUSE Filesystem Uninstaller${NC}"
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

confirm_uninstall() {
    echo -e "${YELLOW}This will remove the YouTube FUSE filesystem service.${NC}"
    echo "The project files will remain, but the systemd service will be removed."
    echo
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Uninstall cancelled."
        exit 0
    fi
}

stop_service() {
    print_step "Stopping service..."
    
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        sudo systemctl stop "$SERVICE_NAME"
        print_info "Service stopped"
    else
        print_info "Service was not running"
    fi
}

disable_service() {
    print_step "Disabling service..."
    
    if sudo systemctl is-enabled --quiet "$SERVICE_NAME"; then
        sudo systemctl disable "$SERVICE_NAME"
        print_info "Service disabled"
    else
        print_info "Service was not enabled"
    fi
}

remove_service_file() {
    print_step "Removing service file..."
    
    if [[ -f "/etc/systemd/system/$SERVICE_NAME.service" ]]; then
        sudo rm "/etc/systemd/system/$SERVICE_NAME.service"
        sudo systemctl daemon-reload
        print_info "Service file removed"
    else
        print_info "Service file not found"
    fi
}

unmount_filesystem() {
    print_step "Unmounting filesystem..."
    
    # Try different mount points
    for mount_point in "$DEFAULT_MOUNT_POINT" "/srv/youtube" "$(pwd)/test-mount"; do
        if mountpoint -q "$mount_point" 2>/dev/null; then
            fusermount -u "$mount_point" 2>/dev/null || sudo fusermount -u "$mount_point" 2>/dev/null || true
            print_info "Unmounted: $mount_point"
        fi
    done
}

cleanup_mount_point() {
    read -p "Remove mount point directory $DEFAULT_MOUNT_POINT? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -d "$DEFAULT_MOUNT_POINT" ]]; then
            sudo rmdir "$DEFAULT_MOUNT_POINT" 2>/dev/null || print_info "Mount point not empty, left in place"
        fi
    fi
}

show_completion() {
    echo
    echo -e "${GREEN}Uninstall complete!${NC}"
    echo
    echo "The YouTube FUSE filesystem service has been removed."
    echo "Project files remain in: $(pwd)"
    echo
    echo "To completely remove the project:"
    echo "  cd .."
    echo "  rm -rf youtube-fuse-project"
    echo
}

# Main uninstallation flow
main() {
    print_header
    confirm_uninstall
    stop_service
    unmount_filesystem
    disable_service
    remove_service_file
    cleanup_mount_point
    show_completion
}

# Run main function
main "$@"
