#!/usr/bin/env python3
"""
Enhanced Playlist Manager for Dashboard Integration
Provides JSON output for web dashboard
"""

import json
import sys
import os
import argparse
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def load_config(config_file='youtube_config.json'):
    """Load configuration file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_youtube_service(config):
    """Get authenticated YouTube service"""
    if not config.get('use_oauth', False):
        return None
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        return None
    
    return build('youtube', 'v3', credentials=creds)

def discover_playlists_json():
    """Discover playlists and return JSON"""
    config = load_config()
    youtube_service = get_youtube_service(config)
    
    if not youtube_service:
        return json.dumps({
            'error': 'No valid OAuth credentials found',
            'playlists': []
        })
    
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
                    'publishedAt': playlist['snippet'].get('publishedAt', ''),
                    'thumbnails': playlist['snippet'].get('thumbnails', {}),
                    'enabled': playlist['id'] in config.get('playlists', {}).get('enabled_playlists', [])
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'playlists': playlists
        })
    
    return json.dumps({
        'error': None,
        'playlists': playlists,
        'total': len(playlists)
    })

def main():
    parser = argparse.ArgumentParser(description='Enhanced YouTube Playlist Manager')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('command', nargs='?', help='Command to execute')
    
    args = parser.parse_args()
    
    if args.json or (args.command == 'discover-json'):
        print(discover_playlists_json())
    else:
        # Fall back to original playlist manager behavior
        import playlist_manager
        playlist_manager.main()

if __name__ == '__main__':
    main()
