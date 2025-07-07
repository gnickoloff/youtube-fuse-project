#!/usr/bin/env python3
"""
Demo Playlist Manager
Provides fake playlist data for testing dashboard functionality
"""

import json
import sys
import os

def get_demo_playlists():
    """Get demo playlists based on actual FUSE mount content"""
    demo_playlists = []
    
    mount_point = '/srv/youtube'
    
    if os.path.exists(mount_point) and os.path.ismount(mount_point):
        try:
            # Get actual directories from the demo FUSE mount
            for item in os.listdir(mount_point):
                item_path = os.path.join(mount_point, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    # Count files in the directory
                    try:
                        files = [f for f in os.listdir(item_path) if f.endswith('.mp4')]
                        demo_playlists.append({
                            'id': f'demo_{item.lower().replace(" ", "_")}',
                            'title': item,
                            'description': f'Demo playlist: {item}',
                            'itemCount': len(files),
                            'enabled': False  # Default to disabled
                        })
                    except:
                        pass
        except Exception as e:
            print(f"Error reading demo mount: {e}", file=sys.stderr)
    
    # Fallback demo playlists if mount not available
    if not demo_playlists:
        demo_playlists = [
            {'id': 'demo_music', 'title': 'Music', 'description': 'Demo music playlist', 'itemCount': 10, 'enabled': False},
            {'id': 'demo_tutorials', 'title': 'Tutorials', 'description': 'Demo tutorial playlist', 'itemCount': 15, 'enabled': False},
            {'id': 'demo_entertainment', 'title': 'Entertainment', 'description': 'Demo entertainment playlist', 'itemCount': 8, 'enabled': False}
        ]
    
    return demo_playlists

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'discover-json':
        playlists = get_demo_playlists()
        result = {
            'playlists': playlists,
            'total_count': len(playlists),
            'demo_mode': True
        }
        print(json.dumps(result, indent=2))
    else:
        playlists = get_demo_playlists()
        print(f"Found {len(playlists)} demo playlists:")
        for playlist in playlists:
            print(f"  - {playlist['title']} ({playlist['itemCount']} videos)")

if __name__ == '__main__':
    main()
