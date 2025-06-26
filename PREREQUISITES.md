# Software Prerequisites

## System Requirements

### Operating System
- **Linux** (Ubuntu 18.04+, Debian 10+, CentOS 7+, Fedora 30+)
- **macOS** (10.14+ with macFUSE)
- **Other Unix-like systems** with FUSE support

### Core Dependencies

#### 1. Python
- **Python 3.7 or higher**
- pip (Python package installer)
- venv (Virtual environment support)

**Installation:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip python3-venv
# OR (newer versions)
sudo dnf install python3 python3-pip python3-venv

# macOS (with Homebrew)
brew install python3
```

#### 2. FUSE (Filesystem in Userspace)
Required for mounting the virtual filesystem.

**Installation:**
```bash
# Ubuntu/Debian
sudo apt install fuse libfuse-dev

# CentOS/RHEL
sudo yum install fuse fuse-devel
# Enable user_allow_other in fuse.conf (if not already enabled)
echo "user_allow_other" | sudo tee -a /etc/fuse.conf

# Fedora
sudo dnf install fuse fuse-devel

# macOS
# Download and install macFUSE from: https://osxfuse.github.io/
```

**Important for file manager integration:** The installer automatically enables `user_allow_other` in `/etc/fuse.conf`, which allows the FUSE filesystem to be properly visible in GUI file managers like Thunar, Nautilus, etc.

#### 3. Git (for installation)
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL/Fedora
sudo yum install git
# OR
sudo dnf install git

# macOS
xcode-select --install
# OR with Homebrew
brew install git
```

### Python Dependencies (Auto-installed)
The following Python packages are automatically installed by the setup script:

- **fusepy** (≥3.0.1) - Python FUSE bindings
- **yt-dlp** (≥2023.12.30) - YouTube video extraction
- **requests** (≥2.31.0) - HTTP library for API calls
- **google-api-python-client** (≥2.108.0) - YouTube Data API client
- **google-auth-oauthlib** (≥1.1.0) - OAuth 2.0 authentication
- **google-auth-httplib2** (≥0.1.1) - HTTP transport for Google Auth

## System Permissions

### FUSE Access
Your user needs permission to use FUSE:

```bash
# Add user to fuse group (if it exists)
sudo usermod -a -G fuse $USER

# Enable user_allow_other in fuse.conf (if not already enabled)
echo "user_allow_other" | sudo tee -a /etc/fuse.conf

# Log out and back in for group changes to take effect
```

### Mount Point Access
The installer will handle mount point creation, but you need sudo access for:
- Creating directories in `/srv/`
- Installing systemd service files
- Managing systemd services

## Google Cloud Setup

### YouTube Data API v3
1. **Google Cloud Project** (free)
2. **YouTube Data API v3** enabled
3. **OAuth 2.0 Credentials** (Desktop application type)

**No billing required** - the YouTube Data API has a generous free quota.

## Verification Commands

Run these to verify prerequisites:

```bash
# Check Python version
python3 --version  # Should be 3.7+

# Check FUSE
fusermount --version

# Check if FUSE module is loaded
lsmod | grep fuse

# Check pip
python3 -m pip --version

# Check venv
python3 -m venv --help

# Check git
git --version

# Check sudo access
sudo echo "sudo works"
```

## Troubleshooting

### Common Issues

#### "Permission denied" when mounting
- Add user to fuse group: `sudo usermod -a -G fuse $USER`
- Enable user_allow_other: `echo "user_allow_other" | sudo tee -a /etc/fuse.conf`
- Log out and back in

#### "fuse: device not found"
- Install FUSE kernel module: `sudo modprobe fuse`
- On some systems: `sudo apt install fuse` or equivalent

#### Python version too old
- Install Python 3.7+ from your distribution's repositories
- Or use [pyenv](https://github.com/pyenv/pyenv) to install newer Python

#### macOS: "macFUSE not found"
- Download and install macFUSE from https://osxfuse.github.io/
- Reboot after installation
- Allow the kernel extension in System Preferences > Security & Privacy

### Testing FUSE
Create a simple test to verify FUSE works:

```bash
# Install test package
python3 -m pip install --user fusepy

# Create test script
cat > test_fuse.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
from fuse import FUSE, FuseOSError, Operations
import stat

class TestFS(Operations):
    def getattr(self, path, fh=None):
        if path == '/':
            st = dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)
        else:
            raise FuseOSError(errno.ENOENT)
        st['st_uid'] = os.getuid()
        st['st_gid'] = os.getgid()
        return st
    
    def readdir(self, path, fh):
        return ['.', '..', 'test.txt']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: test_fuse.py <mountpoint>')
        sys.exit(1)
    
    mountpoint = sys.argv[1]
    os.makedirs(mountpoint, exist_ok=True)
    
    print(f"Mounting test filesystem at {mountpoint}")
    print("Press Ctrl+C to unmount")
    
    try:
        FUSE(TestFS(), mountpoint, foreground=True)
    except KeyboardInterrupt:
        print("\nUnmounting...")
EOF

# Run test
mkdir -p test_mount
python3 test_fuse.py test_mount
# In another terminal: ls test_mount
# Should see test.txt file
# Press Ctrl+C to stop
```

If this test works, your system supports FUSE and the YouTube filesystem should work too.
