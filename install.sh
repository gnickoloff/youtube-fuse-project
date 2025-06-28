#!/bin/bash
# Backward compatibility wrapper for the reorganized project structure
echo "⚠️  Note: Scripts have been moved to scripts/ directory"
echo "🔄 Running: scripts/install.sh $@"
echo ""
exec ./scripts/install.sh "$@"
