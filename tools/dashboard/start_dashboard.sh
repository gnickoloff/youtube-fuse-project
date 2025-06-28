#!/bin/bash
#
# YouTube FUSE Dashboard Launcher
# Starts the web-based control panel for YouTube FUSE
#

echo "🎥 YouTube FUSE Dashboard Launcher"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install dashboard dependencies if needed
echo "📦 Checking dashboard dependencies..."
pip install -q flask psutil

# Check if config file exists
if [ ! -f "youtube_config.json" ]; then
    echo "⚠️  Configuration file not found. Creating basic config..."
    cat > youtube_config.json << 'EOF'
{
  "api_key": "",
  "client_secrets_file": "client_secrets.json",
  "use_oauth": true,
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
  "refresh_interval": 3600,
  "video_quality": "best[ext=mp4]/best"
}
EOF
    echo "✅ Created basic configuration file"
fi

# Check if we have credentials
CREDS_OK=false

if [ "$YOUTUBE_API_KEY" ]; then
    echo "✅ Found YouTube API key in environment"
    CREDS_OK=true
elif [ -f "client_secrets.json" ]; then
    echo "✅ Found OAuth client secrets file"
    CREDS_OK=true
fi

if [ "$CREDS_OK" = false ]; then
    echo ""
    echo "⚠️  No credentials found!"
    echo "   Either set YOUTUBE_API_KEY environment variable"
    echo "   or place client_secrets.json in this directory"
    echo ""
    echo "   The dashboard will still work for configuration management,"
    echo "   but playlist discovery will not function."
    echo ""
fi

# Get the local IP for easier access
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🚀 Starting YouTube FUSE Dashboard..."
echo ""
echo "   Dashboard will be available at:"
echo "   🌐 Local:   http://localhost:5000"
echo "   🌐 Network: http://$LOCAL_IP:5000"
echo ""
echo "   Press Ctrl+C to stop the dashboard"
echo ""

# Start the dashboard
python3 dashboard.py
