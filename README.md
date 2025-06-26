# YouTube FUSE Filesystem

A FUSE-based filesystem that mounts YouTube playlists as virtual video files on your local system. Stream videos directly from YouTube through your filesystem!

## Features

- 🎥 Mount YouTube playlists as local directories
- 📺 Stream videos directly without downloading
- 🔐 Support for both public playlists (API key) and private playlists (OAuth)
- ⚡ Smart caching for better performance
- 🎬 Watch Later playlist support
- 📱 HTTP range requests for video seeking
- 🔄 Auto-refresh playlist contents
- 📅 Authentic file timestamps (YouTube publish dates)

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

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `api_key` | YouTube Data API key | `"AIza..."`  |
| `use_oauth` | Use OAuth instead of API key | `true`/`false` |
| `watch_later` | Include Watch Later playlist | `true`/`false` |
| `custom_playlists` | List of playlist IDs to mount | `["PLxxx", "PLyyy"]` |
| `refresh_interval` | Seconds between playlist updates | `300` |
| `video_quality` | yt-dlp format selector | `"best[ext=mp4]/best"` |

## Usage Examples

### Stream with VLC
```bash
vlc "./mount-point/[WL] My Favorite Video.mp4"
```

### Copy to local file (downloads the video)
```bash
cp "./mount-point/My Video.mp4" ~/Downloads/
```

### Browse with file manager
```bash
nautilus ./mount-point/  # Linux
open ./mount-point/      # macOS
```

### Use with media scripts
```bash
# Get video duration
ffprobe "./mount-point/My Video.mp4"

# Create thumbnail
ffmpeg -i "./mount-point/My Video.mp4" -ss 10 -vframes 1 thumb.jpg
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
