# YouTube FUSE Dashboard

A beautiful web-based control panel for managing your YouTube FUSE filesystem.

## Features

🎛️ **System Control**
- Mount/unmount FUSE filesystem
- Start/stop/restart systemd service
- Real-time system status monitoring
- CPU and memory usage tracking

📊 **Quota Management**
- Visual quota usage display
- Emergency mode toggle
- Preset configurations (minimal, conservative)
- Real-time quota tracking

📋 **Playlist Management**
- Discover all your YouTube playlists
- Enable/disable specific playlists
- Configure playlist and video limits
- Auto-discovery controls

⚙️ **Configuration**
- Edit all settings through web interface
- Apply changes instantly
- Save/restore configurations
- Real-time validation

📂 **File Browser**
- Browse mounted YouTube videos
- See file sizes and dates
- Organized by playlist folders

## Quick Start

1. **Install Dependencies**
   ```bash
   source venv/bin/activate
   pip install flask psutil
   ```

2. **Launch Dashboard**
   ```bash
   ./start_dashboard.sh
   ```

3. **Access Dashboard**
   - Local: http://localhost:5000
   - Network: http://YOUR_IP:5000

## Dashboard Sections

### 🖥️ System Status
- **FUSE Mount**: Shows if filesystem is mounted
- **Service**: Shows systemd service status
- **CPU/Memory**: Real-time usage monitoring
- **Controls**: Mount, unmount, restart service

### 📊 Quota Management
- **Daily Limit**: Current quota limit setting
- **Usage Bar**: Estimated daily usage percentage
- **Rate Limit**: Delay between API calls
- **Emergency Mode**: ON/OFF status
- **Quick Actions**:
  - Emergency Stop (immediate API shutdown)
  - Minimal Settings (very low quota usage)
  - Conservative Settings (balanced usage)

### 📋 Playlist Management
- **Auto-discover**: Toggle automatic playlist discovery
- **Watch Later**: Include Watch Later playlist
- **Limits**: Set max playlists and videos per playlist
- **Playlist Discovery**: 
  - Click "Discover Playlists" to find all playlists
  - Toggle individual playlists on/off
  - See playlist details (video count, description)

### ⚙️ Configuration
- **Refresh Interval**: How often to update video lists
- **Rate Limit Delay**: Seconds between API calls
- **Daily Quota Limit**: Maximum API calls per day
- **Apply Changes**: Save all modifications

### 📂 File Browser
- Shows current mounted videos organized by playlist
- Displays file sizes and modification dates
- Updates automatically when files change

## Emergency Procedures

### If Quota Exhausted
1. Click **Emergency Stop** button immediately
2. Select **Minimal Settings** preset
3. Wait for quota reset (midnight PST)
4. Re-enable with conservative settings

### If Service Won't Start
1. Check **System Status** section
2. Try **Restart Service** button
3. Check mount point permissions
4. Verify credentials are configured

### If Playlists Won't Load
1. Verify OAuth credentials exist (`token.json`)
2. Check quota isn't exhausted
3. Ensure auto-discovery is enabled
4. Try manual playlist discovery

## Configuration Tips

### Low Quota Usage
- Set **Max Playlists**: 2-3
- Set **Max Videos**: 10-15
- Set **Rate Delay**: 3.0 seconds
- Set **Refresh Interval**: 3600 seconds (1 hour)
- Use **enabled_playlists** instead of auto-discovery

### High Performance
- Set **Max Playlists**: 10+
- Set **Max Videos**: 50+
- Set **Rate Delay**: 1.0 seconds
- Set **Refresh Interval**: 1800 seconds (30 min)
- Enable auto-discovery

### Quota Recovery
1. Enable **Emergency Mode**
2. Apply **Minimal Settings**
3. Disable auto-discovery
4. Enable only 1-2 specific playlists
5. Wait for quota reset

## Troubleshooting

### Dashboard Won't Start
```bash
# Check if dependencies installed
source venv/bin/activate
pip list | grep -E "(flask|psutil)"

# Install if missing
pip install flask psutil

# Check if port 5000 is available
netstat -tlnp | grep :5000
```

### Playlist Discovery Fails
```bash
# Check OAuth credentials
ls -la token.json client_secrets.json

# Test playlist manager directly
python3 playlist_manager_api.py discover-json
```

### API Calls Failing
1. Check Emergency Mode is OFF
2. Verify quota hasn't been exhausted
3. Check rate limiting isn't too aggressive
4. Verify credentials are valid

## Advanced Usage

### Running on Different Port
```bash
# Edit dashboard.py, change last line:
app.run(host='0.0.0.0', port=8080, debug=False)
```

### Remote Access
The dashboard binds to `0.0.0.0` so it's accessible from other machines on your network. Access via:
```
http://YOUR_SERVER_IP:5000
```

### Security Considerations
- Dashboard has no authentication
- Only run on trusted networks
- Consider using a reverse proxy with authentication
- Don't expose port 5000 to the internet

### API Endpoints
The dashboard provides a REST API:
- `GET /api/status` - System and quota status
- `GET /api/files` - File listing
- `GET /api/config` - Current configuration
- `POST /api/config` - Update configuration
- `POST /api/emergency` - Toggle emergency mode
- `GET /api/playlists/discover` - Discover playlists
- `POST /api/playlists/enable` - Enable/disable playlist

## Integration

The dashboard can be integrated with other tools:

```bash
# Get status as JSON
curl http://localhost:5000/api/status

# Toggle emergency mode
curl -X POST http://localhost:5000/api/emergency \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'

# Update configuration
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d @youtube_config.json
```

This dashboard provides a complete graphical interface for managing your YouTube FUSE system without needing to remember command-line tools or edit configuration files manually.
