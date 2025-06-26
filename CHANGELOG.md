# YouTube FUSE Filesystem - Release Notes

## Version 1.0.0 - 2025-06-25

🎉 **First Stable Release!**

### Overview
YouTube FUSE Filesystem v1.0.0 is a production-ready FUSE-based filesystem that mounts YouTube playlists as virtual video files on your local system. Perfect for HTPC systems, media centers, and development environments.

### ✨ Key Features

#### 🎥 **Core Functionality**
- Mount YouTube playlists as local directories
- Stream videos directly without downloading
- Support for both public and private playlists
- Auto-discovery of all user playlists
- Smart caching for optimal performance
- HTTP range requests for video seeking

#### 🔐 **Authentication & Security**
- OAuth 2.0 authentication for private playlists
- API key support for public playlists
- Automatic credential file security (chmod 600)
- Environment variable support for credentials
- Watch Later playlist access

#### 🖥️ **System Integration**
- Professional systemd service integration
- Auto-start on boot capability
- One-command installation with `./install.sh`
- Clean uninstallation with `./uninstall.sh`
- HTPC optimization (MythTV user support)
- Cross-platform support (Linux/macOS with FUSE)

#### 📦 **Distribution & Deployment**
- Generic installer that adapts to any system
- Template-based systemd service files
- Comprehensive documentation and prerequisites guide
- Clean separation of local configs and distributable components
- User-switching scripts for HTPC environments

### 🛠️ **Installation**

#### Quick Install
```bash
git clone <your-repo-url>
cd youtube-fuse-project
./install.sh
```

#### Manual Setup
```bash
./setup.sh                    # Set up development environment
source venv/bin/activate      # Activate virtual environment
python youtube_api_fuse.py ./mount-point  # Test mount
```

### 📋 **System Requirements**

#### Core Dependencies
- **Linux/macOS** with FUSE support
- **Python 3.7+** with pip and venv
- **Git** for installation
- **sudo access** for system integration

#### FUSE Libraries
- Ubuntu/Debian: `sudo apt install fuse libfuse-dev`
- CentOS/RHEL: `sudo yum install fuse fuse-devel`
- macOS: Install [macFUSE](https://osxfuse.github.io/)

### 🔧 **Configuration**

#### OAuth Setup (Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 Client ID (Desktop application)
3. Download as `client_secrets.json`
4. Run installer

#### API Key Setup (Public playlists only)
```bash
export YOUTUBE_API_KEY="your-api-key"
export YOUTUBE_USE_OAUTH=false
```

### 📂 **File Structure**

#### Distribution Files (Included in package)
- `youtube_api_fuse.py` - Main FUSE filesystem
- `install.sh` - Automated installer
- `uninstall.sh` - Clean removal script
- `youtube-fuse.service.template` - Systemd template
- `README.md` - Complete documentation
- `PREREQUISITES.md` - System requirements guide
- `requirements.txt` - Python dependencies

#### Local Files (System-specific, not distributed)
- `client_secrets.json` - OAuth credentials
- `token.json` - OAuth tokens
- `youtube_config.json` - Local configuration
- `switch_to_*.sh` - User switching scripts

### 🎯 **Usage Examples**

#### Browse Playlists
```bash
ls /srv/youtube/                    # List all playlists
ls "/srv/youtube/My Playlist/"      # List videos in playlist
```

#### Stream with Media Players
```bash
vlc "/srv/youtube/My Playlist/My Video.mp4"
mpv "/srv/youtube/Watch Later/Tutorial.mp4"
```

#### System Integration
```bash
sudo systemctl status youtube-fuse     # Check service status
sudo systemctl restart youtube-fuse    # Restart service
sudo journalctl -u youtube-fuse -f     # View logs
```

### 🔄 **HTPC Integration**

For HTPC systems (MythTV, Kodi, etc.):
```bash
./switch_to_mythtv.sh    # Switch to media center user
```

This optimizes the filesystem for media center integration and maintains consistency with `/srv/` directory ownership.

### 🛡️ **Security Features**

- **Credential Protection**: All sensitive files automatically secured with 600 permissions
- **Environment Priority**: Environment variables override config files
- **No Sensitive Distribution**: Credentials never included in distributed packages
- **OAuth Token Management**: Automatic token refresh and secure storage

### 📈 **Performance**

- **Smart Caching**: Video metadata cached for 5 minutes (configurable)
- **Stream URL Caching**: Fresh URLs cached for 30 minutes
- **Lazy Loading**: Playlists loaded on-demand
- **Range Requests**: Efficient streaming with seek support

### 🐛 **Known Limitations**

- Read-only filesystem (no upload capability)
- Requires active internet connection
- YouTube rate limits apply
- Stream URLs have expiration (handled automatically)
- Linux/macOS only (no Windows FUSE support)

### 🔮 **Future Enhancements**

- Web interface for configuration
- Multiple YouTube account support
- Playlist filtering and search
- Integration with media server APIs
- Windows support (when FUSE becomes available)

### 📞 **Support**

- **Documentation**: See README.md and PREREQUISITES.md
- **Prerequisites**: Detailed system requirements in PREREQUISITES.md
- **Troubleshooting**: Common issues and solutions in README.md
- **Installation**: Step-by-step guide with install.sh

### 🙏 **Acknowledgments**

Built with:
- **FUSE** - Filesystem in Userspace
- **yt-dlp** - YouTube video extraction
- **Google APIs** - YouTube Data API v3
- **Python ecosystem** - requests, google-api-python-client

### 📄 **License**

This project is for educational and personal use. Please respect YouTube's Terms of Service.

---

**Ready for production use! 🚀**

Perfect for HTPC systems, media centers, and any environment where you want seamless access to your YouTube library through the filesystem.
