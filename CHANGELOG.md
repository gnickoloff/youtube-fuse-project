# YouTube FUSE Filesystem - Release Notes

## Version 1.2.0 - 2025-06-26

🗂️ **Playlist Subdirectory Organization & Auto-Discovery**

### 🆕 New Features

#### 📁 **Automatic Playlist Organization**
- **Subdirectory structure** - Each playlist now appears as its own directory
- **Auto-discovery** - Automatically finds and mounts all user playlists when `auto_discover: true`
- **Clean organization** - Videos are organized within their respective playlist directories
- **Sanitized directory names** - Playlist titles converted to filesystem-safe directory names

#### 🔍 **Auto-Discovery Configuration**
- New `auto_discover` config option to enable automatic playlist detection
- Discovers all user playlists via YouTube API
- Creates individual subdirectories for each playlist
- Maintains existing Watch Later and custom playlist support

### 🗂️ **Directory Structure**
```
/srv/youtube/
├── Watch_Later/                 # Watch Later playlist
├── My_Cooking_Videos/          # Auto-discovered playlist  
├── Gaming_Tutorials/           # Auto-discovered playlist
└── Custom_Playlist_Name/       # Custom playlist by ID
```

### 🔧 **Technical Improvements**
- Refactored FUSE operations (`getattr`, `readdir`, `open`, `read`) for directory support
- Enhanced playlist metadata caching with nested video organization
- Updated configuration structure with `auto_discover` option
- Improved path handling for subdirectory navigation

### 💡 **Benefits**
- **Better Organization**: Videos grouped by playlist for easier browsing
- **Scalable**: Works with hundreds of playlists without cluttering root directory
- **Intuitive Navigation**: Familiar directory-based file management
- **Automatic Discovery**: No need to manually configure playlist IDs

---

## Version 1.1.0 - 2025-01-14

🕒 **Authentic Timestamp Support**

### 🆕 New Features

#### 📅 **YouTube Publish Date Integration**
- **File timestamps now reflect actual YouTube publish dates** - Videos in the mounted filesystem show their real YouTube publish date as the file modification time
- Enhanced metadata accuracy for media organization
- Better integration with backup tools and media applications that sort by date
- Authentic file attributes that match the original content timeline

### 🔧 **Technical Improvements**
- Modified FUSE `getattr()` to extract and use YouTube video `publishedAt` metadata
- Automatic conversion of ISO 8601 timestamp format to Unix timestamp
- Fallback to current time if publish date is unavailable
- Maintains compatibility with all existing functionality

### 💡 **Benefits**
- **Media Library Organization**: Sort videos by actual publish date in file managers
- **Authentic Metadata**: File properties reflect real YouTube timeline
- **Backup Consistency**: Timestamp preservation across backup operations
- **Timeline Accuracy**: Historical context preserved in filesystem view

### 📋 **Example Usage**
```bash
# See real YouTube publish dates
ls -la /srv/youtube/Watch\ Later/
# -rw-r--r-- 1 mythtv mythtv 0 Dec 15  2023 My Video.mp4
#                                ^^^^^^^^^^^^^
#                                Actual YouTube publish date

# Use with media tools that respect timestamps
find /srv/youtube -type f -newermt "2024-01-01" | head -10
```

### ⬆️ **Upgrade Notes**
- Fully backward compatible - no configuration changes needed
- Existing mounts will automatically show correct timestamps after restart
- All previous functionality remains unchanged

---

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
