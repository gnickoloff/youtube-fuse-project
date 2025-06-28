# YouTube FUSE - Quota Management Tools Summary

You now have comprehensive tools to manage YouTube API quotas and prevent crashes:

## 🛠️ Available Tools

### 1. Quota Control Script (`./quota_control.sh`)
**Quick quota management commands:**

```bash
# Status and monitoring
./quota_control.sh status                    # Show current quota configuration
./quota_control.sh optimize                  # Get optimization suggestions

# Emergency controls
./quota_control.sh emergency-on              # STOP all API calls immediately
./quota_control.sh emergency-off             # Resume API calls

# Preset configurations
./quota_control.sh conservative              # Safe settings (70% quota usage)
./quota_control.sh minimal                   # Very low quota usage
./quota_control.sh watch-later-only          # Only Watch Later playlist

# Manual controls
./quota_control.sh set-limit 8000            # Set daily quota limit
./quota_control.sh set-playlists 5           # Max playlists to fetch
./quota_control.sh set-videos 25             # Max videos per playlist
./quota_control.sh set-delay 2.0             # Rate limit delay
./quota_control.sh auto-discover-off         # Disable auto-discovery
```

### 2. Playlist Manager (`python3 playlist_manager.py`)
**Control which playlists to fetch:**

```bash
# Discovery and listing
python3 playlist_manager.py list             # List all available playlists
python3 playlist_manager.py config           # Show current configuration

# Enable/disable specific playlists
python3 playlist_manager.py enable PLxxx     # Enable specific playlist
python3 playlist_manager.py disable PLxxx    # Disable specific playlist
python3 playlist_manager.py clear            # Clear all enabled playlists
```

### 3. Quota Manager (`python3 quota_manager.py`)
**Advanced quota monitoring:**

```bash
python3 quota_manager.py --status            # Detailed quota status
python3 quota_manager.py --optimize          # Optimization suggestions
python3 quota_manager.py --emergency-on      # Enable emergency mode
python3 quota_manager.py --emergency-off     # Disable emergency mode
```

## 🚨 Emergency Response

If you're currently hitting quota limits:

### Step 1: Immediate Stop
```bash
./quota_control.sh emergency-on
```
This immediately disables ALL YouTube API calls.

### Step 2: Apply Conservative Settings
```bash
./quota_control.sh minimal
```
This sets very low quota usage parameters.

### Step 3: Check Configuration
```bash
./quota_control.sh status
```
Verify the new settings and estimated usage.

### Step 4: Resume Operations
```bash
./quota_control.sh emergency-off
```
Re-enable API calls with the new limits.

## 📊 Current Configuration

Your current settings (very conservative to prevent quota issues):

- **Daily Quota Limit**: 5,000 (out of 10,000 API default)
- **Max Playlists**: 3
- **Max Videos per Playlist**: 15
- **Rate Limit Delay**: 2.0 seconds
- **Refresh Interval**: 3600 seconds (1 hour)
- **Cache Duration**: 7200 seconds (2 hours)
- **Estimated Daily Usage**: ~96 units (1.9% of quota)

## 🎯 Optimization Strategies

### For Low Quota Usage
```bash
./quota_control.sh watch-later-only         # Only fetch Watch Later
./quota_control.sh set-videos 10            # Reduce videos per playlist
./quota_control.sh set-delay 5.0            # Increase rate limiting
```

### For Specific Playlists Only
```bash
./quota_control.sh auto-discover-off        # Turn off auto-discovery
python3 playlist_manager.py list            # See available playlists
python3 playlist_manager.py clear           # Clear all enabled playlists
python3 playlist_manager.py enable PLxxx    # Enable only what you need
```

### For Maximum Performance (if you have quota to spare)
```bash
./quota_control.sh conservative             # Apply conservative preset
./quota_control.sh set-limit 9000           # Use 90% of quota
./quota_control.sh set-playlists 10         # More playlists
```

## 🔄 Real-time Monitoring

The filesystem now logs quota usage in real-time:

```
📊 API Call: get_user_playlists (Cost: 1) - Usage: 3/5000 (3 calls)
⏱️ Rate limiting: sleeping 2.0s
⚠️ Warning: Using 85.2% of daily quota
```

## 📖 Documentation

- **[QUOTA_MANAGEMENT.md](QUOTA_MANAGEMENT.md)** - Complete quota management guide
- **[README.md](README.md)** - Main project documentation
- **[PREREQUISITES.md](PREREQUISITES.md)** - Installation requirements

## 🎛️ Configuration File Structure

Your `youtube_config.json` now supports these quota controls:

```json
{
  "playlists": {
    "auto_discover": false,
    "watch_later": true,
    "custom_playlists": [],
    "enabled_playlists": [],
    "max_playlists": 3,
    "max_videos_per_playlist": 15
  },
  "quota_management": {
    "enabled": true,
    "daily_quota_limit": 5000,
    "rate_limit_delay": 2.0,
    "quota_reset_hour": 0,
    "emergency_mode": false,
    "cache_duration": 7200
  },
  "refresh_interval": 3600
}
```

This quota management system should prevent any future crashes from API quota exhaustion while giving you fine-grained control over which playlists to fetch and how much API quota to use.
