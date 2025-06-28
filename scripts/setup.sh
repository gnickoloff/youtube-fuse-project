#!/bin/bash

echo "Setting up YouTube FUSE project..."

# Check if FUSE is installed
if ! command -v fusermount &> /dev/null; then
    echo "❌ FUSE is not installed!"
    echo "Please install FUSE first:"
    echo "  Ubuntu/Debian: sudo apt install fuse libfuse-dev"
    echo "  CentOS/RHEL:   sudo yum install fuse fuse-devel"
    echo "  macOS:         Install macFUSE from https://osxfuse.github.io/"
    exit 1
fi

# Check Python version
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null; then
    echo "❌ Python 3.7+ is required!"
    echo "Current version: $(python3 --version 2>/dev/null || echo 'Not found')"
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create mount point for testing
mkdir -p ./test-mount

# Create example config file (template)
if [ ! -f youtube_config.example.json ]; then
    echo "📝 Creating example config file..."
    cat > youtube_config.example.json << 'EOF'
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

# Only create actual config if it doesn't exist
if [ ! -f youtube_config.json ]; then
    echo "📝 Creating default config file..."
    cp youtube_config.example.json youtube_config.json
fi

echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Get YouTube API credentials from Google Cloud Console"
echo "2. Edit youtube_config.json with your API key/OAuth settings"
echo "3. If using OAuth, download client_secrets.json"
echo "4. Test with: source venv/bin/activate && python youtube_api_fuse.py ./test-mount"
echo ""
echo "📖 See README.md for detailed setup instructions"
