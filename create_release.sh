#!/bin/bash

# YouTube FUSE Filesystem v1.1.0 Release Package Creator

echo "🎉 Creating YouTube FUSE Filesystem v1.1.0 Release Package..."

VERSION="1.1.0"
RELEASE_NAME="youtube-fuse-v${VERSION}"
RELEASE_DATE=$(date +%Y-%m-%d)

# Create release directory
mkdir -p "releases/$RELEASE_NAME"

echo "📦 Packaging distribution files..."

# Copy all distribution files
cp youtube_api_fuse.py "releases/$RELEASE_NAME/"
cp requirements.txt "releases/$RELEASE_NAME/"
cp setup.sh "releases/$RELEASE_NAME/"
cp README.md "releases/$RELEASE_NAME/"
cp PREREQUISITES.md "releases/$RELEASE_NAME/"
cp CHANGELOG.md "releases/$RELEASE_NAME/"
cp youtube_config.example.json "releases/$RELEASE_NAME/"
cp .gitignore "releases/$RELEASE_NAME/"
cp install.sh "releases/$RELEASE_NAME/"
cp uninstall.sh "releases/$RELEASE_NAME/"
cp usage_examples.sh "releases/$RELEASE_NAME/"
cp youtube-fuse.service.template "releases/$RELEASE_NAME/"
cp package.json "releases/$RELEASE_NAME/"

# Make scripts executable
chmod +x "releases/$RELEASE_NAME/setup.sh"
chmod +x "releases/$RELEASE_NAME/install.sh"
chmod +x "releases/$RELEASE_NAME/uninstall.sh"
chmod +x "releases/$RELEASE_NAME/usage_examples.sh"

# Create release info
cat > "releases/$RELEASE_NAME/RELEASE_INFO.txt" << EOF
YouTube FUSE Filesystem v${VERSION}
Release Date: ${RELEASE_DATE}
Git Tag: v${VERSION}

🕒 AUTHENTIC TIMESTAMP SUPPORT! 🕒

This release adds authentic YouTube publish date support as file timestamps.
Enhanced metadata accuracy for better media library organization.

QUICK START:
1. Extract this package
2. Run: ./install.sh
3. Follow the setup prompts
4. Access your YouTube library at /srv/youtube

NEW FEATURES (v1.1.0):
✅ File timestamps reflect actual YouTube publish dates
✅ Enhanced metadata accuracy for media organization
✅ Better integration with backup tools and media applications
✅ Authentic file attributes that match original content timeline

CORE FEATURES:
✅ Mount YouTube playlists as virtual video files
✅ OAuth authentication for private playlists
✅ Auto-discovery of all user playlists
✅ Systemd service integration
✅ HTPC optimization (MythTV support)
✅ Professional installer/uninstaller
✅ Secure credential management
✅ Cross-platform FUSE support

REQUIREMENTS:
- Linux/macOS with FUSE support
- Python 3.7+
- sudo access for installation

For detailed information, see README.md and PREREQUISITES.md

Repository: https://github.com/your-username/youtube-fuse-project
EOF

echo "📁 Creating archives..."

# Create tar.gz archive
cd releases
tar -czf "${RELEASE_NAME}.tar.gz" "$RELEASE_NAME"

# Create zip archive  
zip -r "${RELEASE_NAME}.zip" "$RELEASE_NAME" >/dev/null

cd ..

# Create checksums
cd releases
sha256sum "${RELEASE_NAME}.tar.gz" > "${RELEASE_NAME}.tar.gz.sha256"
sha256sum "${RELEASE_NAME}.zip" > "${RELEASE_NAME}.zip.sha256"
cd ..

echo "✅ Release v${VERSION} created successfully!"
echo ""
echo "📦 Release files:"
echo "   releases/${RELEASE_NAME}.tar.gz"
echo "   releases/${RELEASE_NAME}.zip"
echo "   releases/${RELEASE_NAME}.tar.gz.sha256"
echo "   releases/${RELEASE_NAME}.zip.sha256"
echo ""
echo "🚀 Ready for distribution!"
echo ""
echo "Next steps:"
echo "1. Test the release package on a clean system"
echo "2. Push git tag: git push origin v${VERSION}"
echo "3. Create GitHub release with these archives"
echo "4. Update documentation with release notes"
echo ""
echo "🎯 v${VERSION} includes authentic YouTube publish date timestamps for enhanced media organization!"
