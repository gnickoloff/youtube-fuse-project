# YouTube FUSE Filesystem

A FUSE-based filesystem that mounts YouTube playlists as virtual video files on your local system. Stream videos directly from YouTube through your filesystem!

> **⚠️ QUOTA MANAGEMENT**: YouTube API has daily quota limits. If you're experiencing crashes due to quota exhaustion, see **[QUOTA_MANAGEMENT.md](QUOTA_MANAGEMENT.md)** for immediate solutions and traffic control.

## Features

- 🎥 Mount YouTube playlists as local directories
- 📁 **Auto-discover all user playlists** with subdirectory organization
- 📺 Stream videos directly without downloading
- 🔐 Support for both public playlists (API key) and private playlists (OAuth)
- ⚡ **Smart incremental refresh** - saves 80-95% of API quota
- 🎯 **ETag-based change detection** - only fetch what actually changed
- 🎬 Watch Later playlist support
- 📱 HTTP range requests for video seeking
- 🔄 Auto-refresh playlist contents
- 📅 Authentic file timestamps (YouTube publish dates)
- 🗂️ **Organized directory structure** - each playlist becomes a subdirectory
- 📊 **Advanced quota management** with rate limiting and emergency mode
- 🎛️ **Web dashboard** for real-time monitoring and control
- 📈 **Quota analytics** and efficiency tracking
- 🎛️ **Configurable playlist selection** and traffic controls

## Requirements

### Quick Prerequisites Check
- **Linux/macOS** with FUSE support
- **Python 3.7+** 
- **Git** for installation
- **sudo access** for system integration

**👉 For detailed requirements and installation instructions, see [PREREQUISITES.md](PREREQUISITES.md)**

### System Dependencies
- **FUSE libraries**:
  - Ubuntu/Debian: `sudo apt install fuse libfuse-dev`
  - CentOS/RHEL: `sudo yum install fuse fuse-devel`
  - macOS: Install [macFUSE](https://osxfuse.github.io/)

### Python Dependencies
All Python dependencies are automatically installed by the setup script.

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd youtube-fuse-project
./setup.sh
```

### 2. Get YouTube API Credentials

#### Option A: API Key (for public playlists only)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Set environment variable: `export YOUTUBE_API_KEY="your-key-here"`

#### Option B: OAuth (for Watch Later and private playlists)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "YouTube Data API v3"
4. Create credentials → OAuth 2.0 Client IDs
5. Download the JSON file as `client_secrets.json`
6. Place it in the project directory

### 3. Configure and Run

#### Quick Start (API Key - Recommended for beginners):
```bash
# Set your credentials
export YOUTUBE_API_KEY="your-api-key-here"
export YOUTUBE_USE_OAUTH=false

# Activate and run
source venv/bin/activate
python youtube_api_fuse.py ./test-mount

# Browse your videos
ls ./test-mount/
```

#### Advanced (OAuth for Watch Later):
```bash
# Use OAuth (requires client_secrets.json)
export YOUTUBE_USE_OAUTH=true
source venv/bin/activate
python youtube_api_fuse.py ./test-mount
```

#### Alternative: Config File Method
Edit `youtube_config.json`:
```json
{
  "api_key": "your-api-key-here",
  "use_oauth": false,
  "playlists": {
    "watch_later": true,
    "custom_playlists": ["PLxxx"]
  }
}
```

## 📊 Quota Management

YouTube API has daily quota limits. This project includes comprehensive quota management to prevent hitting limits:

### Quota Configuration

```json
{
  "quota_management": {
    "enabled": true,
    "daily_quota_limit": 8000,
    "rate_limit_delay": 1.5,
    "quota_reset_hour": 0,
    "emergency_mode": false,
    "cache_duration": 3600
  },
  "playlists": {
    "max_playlists": 5,
    "max_videos_per_playlist": 25,
    "enabled_playlists": ["specific_playlist_id"]
  }
}
```

### Quota Management Features

- **Daily Quota Tracking**: Monitors API usage against your daily limit
- **Rate Limiting**: Adds delays between API calls to prevent bursts
- **Emergency Mode**: Completely disables API calls when quota is exhausted
- **Smart Caching**: Extends cache duration when quota is running low
- **Playlist Limiting**: Control exactly which playlists to fetch
- **Video Limiting**: Limit videos per playlist to reduce quota usage

### Using the Quota Manager

```bash
# Check current quota status and estimated usage
python quota_manager.py --status

# Get optimization suggestions
python quota_manager.py --optimize

# Enable emergency mode (stops all API calls)
python quota_manager.py --emergency-on

# Disable emergency mode
python quota_manager.py --emergency-off
```

### Quota Optimization Tips

1. **Limit Playlists**: Use `enabled_playlists` to fetch only needed playlists
2. **Reduce Video Count**: Set `max_videos_per_playlist` to 10-25
3. **Increase Cache Time**: Set longer `refresh_interval` (1800-3600 seconds)
4. **Rate Limiting**: Use 1.5-2.0 second delays between API calls
5. **Monitor Usage**: Check logs for quota consumption patterns

### Emergency Mode

When quota is exhausted, enable emergency mode:
```bash
python quota_manager.py --emergency-on
```
This will:
- Disable all YouTube API calls
- Serve cached content only
- Prevent further quota consumption

## 🚨 Quick Quota Management

If you're hitting YouTube API quota limits:

```bash
# EMERGENCY: Stop all API calls immediately
./quota_control.sh emergency-on

# Apply conservative settings
./quota_control.sh conservative

# Check quota status
./quota_control.sh status

# Re-enable when ready
./quota_control.sh emergency-off
```

**📖 Full quota management guide: [QUOTA_MANAGEMENT.md](QUOTA_MANAGEMENT.md)**

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `api_key` | YouTube Data API key | `"AIza..."`  |
| `use_oauth` | Use OAuth instead of API key | `true`/`false` |
| `auto_discover` | Auto-discover all user playlists | `true`/`false` |
| `watch_later` | Include Watch Later playlist | `true`/`false` |
| `custom_playlists` | List of playlist IDs to mount | `["PLxxx", "PLyyy"]` |
| `refresh_interval` | Seconds between playlist updates | `300` |
| `video_quality` | yt-dlp format selector | `"best[ext=mp4]/best"` |

## 🚀 Quota Efficiency (NEW!)

**YouTube FUSE v2.0+** includes revolutionary **incremental refresh** that saves **80-95% of your API quota**:

### Smart Change Detection
- **ETag-based tracking** - Uses YouTube's native change detection
- **Conditional requests** - HTTP 304 "Not Modified" responses cost zero quota
- **Granular updates** - Only fetch playlists that actually changed

### Quota Savings Example
```bash
# Traditional approach: 50 quota units per refresh
# With incremental refresh: 2-5 quota units per refresh
# 🎉 90% quota savings!

# View your efficiency metrics
python3 quota_analytics.py report

# Test the difference
python3 test_quota_efficiency.py
```

### Usage Modes
```bash
# Normal mode (quota-optimized, recommended)
python3 youtube_api_fuse.py /srv/youtube

# Force full refresh (troubleshooting)
python3 youtube_api_fuse.py /srv/youtube --full-refresh
```

**📈 Full efficiency guide: [QUOTA_EFFICIENCY.md](QUOTA_EFFICIENCY.md)**

## Usage Examples

### Browse playlist directories
```bash
# List all available playlists
ls /srv/youtube/

# Browse a specific playlist
ls "/srv/youtube/My_Cooking_Playlist/"
```

### Stream with VLC
```bash
# Play a video from a specific playlist
vlc "/srv/youtube/Gaming_Videos/My Favorite Gaming Video.mp4"
```

### Copy to local file (downloads the video)
```bash
cp "/srv/youtube/Music_Playlist/Great Song.mp4" ~/Downloads/
```

### Browse with file manager
```bash
nautilus /srv/youtube/  # Linux - browse playlist directories
open /srv/youtube/      # macOS
```

### Use with media scripts
```bash
# Get video duration from specific playlist
ffprobe "/srv/youtube/Tutorials/Python Tutorial.mp4"

# Create thumbnail
ffmpeg -i "/srv/youtube/Cooking/Recipe Video.mp4" -ss 10 -vframes 1 thumb.jpg
```

## How It Works

1. **Authentication**: Connects to YouTube API using OAuth or API key
2. **Playlist Fetching**: Retrieves video metadata from configured playlists
3. **Virtual Files**: Creates virtual `.mp4` files in the mount directory
4. **Authentic Timestamps**: Sets file modification time to match YouTube publish date
5. **Stream Resolution**: Uses `yt-dlp` to resolve actual video stream URLs
6. **HTTP Proxying**: Forwards read requests to YouTube's servers with range support

### File Timestamps Feature

Videos in the mounted filesystem show their **actual YouTube publish date** as the file modification time. This means:

- `ls -la` shows when the video was originally published on YouTube
- File managers display authentic creation dates
- Media applications can sort by actual publish date
- Backup tools respect original timestamps

```bash
# Example: See real publish dates
ls -la /srv/youtube/Watch\ Later/
# -rw-r--r-- 1 mythtv mythtv 0 Dec 15  2023 My Video.mp4
#                                ^^^^^^^^^^^^^
#                                Actual YouTube publish date
```

## Directory Structure

The filesystem organizes your playlists into a clean directory structure:

```
/srv/youtube/                    # Mount point
├── Watch_Later/                 # Watch Later playlist (if enabled)
│   ├── Video 1.mp4
│   ├── Video 2.mp4
│   └── ...
├── My_Cooking_Playlist/         # Auto-discovered user playlist
│   ├── Recipe Video 1.mp4
│   ├── Recipe Video 2.mp4
│   └── ...
├── Gaming_Videos/               # Another user playlist
│   ├── Game Review 1.mp4
│   ├── Tutorial 1.mp4
│   └── ...
└── Custom_Playlist_Name/        # Custom playlist by ID
    ├── Custom Video 1.mp4
    └── Custom Video 2.mp4
```

### Auto-Discovery
When `auto_discover: true` is set in your config, the filesystem will:
- Automatically find all your YouTube playlists
- Create a subdirectory for each playlist
- Use sanitized playlist names as directory names
- Organize videos within their respective playlist directories

## Troubleshooting

### "Transport endpoint is not connected"
The filesystem crashed. Unmount and restart:
```bash
fusermount -u ./mount-point
python youtube_api_fuse.py ./mount-point
```

### "Permission denied" errors
Make sure your user can access FUSE:
```bash
sudo usermod -a -G fuse $USER
# Logout and login again
```

### Videos won't play
1. Check your API credentials are valid
2. Ensure the playlist is accessible
3. Try a different video quality in config
4. Check internet connection

### Import errors
Run the setup script again:
```bash
./setup.sh
source venv/bin/activate
```

## Security Notes

- **Never commit `client_secrets.json` or `token.json`**
- **Never commit `youtube_config.json` with real API keys**
- API keys and OAuth tokens are cached locally
- All network requests go directly to YouTube (no third-party servers)

## Limitations

- Read-only filesystem (you can't upload or modify videos)
- Requires active internet connection
- YouTube rate limits apply
- Stream URLs expire (handled automatically)
- Linux/macOS only (no Windows FUSE support)

## Distribution & Installation

### For End Users

1. **Download the project**:
   ```bash
   git clone <your-repo-url>
   cd youtube-fuse-project
   ```

2. **Run the installer**:
   ```bash
   ./install.sh
   ```
   
   The installer will:
   - Set up Python virtual environment
   - Install all dependencies
   - Configure systemd service
   - Set up mount point
   - Start the service automatically

3. **Set up credentials** (if not done already):
   - Follow the OAuth setup instructions above
   - Place `client_secrets.json` in the project directory

4. **Access your videos**:
   ```bash
   ls /srv/youtube/  # Default mount point
   ```

### For Developers/Distributors

The project includes template files for easy distribution:

- `youtube-fuse.service.template` - Systemd service template
- `install.sh` - Automated installation script
- `uninstall.sh` - Clean removal script

The installer automatically:
- Detects the current user and system paths
- Creates appropriate systemd service file
- Sets up mount points with correct permissions
- Handles all system integration

### Uninstalling

To remove the YouTube FUSE filesystem:

```bash
./uninstall.sh
```

This will:
- Stop and disable the systemd service
- Unmount the filesystem
- Remove service files
- Optionally clean up mount points

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## License

This project is for educational and personal use. Respect YouTube's Terms of Service.
