#!/bin/bash
# Example usage script for YouTube FUSE

echo "YouTube FUSE - Example Usage"
echo "============================="
echo ""

# Method 1: Using environment variables (recommended)
echo "Method 1: Environment Variables (Recommended)"
echo "----------------------------------------------"
echo "# For API key authentication:"
echo "export YOUTUBE_API_KEY='AIza-your-api-key-here'"
echo "export YOUTUBE_USE_OAUTH=false"
echo ""
echo "# For OAuth authentication (Watch Later support):"
echo "export YOUTUBE_USE_OAUTH=true"
echo "export YOUTUBE_CLIENT_SECRETS='./client_secrets.json'"
echo ""
echo "# Then run:"
echo "source venv/bin/activate"
echo "python src/youtube_api_fuse.py ./mount-point"
echo ""

# Method 2: Using config file
echo "Method 2: Config File"
echo "--------------------"
echo "# Edit youtube_config.json with your credentials"
echo "# Then run:"
echo "source venv/bin/activate"
echo "python src/youtube_api_fuse.py ./mount-point"
echo ""

# Quick start for API key users
echo "Quick Start (API Key):"
echo "---------------------"
echo "1. Get YouTube Data API key from Google Cloud Console"
echo "2. Run these commands:"
echo ""
echo "   export YOUTUBE_API_KEY='your-api-key-here'"
echo "   export YOUTUBE_USE_OAUTH=false"
echo "   source venv/bin/activate"
echo "   python src/youtube_api_fuse.py ./test-mount"
echo ""
echo "3. In another terminal:"
echo "   ls ./test-mount/"
echo "   vlc './test-mount/My Video.mp4'"
echo ""

echo "Security Notes:"
echo "- Never commit real API keys to git"
echo "- Environment variables are more secure"
echo "- Each person should use their own credentials"
