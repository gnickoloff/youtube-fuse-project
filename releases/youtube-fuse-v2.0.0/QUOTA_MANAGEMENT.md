# YouTube API Quota Management Guide

Your YouTube FUSE project now includes comprehensive quota management to prevent hitting API limits and crashing. This guide shows you how to manage quotas, control traffic, and configure which playlists to retrieve.

## Quick Start - Emergency Mode

If you're currently hitting quota limits and need immediate relief:

```bash
# IMMEDIATELY stop all API calls
./quota_control.sh emergency-on

# When you're ready to resume (with lower limits)
./quota_control.sh minimal          # Apply minimal settings
./quota_control.sh emergency-off    # Re-enable API calls
```

## Current Configuration

Check your current quota status:

```bash
./quota_control.sh status
```

Example output:
```
📊 YouTube API Quota Configuration
==================================================
Daily Quota Limit: 5000
Rate Limit Delay: 2.0s
Cache Duration: 7200s
Quota Management: Enabled
Emergency Mode: OFF

📈 Estimated Quota Usage
==================================================
Max Playlists: 3
Max Videos per Playlist: 15
Estimated Cost per Refresh: 4 units
Estimated Daily Refreshes: 1250
Current Refresh Interval: 3600s (60min)
Scheduled Daily Refreshes: 24
Estimated Daily Usage: 96 units (1.9%)
```

## Preset Configurations

### Conservative Settings (Recommended)
Uses 70% of your quota safely:
```bash
./quota_control.sh conservative
```

### Minimal Settings (Quota Recovery)
Very low quota usage for when you're near limits:
```bash
./quota_control.sh minimal
```

### Watch Later Only
Only fetch your Watch Later playlist:
```bash
./quota_control.sh watch-later-only
```

## Manual Configuration

### Set Quota Limits
```bash
./quota_control.sh set-limit 8000        # Set daily quota limit
./quota_control.sh set-playlists 5       # Max playlists to fetch
./quota_control.sh set-videos 25         # Max videos per playlist
./quota_control.sh set-delay 2.0         # Rate limit delay (seconds)
```

### Playlist Discovery Control
```bash
./quota_control.sh auto-discover-off     # Disable auto-discovery
./quota_control.sh auto-discover-on      # Enable auto-discovery
```

## Playlist Management

### List Available Playlists
```bash
python3 playlist_manager.py list
```

### Enable Specific Playlists
```bash
# Show current config
python3 playlist_manager.py config

# Enable specific playlists by ID
python3 playlist_manager.py enable PLrAXtmRdnEQy6nuLMfO6uiyzVb7x_u0Tg
python3 playlist_manager.py enable PLother_playlist_id_here

# Disable a playlist
python3 playlist_manager.py disable PLrAXtmRdnEQy6nuLMfO6uiyzVb7x_u0Tg

# Clear all enabled playlists
python3 playlist_manager.py clear
```

## Understanding Quota Costs

YouTube API operations have different costs:
- **List playlists**: 1 unit per request (50 playlists per request)
- **Get playlist items**: 1 unit per request (50 videos per request)  
- **Get playlist metadata**: 1 unit per playlist

### Example Calculation
- 5 playlists with 25 videos each = ~3 units per refresh
- Refreshing every hour = 24 refreshes per day
- Daily usage = 72 units (well under 10,000 limit)

## Configuration File Reference

Your `youtube_config.json` supports these quota-related settings:

```json
{
  "playlists": {
    "auto_discover": false,
    "watch_later": true,
    "custom_playlists": ["PLplaylist_id_here"],
    "enabled_playlists": ["PLspecific_id_1", "PLspecific_id_2"],
    "max_playlists": 5,
    "max_videos_per_playlist": 25
  },
  "quota_management": {
    "enabled": true,
    "daily_quota_limit": 8000,
    "rate_limit_delay": 1.5,
    "quota_reset_hour": 0,
    "emergency_mode": false,
    "cache_duration": 3600
  },
  "refresh_interval": 1800
}
```

### Configuration Options Explained

#### Playlist Settings
- `auto_discover`: Automatically find all your playlists
- `watch_later`: Include your Watch Later playlist
- `custom_playlists`: Specific playlist IDs to always include
- `enabled_playlists`: When set, ONLY these playlists are fetched (overrides auto_discover)
- `max_playlists`: Maximum number of playlists to fetch
- `max_videos_per_playlist`: Maximum videos per playlist

#### Quota Management
- `enabled`: Enable/disable quota management features
- `daily_quota_limit`: Conservative daily quota limit (default API limit is 10,000)
- `rate_limit_delay`: Seconds to wait between API calls
- `quota_reset_hour`: Hour when quota resets (0-23, PST timezone)
- `emergency_mode`: When true, disables ALL API calls
- `cache_duration`: How long to cache data before refreshing

#### General Settings
- `refresh_interval`: How often to refresh video list (seconds)

## Monitoring and Optimization

### Check Optimization Suggestions
```bash
./quota_control.sh optimize
```

### Monitor Real-time Usage
The filesystem logs quota usage in real-time:
```
📊 API Call: get_user_playlists (Cost: 1) - Usage: 3/5000 (3 calls)
⏱️ Rate limiting: sleeping 1.5s
```

### Warning System
You'll get warnings when approaching limits:
```
⚠️ Warning: Using 85.2% of daily quota
```

## Troubleshooting

### If You Hit Quota Limits
1. **Immediate**: `./quota_control.sh emergency-on`
2. **Reduce load**: `./quota_control.sh minimal`
3. **Re-enable**: `./quota_control.sh emergency-off`
4. **Monitor**: `./quota_control.sh status`

### Common Issues

**"Quota limit reached" messages**
- The system is working correctly, preventing API overuse
- Use emergency mode and reduce settings

**Videos not updating**
- Check if emergency mode is enabled: `./quota_control.sh status`
- Increase refresh_interval to reduce quota usage

**Too many playlists**
- Use `python3 playlist_manager.py list` to see all playlists
- Enable only specific ones with `enabled_playlists`
- Turn off auto_discover: `./quota_control.sh auto-discover-off`

## Best Practices

1. **Start Conservative**: Use `./quota_control.sh conservative` initially
2. **Monitor Usage**: Check `./quota_control.sh status` regularly  
3. **Use Specific Playlists**: Instead of auto-discovery, enable only what you need
4. **Emergency Preparedness**: Know how to quickly enable emergency mode
5. **Cache Duration**: Longer cache duration = less API calls
6. **Rate Limiting**: Higher delays = more stable operation

## Example Workflows

### New User Setup
```bash
# Start with conservative settings
./quota_control.sh conservative

# See what playlists are available
python3 playlist_manager.py list

# Enable only specific ones you want
python3 playlist_manager.py clear
python3 playlist_manager.py enable PLyour_playlist_id_here

# Turn off auto-discovery to save quota
./quota_control.sh auto-discover-off

# Check final status
./quota_control.sh status
```

### Quota Recovery
```bash
# Immediate stop
./quota_control.sh emergency-on

# Apply minimal settings
./quota_control.sh minimal

# Check what this gives you
./quota_control.sh status

# Re-enable when ready
./quota_control.sh emergency-off
```

### High-Use Setup (if you have quota to spare)
```bash
# Increase limits
./quota_control.sh set-limit 9000
./quota_control.sh set-playlists 10
./quota_control.sh set-videos 50

# Enable auto-discovery
./quota_control.sh auto-discover-on

# Check estimated usage
./quota_control.sh status
```
