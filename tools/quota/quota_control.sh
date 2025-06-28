#!/bin/bash
#
# YouTube FUSE Quota Control Script
# Quick controls for managing quota limits and playlist configuration
#

CONFIG_FILE="youtube_config.json"

show_help() {
    echo "YouTube FUSE Quota Control"
    echo "========================="
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  status                    Show current quota status"
    echo "  emergency-on              Enable emergency mode (disable all API calls)"
    echo "  emergency-off             Disable emergency mode"
    echo "  set-limit <number>        Set daily quota limit"
    echo "  set-playlists <number>    Set max playlists"
    echo "  set-videos <number>       Set max videos per playlist"
    echo "  set-delay <seconds>       Set rate limit delay"
    echo "  conservative              Apply conservative settings (70% quota usage)"
    echo "  minimal                   Apply minimal settings (very low quota usage)"
    echo "  optimize                  Show optimization suggestions"
    echo "  watch-later-only          Only fetch Watch Later playlist"
    echo "  auto-discover-off         Disable auto-discovery of playlists"
    echo "  auto-discover-on          Enable auto-discovery of playlists"
    echo ""
}

update_config() {
    local key="$1"
    local value="$2"
    
    # Use python to update JSON safely
    python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

# Navigate nested keys
keys = '$key'.split('.')
current = config
for k in keys[:-1]:
    if k not in current:
        current[k] = {}
    current = current[k]

# Set the value
last_key = keys[-1]
if '$value' in ['true', 'false']:
    current[last_key] = '$value' == 'true'
elif '$value'.isdigit():
    current[last_key] = int('$value')
elif '.' in '$value' and all(part.isdigit() for part in '$value'.split('.')):
    current[last_key] = float('$value')
else:
    current[last_key] = '$value'

with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Updated $key = $value"
    else
        echo "❌ Failed to update configuration"
        exit 1
    fi
}

case "$1" in
    "status")
        python3 quota_manager.py --status
        ;;
    "emergency-on")
        python3 quota_manager.py --emergency-on
        ;;
    "emergency-off")
        python3 quota_manager.py --emergency-off
        ;;
    "set-limit")
        if [ -z "$2" ]; then
            echo "Error: Please specify quota limit number"
            exit 1
        fi
        update_config "quota_management.daily_quota_limit" "$2"
        ;;
    "set-playlists")
        if [ -z "$2" ]; then
            echo "Error: Please specify max playlists number"
            exit 1
        fi
        update_config "playlists.max_playlists" "$2"
        ;;
    "set-videos")
        if [ -z "$2" ]; then
            echo "Error: Please specify max videos per playlist number"
            exit 1
        fi
        update_config "playlists.max_videos_per_playlist" "$2"
        ;;
    "set-delay")
        if [ -z "$2" ]; then
            echo "Error: Please specify delay in seconds"
            exit 1
        fi
        update_config "quota_management.rate_limit_delay" "$2"
        ;;
    "conservative")
        echo "Applying conservative settings..."
        update_config "quota_management.daily_quota_limit" "8000"
        update_config "playlists.max_playlists" "5"
        update_config "playlists.max_videos_per_playlist" "25"
        update_config "quota_management.rate_limit_delay" "1.5"
        update_config "refresh_interval" "1800"
        echo "✅ Applied conservative settings"
        ;;
    "minimal")
        echo "Applying minimal settings..."
        update_config "quota_management.daily_quota_limit" "3000"
        update_config "playlists.max_playlists" "2"
        update_config "playlists.max_videos_per_playlist" "10"
        update_config "quota_management.rate_limit_delay" "3.0"
        update_config "refresh_interval" "3600"
        echo "✅ Applied minimal settings"
        ;;
    "optimize")
        python3 quota_manager.py --optimize
        ;;
    "watch-later-only")
        echo "Configuring for Watch Later only..."
        update_config "playlists.auto_discover" "false"
        update_config "playlists.watch_later" "true"
        update_config "playlists.custom_playlists" "[]"
        update_config "playlists.max_playlists" "1"
        update_config "playlists.max_videos_per_playlist" "50"
        echo "✅ Configured for Watch Later only"
        ;;
    "auto-discover-off")
        update_config "playlists.auto_discover" "false"
        echo "Auto-discovery disabled. Add specific playlist IDs to custom_playlists if needed."
        ;;
    "auto-discover-on")
        update_config "playlists.auto_discover" "true"
        echo "Auto-discovery enabled. Will fetch all user playlists."
        ;;
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
