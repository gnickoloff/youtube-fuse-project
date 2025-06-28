# Local System Scripts

This directory contains system-specific scripts that are **NOT** included in the distributed package:

## User Switching Scripts (Local Only)

These scripts are specific to your HTPC setup and help switch between different system users:

### `switch_to_mythtv.sh`
- Switches the YouTube FUSE service to run as `mythtv:mythtv`
- Useful for HTPC systems where MythTV is the primary media application
- Updates permissions and service configuration appropriately

### `switch_to_gnicko.sh` 
- Switches the YouTube FUSE service back to run as `gnicko:gnicko`
- Restores original user configuration
- Useful for development or single-user setups

## Why These Are Local Only

These scripts contain:
- **Hardcoded usernames** (`gnicko`, `mythtv`) specific to your system
- **System-specific paths** and configurations
- **Local permission assumptions** about your HTPC setup

## For Distribution

The distributed package includes:
- ✅ `install.sh` - Generic installer that works on any system
- ✅ `youtube-fuse.service.template` - Template that adapts to any user
- ✅ `uninstall.sh` - Generic uninstaller
- ❌ **NOT** these user-switching scripts (they're in `.gitignore`)

## Usage

```bash
# Switch to mythtv user (recommended for HTPC)
./switch_to_mythtv.sh

# Switch back to original user
./switch_to_gnicko.sh
```

These scripts handle all the permission changes, service restarts, and configuration updates automatically.
