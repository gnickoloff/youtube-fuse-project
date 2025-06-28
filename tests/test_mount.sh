#!/bin/bash

# Test script for YouTube FUSE mounting
echo "🔧 YouTube FUSE Mount Test"
echo "=========================="

MOUNT_POINT="/srv/youtube"

echo "📁 Checking mount point: $MOUNT_POINT"

# Check if mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    echo "❌ Mount point does not exist, creating..."
    sudo mkdir -p "$MOUNT_POINT"
fi

# Check current permissions
echo "📋 Current permissions:"
ls -la "$MOUNT_POINT"

# Set proper ownership and permissions
echo "🔧 Setting ownership to mythtv:mythtv..."
sudo chown mythtv:mythtv "$MOUNT_POINT"
sudo chmod 2775 "$MOUNT_POINT"

echo "📋 New permissions:"
ls -la "$MOUNT_POINT"

# Check if anything is mounted
echo "🔍 Current mounts:"
mount | grep "$MOUNT_POINT" || echo "Nothing mounted at $MOUNT_POINT"

# Test basic directory operations
echo "🧪 Testing directory operations..."
if [ -w "$MOUNT_POINT" ]; then
    echo "✅ Mount point is writable"
else
    echo "❌ Mount point is not writable"
fi

echo ""
echo "💡 To mount YouTube FUSE:"
echo "   cd /home/gnicko/Development/youtube-fuse-project"
echo "   python3 youtube_api_fuse.py $MOUNT_POINT"
