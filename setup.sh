#!/bin/bash

echo "Setting up YouTube FUSE project..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create mount point for testing
mkdir -p ./test-mount

# Create config from template if it doesn't exist
if [ ! -f youtube_config.json ]; then
    echo "Creating default config file..."
    cat > youtube_config.json << 'EOF'
{
  "api_key": "YOUR_YOUTUBE_API_KEY_HERE",
  "client_secrets_file": "client_secrets.json",
  "use_oauth": true,
  "playlists": {
    "watch_later": true,
    "custom_playlists": [
      "PLrAXtmRdnEQy6nuLMfO6uiyzVb7x_u0Tg"
    ]
  },
  "refresh_interval": 300,
  "video_quality": "best[ext=mp4]/best"
}
EOF
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit youtube_config.json with your YouTube API credentials"
echo "2. If using Watch Later, download client_secrets.json from Google Cloud Console"
echo "3. Test with: python youtube_api_fuse.py ./test-mount"
echo "4. Check ./test-mount directory for virtual video files"
