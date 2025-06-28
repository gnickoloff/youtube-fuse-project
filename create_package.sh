#!/bin/bash

# Create a distributable package for YouTube FUSE

echo "Creating distributable package..."

# Create package directory
PACKAGE_NAME="youtube-fuse-$(date +%Y%m%d)"
mkdir -p "dist/$PACKAGE_NAME"

# Copy essential files
cp youtube_api_fuse.py "dist/$PACKAGE_NAME/"
cp requirements.txt "dist/$PACKAGE_NAME/"
cp setup.sh "dist/$PACKAGE_NAME/"
cp README.md "dist/$PACKAGE_NAME/"
cp youtube_config.example.json "dist/$PACKAGE_NAME/"
cp .gitignore "dist/$PACKAGE_NAME/"

# Make setup script executable
chmod +x "dist/$PACKAGE_NAME/setup.sh"

# Create archive
cd dist
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"
cd ..

echo "✅ Package created: dist/$PACKAGE_NAME.tar.gz"
echo ""
echo "To distribute:"
echo "1. Share the .tar.gz file"
echo "2. Recipients should extract and run: ./setup.sh"
echo "3. They'll need to get their own YouTube API credentials"
