#!/usr/bin/env python3
"""
YouTube FUSE Playlist Manager
Tool for discovering, enabling, and managing playlists
"""

import json
import sys
import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def load_config(config_file='youtube_config.json'):
    """Load configuration file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {config_file} not found")
        return None

def save_config(config, config_file='youtube_config.json'):
    """Save configuration file"""
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def get_youtube_service(config):
    """Get authenticated YouTube service"""
    if not config['use_oauth']:
        print("❌ OAuth required for playlist discovery")
        return None
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        print("❌ No valid OAuth credentials found. Run the main application first.")
        return None
    
    return build('youtube', 'v3', credentials=creds)

def discover_playlists(youtube_service):
    """Discover all user playlists"""
    playlists = []
    next_page_token = None
    
    try:
        while True:
            request = youtube_service.playlists().list(
                part='snippet,contentDetails',
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for playlist in response['items']:
                playlists.append({
                    'id': playlist['id'],
                    'title': playlist['snippet']['title'],
                    'description': playlist['snippet'].get('description', ''),
                    'itemCount': playlist['contentDetails'].get('itemCount', 0),
                    'publishedAt': playlist['snippet'].get('publishedAt', '')
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
    except Exception as e:
        print(f"❌ Error fetching playlists: {e}")
    
    return playlists

def list_playlists():
    """List all available playlists"""
    config = load_config()
    if not config:
        return
    
    youtube_service = get_youtube_service(config)
    if not youtube_service:
        return
    
    print("🔍 Discovering your playlists...")
    playlists = discover_playlists(youtube_service)
    
    if not playlists:
        print("No playlists found")
        return
    
    enabled_playlists = config.get('playlists', {}).get('enabled_playlists', [])
    custom_playlists = config.get('playlists', {}).get('custom_playlists', [])
    
    print(f"\n📋 Found {len(playlists)} playlists:")
    print("=" * 80)
    
    for i, playlist in enumerate(playlists, 1):
        status_icons = []
        
        if playlist['id'] in enabled_playlists:
            status_icons.append("✅ ENABLED")
        elif playlist['id'] in custom_playlists:
            status_icons.append("📌 CUSTOM")
        else:
            status_icons.append("⭕ AVAILABLE")
        
        status = " ".join(status_icons)
        
        print(f"{i:2d}. {status}")
        print(f"    ID: {playlist['id']}")
        print(f"    Title: {playlist['title']}")
        print(f"    Videos: {playlist['itemCount']}")
        if playlist['description']:
            desc = playlist['description'][:60] + "..." if len(playlist['description']) > 60 else playlist['description']
            print(f"    Description: {desc}")
        print()

def enable_playlist(playlist_id):
    """Enable a specific playlist"""
    config = load_config()
    if not config:
        return
    
    if 'playlists' not in config:
        config['playlists'] = {}
    
    if 'enabled_playlists' not in config['playlists']:
        config['playlists']['enabled_playlists'] = []
    
    if playlist_id not in config['playlists']['enabled_playlists']:
        config['playlists']['enabled_playlists'].append(playlist_id)
        
        if save_config(config):
            print(f"✅ Enabled playlist: {playlist_id}")
        else:
            print(f"❌ Failed to enable playlist: {playlist_id}")
    else:
        print(f"ℹ️  Playlist already enabled: {playlist_id}")

def disable_playlist(playlist_id):
    """Disable a specific playlist"""
    config = load_config()
    if not config:
        return
    
    enabled_playlists = config.get('playlists', {}).get('enabled_playlists', [])
    
    if playlist_id in enabled_playlists:
        enabled_playlists.remove(playlist_id)
        config['playlists']['enabled_playlists'] = enabled_playlists
        
        if save_config(config):
            print(f"✅ Disabled playlist: {playlist_id}")
        else:
            print(f"❌ Failed to disable playlist: {playlist_id}")
    else:
        print(f"ℹ️  Playlist not enabled: {playlist_id}")

def clear_enabled():
    """Clear all enabled playlists"""
    config = load_config()
    if not config:
        return
    
    if 'playlists' not in config:
        config['playlists'] = {}
    
    config['playlists']['enabled_playlists'] = []
    
    if save_config(config):
        print("✅ Cleared all enabled playlists")
    else:
        print("❌ Failed to clear enabled playlists")

def show_current_config():
    """Show current playlist configuration"""
    config = load_config()
    if not config:
        return
    
    playlist_config = config.get('playlists', {})
    
    print("📋 Current Playlist Configuration")
    print("=" * 50)
    print(f"Auto-discover: {playlist_config.get('auto_discover', False)}")
    print(f"Watch Later: {playlist_config.get('watch_later', False)}")
    print(f"Max Playlists: {playlist_config.get('max_playlists', 10)}")
    print(f"Max Videos per Playlist: {playlist_config.get('max_videos_per_playlist', 50)}")
    
    enabled = playlist_config.get('enabled_playlists', [])
    custom = playlist_config.get('custom_playlists', [])
    
    if enabled:
        print(f"\nEnabled Playlists ({len(enabled)}):")
        for playlist_id in enabled:
            print(f"  - {playlist_id}")
    else:
        print("\nEnabled Playlists: None")
    
    if custom:
        print(f"\nCustom Playlists ({len(custom)}):")
        for playlist_id in custom:
            print(f"  - {playlist_id}")
    else:
        print("\nCustom Playlists: None")

def main():
    if len(sys.argv) < 2:
        print("YouTube FUSE Playlist Manager")
        print("============================")
        print()
        print("Usage: python3 playlist_manager.py <command> [options]")
        print()
        print("Commands:")
        print("  list                    List all available playlists")
        print("  config                  Show current configuration")
        print("  enable <playlist_id>    Enable a specific playlist")
        print("  disable <playlist_id>   Disable a specific playlist") 
        print("  clear                   Clear all enabled playlists")
        print()
        print("Examples:")
        print("  python3 playlist_manager.py list")
        print("  python3 playlist_manager.py enable PLrAXtmRdnEQy6nuLMfO6uiyzVb7x_u0Tg")
        print("  python3 playlist_manager.py disable PLrAXtmRdnEQy6nuLMfO6uiyzVb7x_u0Tg")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_playlists()
    elif command == "config":
        show_current_config()
    elif command == "enable":
        if len(sys.argv) < 3:
            print("❌ Please specify playlist ID")
            return
        enable_playlist(sys.argv[2])
    elif command == "disable":
        if len(sys.argv) < 3:
            print("❌ Please specify playlist ID")
            return
        disable_playlist(sys.argv[2])
    elif command == "clear":
        clear_enabled()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()
