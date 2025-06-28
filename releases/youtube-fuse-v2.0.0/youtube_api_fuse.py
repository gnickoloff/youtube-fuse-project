#!/usr/bin/env python3

import os
import sys
import errno
import stat
import threading
import time
import json
from datetime import datetime, timedelta
from fuse import FUSE, FuseOSError, Operations
import yt_dlp
import requests
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pytz

class YouTubeAPIFUSE(Operations):
    def __init__(self, config_file='youtube_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.youtube_service = None
        self.playlists = {}  # Cache playlist metadata {playlist_id: {title, sanitized_name, videos}}
        self.videos = {}  # Cache video metadata by playlist (DEPRECATED - now in playlists)
        self.stream_cache = {}  # Cache stream URLs temporarily
        self.cache_lock = threading.Lock()
        self.last_refresh = 0
        self.refresh_interval = self.config.get('refresh_interval', 1800)
        
        # Quota management initialization
        self.quota_usage = 0
        self.api_call_count = 0
        self.last_api_call = 0
        self.quota_reset_time = time.time() + 86400  # Default to 24 hours from now
        
        # Now set the proper quota reset time
        try:
            self.quota_reset_time = self.get_next_quota_reset()
        except Exception as e:
            print(f"Warning: Could not set quota reset time: {e}")
            # Fall back to midnight today
            self.quota_reset_time = time.time() + (86400 - (time.time() % 86400))
        
        self.authenticate()
        self.refresh_videos()
    
    def load_config(self):
        """Load configuration from JSON file and environment variables"""
        default_config = {
            "api_key": "",  # For public playlists only
            "client_secrets_file": "client_secrets.json",  # For OAuth (Watch Later)
            "use_oauth": True,  # Set to False for API key only
            "playlists": {
                "auto_discover": False,  # Auto-discover all user playlists
                "watch_later": True,  # Special case
                "custom_playlists": [],  # List of playlist IDs
                "enabled_playlists": [],  # Specific playlist IDs to enable (empty = all)
                "max_playlists": 10,  # Maximum number of playlists to fetch
                "max_videos_per_playlist": 50  # Maximum videos per playlist
            },
            "quota_management": {
                "enabled": True,  # Enable quota management features
                "daily_quota_limit": 10000,  # Conservative daily quota limit
                "rate_limit_delay": 1.0,  # Seconds between API calls
                "quota_reset_hour": 0,  # Hour when quota resets (0-23, PST)
                "emergency_mode": False,  # Disable all API calls if quota exceeded
                "cache_duration": 3600  # How long to cache data (seconds)
            },
            "refresh_interval": 1800,  # 30 minutes (increased from 5)
            "video_quality": "best[ext=mp4]/best"
        }
        
        # Try to load config file
        config = default_config.copy()
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
                # Merge file config with defaults
                for key, value in file_config.items():
                    config[key] = value
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Creating template...")
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Template config created: {self.config_file}")
        
        # Override with environment variables (these take priority)
        env_api_key = os.environ.get('YOUTUBE_API_KEY')
        if env_api_key:
            config['api_key'] = env_api_key
            print("✓ Using API key from environment variable")
        
        env_secrets_file = os.environ.get('YOUTUBE_CLIENT_SECRETS')
        if env_secrets_file:
            config['client_secrets_file'] = env_secrets_file
            print(f"✓ Using client secrets from: {env_secrets_file}")
        
        env_use_oauth = os.environ.get('YOUTUBE_USE_OAUTH')
        if env_use_oauth:
            config['use_oauth'] = env_use_oauth.lower() in ('true', '1', 'yes')
            print(f"✓ OAuth mode set to: {config['use_oauth']}")
        
        # Validate credentials are available
        if config['use_oauth']:
            if not os.path.exists(config['client_secrets_file']):
                print(f"\n❌ OAuth enabled but client secrets file not found: {config['client_secrets_file']}")
                print("Either:")
                print("1. Download client_secrets.json from Google Cloud Console")
                print("2. Set YOUTUBE_CLIENT_SECRETS environment variable")
                print("3. Set use_oauth=false in config to use API key instead")
                sys.exit(1)
        else:
            if not config['api_key']:
                print(f"\n❌ API key authentication selected but no API key found!")
                print("Either:")
                print("1. Set YOUTUBE_API_KEY environment variable")
                print("2. Add api_key to your config file")
                print("3. Set use_oauth=true to use OAuth instead")
                sys.exit(1)
        
        return config
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        if self.config['use_oauth']:
            self.authenticate_oauth()
        else:
            self.authenticate_api_key()
    
    def authenticate_oauth(self):
        """OAuth authentication for private playlists (Watch Later)"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        creds = None
        
        # Load existing credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.config['client_secrets_file']):
                    print(f"OAuth client secrets file {self.config['client_secrets_file']} not found!")
                    print("Download it from Google Cloud Console > APIs & Services > Credentials")
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config['client_secrets_file'], SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.youtube_service = build('youtube', 'v3', credentials=creds)
        print("✅ OAuth authentication successful")
    
    def authenticate_api_key(self):
        """API key authentication for public playlists only"""
        if not self.config['api_key']:
            print("❌ API key not configured!")
            print("Set it with: export YOUTUBE_API_KEY='your-key-here'")
            sys.exit(1)
        
        self.youtube_service = build('youtube', 'v3', developerKey=self.config['api_key'])
        print("✅ API key authentication successful")
    
    def get_next_quota_reset(self):
        """Calculate when the YouTube API quota resets (daily at configured hour)"""
        # YouTube API quota resets at midnight PST
        pst = pytz.timezone('US/Pacific')
        now = datetime.now(pst)
        reset_hour = self.config.get('quota_management', {}).get('quota_reset_hour', 0)
        
        # Calculate next reset time
        next_reset = now.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
        if now.hour >= reset_hour:
            next_reset += timedelta(days=1)
        
        return next_reset.timestamp()
    
    def check_quota_limit(self, required_quota=1):
        """Check if we can make an API call without exceeding quota"""
        quota_config = self.config.get('quota_management', {})
        
        if not quota_config.get('enabled', True):
            return True
        
        # Reset quota usage if we've passed the reset time
        current_time = time.time()
        if current_time >= self.quota_reset_time:
            self.quota_usage = 0
            self.api_call_count = 0
            self.quota_reset_time = self.get_next_quota_reset()
            print(f"🔄 Quota reset! New reset time: {datetime.fromtimestamp(self.quota_reset_time)}")
        
        # Check if we're in emergency mode
        if quota_config.get('emergency_mode', False):
            print("🚨 Emergency mode enabled - API calls disabled")
            return False
        
        # Check daily quota limit
        daily_limit = quota_config.get('daily_quota_limit', 10000)
        if self.quota_usage + required_quota > daily_limit:
            print(f"⚠️ Quota limit reached: {self.quota_usage}/{daily_limit}")
            return False
        
        return True
    
    def rate_limit_api_call(self):
        """Implement rate limiting between API calls"""
        quota_config = self.config.get('quota_management', {})
        rate_limit = quota_config.get('rate_limit_delay', 1.0)
        
        if rate_limit > 0:
            current_time = time.time()
            time_since_last_call = current_time - self.last_api_call
            
            if time_since_last_call < rate_limit:
                sleep_time = rate_limit - time_since_last_call
                print(f"⏱️ Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_api_call = time.time()
    
    def track_quota_usage(self, operation_type, quota_cost=1):
        """Track quota usage for monitoring"""
        self.quota_usage += quota_cost
        self.api_call_count += 1
        
        quota_config = self.config.get('quota_management', {})
        daily_limit = quota_config.get('daily_quota_limit', 10000)
        
        print(f"📊 API Call: {operation_type} (Cost: {quota_cost}) - "
              f"Usage: {self.quota_usage}/{daily_limit} ({self.api_call_count} calls)")
        
        # Warn if getting close to limit
        if self.quota_usage > daily_limit * 0.8:
            print(f"⚠️ Warning: Using {(self.quota_usage/daily_limit)*100:.1f}% of daily quota")
    
    def make_api_call(self, operation_type, api_call_func, quota_cost=1):
        """Wrapper for YouTube API calls with quota management"""
        if not self.check_quota_limit(quota_cost):
            print(f"❌ Skipping {operation_type} - quota limit reached")
            return None
        
        try:
            self.rate_limit_api_call()
            result = api_call_func()
            self.track_quota_usage(operation_type, quota_cost)
            return result
        except Exception as e:
            print(f"❌ API call failed for {operation_type}: {e}")
            # Still count the quota usage even on failure
            self.track_quota_usage(f"{operation_type} (failed)", quota_cost)
            return None
    
    def get_user_playlists(self):
        """Auto-discover all user playlists with quota management"""
        if not self.config['use_oauth']:
            print("Auto-discovery requires OAuth authentication")
            return []

        playlist_config = self.config.get('playlists', {})
        max_playlists = playlist_config.get('max_playlists', 10)
        enabled_playlists = playlist_config.get('enabled_playlists', [])
        
        playlists = []
        next_page_token = None
        fetched_count = 0

        try:
            while True:
                def api_call():
                    return self.youtube_service.playlists().list(
                        part='snippet',
                        mine=True,
                        maxResults=min(50, max_playlists - fetched_count),
                        pageToken=next_page_token
                    ).execute()

                response = self.make_api_call("get_user_playlists", api_call, quota_cost=1)
                if not response:
                    break

                for playlist in response['items']:
                    playlist_id = playlist['id']
                    
                    # If enabled_playlists is specified, only include those
                    if enabled_playlists and playlist_id not in enabled_playlists:
                        continue
                    
                    playlists.append({
                        'id': playlist_id,
                        'title': playlist['snippet']['title'],
                        'description': playlist['snippet'].get('description', ''),
                        'itemCount': playlist['snippet'].get('itemCount', 0)
                    })
                    
                    fetched_count += 1
                    if fetched_count >= max_playlists:
                        print(f"🛑 Reached max playlists limit: {max_playlists}")
                        return playlists

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

        except Exception as e:
            print(f"Error fetching user playlists: {e}")

        print(f"📋 Discovered {len(playlists)} playlists (max: {max_playlists})")
        return playlists

    def get_watch_later_playlist(self):
        """Get Watch Later playlist items"""
        if not self.config['use_oauth']:
            print("Watch Later requires OAuth authentication")
            return []
        
        try:
            # Get the user's playlists to find Watch Later
            playlists_response = self.youtube_service.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            ).execute()
            
            watch_later_id = None
            for playlist in playlists_response['items']:
                if playlist['snippet']['title'] == 'Watch Later':
                    watch_later_id = playlist['id']
                    break
            
            if not watch_later_id:
                # Try the standard Watch Later playlist ID
                watch_later_id = 'WL'
            
            return self.get_playlist_videos(watch_later_id)
            
        except Exception as e:
            print(f"Error fetching Watch Later: {e}")
            return []
    
    def get_playlist_videos(self, playlist_id):
        """Get videos from a specific playlist with quota management"""
        playlist_config = self.config.get('playlists', {})
        max_videos = playlist_config.get('max_videos_per_playlist', 50)
        
        videos = []
        next_page_token = None
        fetched_count = 0
        
        try:
            while True:
                def api_call():
                    return self.youtube_service.playlistItems().list(
                        part='snippet',
                        playlistId=playlist_id,
                        maxResults=min(50, max_videos - fetched_count),
                        pageToken=next_page_token
                    ).execute()

                response = self.make_api_call(f"get_playlist_videos({playlist_id})", api_call, quota_cost=1)
                if not response:
                    break

                for item in response['items']:
                    if item['snippet']['resourceId']['kind'] == 'youtube#video':
                        video_id = item['snippet']['resourceId']['videoId']
                        title = item['snippet']['title']
                        
                        # Skip deleted/private videos
                        if title != 'Deleted video' and title != 'Private video':
                            videos.append({
                                'id': video_id,
                                'title': title,
                                'url': f'https://youtube.com/watch?v={video_id}',
                                'publishedAt': item['snippet'].get('publishedAt')
                            })
                            
                            fetched_count += 1
                            if fetched_count >= max_videos:
                                print(f"🛑 Reached max videos limit for playlist {playlist_id}: {max_videos}")
                                return videos

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except Exception as e:
            print(f"Error fetching playlist {playlist_id}: {e}")
        
        print(f"📺 Fetched {len(videos)} videos from playlist {playlist_id} (max: {max_videos})")
        return videos

    def refresh_videos(self):
        """Fetch all configured playlists and build video cache with quota management"""
        current_time = time.time()
        quota_config = self.config.get('quota_management', {})
        cache_duration = quota_config.get('cache_duration', 3600)
        
        # Use cache duration from quota config if available
        effective_refresh_interval = min(self.refresh_interval, cache_duration)
        
        if current_time - self.last_refresh < effective_refresh_interval:
            return  # Too soon to refresh

        # Check if we're in emergency mode
        if quota_config.get('emergency_mode', False):
            print("🚨 Emergency mode enabled - skipping video refresh")
            return

        print("🔄 Refreshing videos from YouTube API...")
        print(f"📊 Current quota usage: {self.quota_usage}/{quota_config.get('daily_quota_limit', 10000)}")
        
        new_playlists = {}
        playlist_config = self.config.get('playlists', {})

        # Auto-discover user playlists if enabled
        if playlist_config.get('auto_discover', False):
            print("🔍 Auto-discovering user playlists...")
            user_playlists = self.get_user_playlists()
            
            for playlist in user_playlists:
                playlist_id = playlist['id']
                playlist_title = playlist['title']
                sanitized_name = self.sanitize_filename(playlist_title)
                
                print(f"📋 Fetching auto-discovered playlist: {playlist_title}")
                playlist_videos = self.get_playlist_videos(playlist_id)
                
                new_playlists[playlist_id] = {
                    'title': playlist_title,
                    'sanitized_name': sanitized_name,
                    'videos': {}
                }
                
                for video in playlist_videos:
                    filename = f"{self.sanitize_filename(video['title'])}.mp4"
                    new_playlists[playlist_id]['videos'][filename] = self.create_video_entry(video)

        # Get Watch Later if configured
        if playlist_config.get('watch_later', True):
            print("📺 Fetching Watch Later playlist...")
            watch_later_videos = self.get_watch_later_playlist()
            playlist_id = 'watch_later'
            
            new_playlists[playlist_id] = {
                'title': 'Watch Later',
                'sanitized_name': 'Watch_Later',
                'videos': {}
            }
            
            for video in watch_later_videos:
                filename = f"{self.sanitize_filename(video['title'])}.mp4"
                new_playlists[playlist_id]['videos'][filename] = self.create_video_entry(video)

        # Get custom playlists
        custom_playlists = playlist_config.get('custom_playlists', [])
        enabled_playlists = playlist_config.get('enabled_playlists', [])
        
        for playlist_id in custom_playlists:
            # Skip if enabled_playlists is specified and this isn't in it
            if enabled_playlists and playlist_id not in enabled_playlists:
                print(f"⏭️ Skipping disabled playlist: {playlist_id}")
                continue
                
            print(f"📋 Fetching custom playlist {playlist_id}...")
            
            # Get playlist metadata first
            def get_metadata():
                return self.youtube_service.playlists().list(
                    part='snippet',
                    id=playlist_id
                ).execute()
            
            try:
                playlist_response = self.make_api_call(f"get_playlist_metadata({playlist_id})", get_metadata, quota_cost=1)
                
                if playlist_response and playlist_response['items']:
                    playlist_title = playlist_response['items'][0]['snippet']['title']
                else:
                    playlist_title = f"Playlist_{playlist_id}"
            except Exception as e:
                print(f"Error getting playlist metadata for {playlist_id}: {e}")
                playlist_title = f"Playlist_{playlist_id}"
            
            sanitized_name = self.sanitize_filename(playlist_title)
            playlist_videos = self.get_playlist_videos(playlist_id)
            
            new_playlists[playlist_id] = {
                'title': playlist_title,
                'sanitized_name': sanitized_name,
                'videos': {}
            }
            
            for video in playlist_videos:
                filename = f"{self.sanitize_filename(video['title'])}.mp4"
                new_playlists[playlist_id]['videos'][filename] = self.create_video_entry(video)

        # Update playlist cache
        with self.cache_lock:
            self.playlists = new_playlists
            self.last_refresh = current_time

        total_videos = sum(len(playlist['videos']) for playlist in new_playlists.values())
        print(f"✅ Loaded {len(new_playlists)} playlists with {total_videos} total videos")
        print(f"📊 Final quota usage: {self.quota_usage}/{quota_config.get('daily_quota_limit', 10000)}")
    
    def create_video_entry(self, video_data):
        """Create a video cache entry with YouTube publish date as mtime"""
        # Extract YouTube publish date for authentic timestamps
        mtime = time.time()  # Default to current time
        if 'publishedAt' in video_data:
            try:
                # Parse ISO 8601 timestamp from YouTube API
                published_dt = datetime.fromisoformat(video_data['publishedAt'].replace('Z', '+00:00'))
                mtime = published_dt.timestamp()
                print(f"Using publish date {video_data['publishedAt']} for {video_data['title'][:50]}...")
            except Exception as e:
                print(f"Error parsing publish date for {video_data['title']}: {e}")
        
        return {
            'id': video_data['id'],
            'title': video_data['title'],
            'url': video_data['url'],
            'size': 100 * 1024 * 1024,  # Default 100MB estimate
            'mtime': mtime,
        }
    
    def sanitize_filename(self, title):
        """Convert video title to safe filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        
        if len(title) > 80:  # Leave room for prefix
            title = title[:80]
            
        return title
    
    def get_stream_url(self, video_id):
        """Get fresh stream URL for video (cached for 30 minutes)"""
        cache_key = video_id
        current_time = time.time()
        
        with self.cache_lock:
            if cache_key in self.stream_cache:
                cached_data = self.stream_cache[cache_key]
                if current_time - cached_data['timestamp'] < 1800:  # 30 minutes
                    return cached_data['url']
        
        # Extract fresh URL using yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': self.config['video_quality'],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://youtube.com/watch?v={video_id}', download=False)
                
                stream_url = None
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('url') and fmt.get('ext') == 'mp4':
                            stream_url = fmt['url']
                            break
                
                if not stream_url and info.get('url'):
                    stream_url = info['url']
                
                if stream_url:
                    with self.cache_lock:
                        self.stream_cache[cache_key] = {
                            'url': stream_url,
                            'timestamp': current_time
                        }
                    return stream_url
                    
        except Exception as e:
            print(f"Error extracting stream URL for {video_id}: {e}")
            
        return None
     # FUSE Operations
    def getattr(self, path, fh=None):
        """Get file/directory attributes"""
        # Refresh videos if needed
        self.refresh_videos()

        if path == '/':
            # Root directory
            st = dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)
        else:
            path_parts = path.strip('/').split('/')
            
            if len(path_parts) == 1:
                # This is a playlist directory
                playlist_dir = path_parts[0]
                
                # Check if this matches any playlist's sanitized name
                playlist_found = False
                for playlist_id, playlist_data in self.playlists.items():
                    if playlist_data['sanitized_name'] == playlist_dir:
                        playlist_found = True
                        break
                
                if playlist_found:
                    st = dict(st_mode=(stat.S_IFDIR | 0o755), st_nlink=2)
                else:
                    raise FuseOSError(errno.ENOENT)
                    
            elif len(path_parts) == 2:
                # This is a video file within a playlist directory
                playlist_dir = path_parts[0]
                filename = path_parts[1]
                
                # Find the playlist
                target_playlist = None
                for playlist_id, playlist_data in self.playlists.items():
                    if playlist_data['sanitized_name'] == playlist_dir:
                        target_playlist = playlist_data
                        break
                
                if target_playlist and filename in target_playlist['videos']:
                    video = target_playlist['videos'][filename]
                    st = dict(
                        st_mode=(stat.S_IFREG | 0o644),
                        st_nlink=1,
                        st_size=video['size'],
                        st_mtime=video['mtime'],
                        st_atime=video['mtime'],
                        st_ctime=video['mtime']
                    )
                else:
                    raise FuseOSError(errno.ENOENT)
            else:
                raise FuseOSError(errno.ENOENT)

        st['st_uid'] = os.getuid()
        st['st_gid'] = os.getgid()
        return st

    def readdir(self, path, fh):
        """List directory contents"""
        self.refresh_videos()

        if path == '/':
            # Root directory - list all playlist directories
            playlist_dirs = [playlist_data['sanitized_name'] 
                           for playlist_data in self.playlists.values()]
            return ['.', '..'] + playlist_dirs
        else:
            path_parts = path.strip('/').split('/')
            
            if len(path_parts) == 1:
                # This is a playlist directory - list videos
                playlist_dir = path_parts[0]
                
                # Find the playlist
                for playlist_id, playlist_data in self.playlists.items():
                    if playlist_data['sanitized_name'] == playlist_dir:
                        return ['.', '..'] + list(playlist_data['videos'].keys())
                
                raise FuseOSError(errno.ENOENT)
            else:
                raise FuseOSError(errno.ENOENT)
    
    def open(self, path, flags):
        """Open file for reading"""
        path_parts = path.strip('/').split('/')
        
        if len(path_parts) != 2:
            raise FuseOSError(errno.ENOENT)
            
        playlist_dir = path_parts[0]
        filename = path_parts[1]
        
        # Find the playlist and check if file exists
        for playlist_id, playlist_data in self.playlists.items():
            if playlist_data['sanitized_name'] == playlist_dir:
                if filename in playlist_data['videos']:
                    return hash(path) % 1000000
                break
        
        raise FuseOSError(errno.ENOENT)
    
    def read(self, path, length, offset, fh):
        """Read data from file"""
        path_parts = path.strip('/').split('/')
        
        if len(path_parts) != 2:
            raise FuseOSError(errno.ENOENT)
            
        playlist_dir = path_parts[0]
        filename = path_parts[1]
        
        # Find the playlist and video
        video = None
        for playlist_id, playlist_data in self.playlists.items():
            if playlist_data['sanitized_name'] == playlist_dir:
                if filename in playlist_data['videos']:
                    video = playlist_data['videos'][filename]
                    break
        
        if not video:
            raise FuseOSError(errno.ENOENT)
        
        stream_url = self.get_stream_url(video['id'])
        
        if not stream_url:
            raise FuseOSError(errno.EIO)
        
        try:
            headers = {'Range': f'bytes={offset}-{offset + length - 1}'}
            response = requests.get(stream_url, headers=headers, stream=True, timeout=30)
            
            if response.status_code in [200, 206]:
                return response.content
            else:
                raise FuseOSError(errno.EIO)
                
        except Exception as e:
            print(f"Error reading {path}: {e}")
            raise FuseOSError(errno.EIO)

def main():
    if len(sys.argv) != 2:
        print("Usage: python youtube_api_fuse.py <mount_point>")
        print("\nMake sure you have configured youtube_config.json first!")
        sys.exit(1)
    
    mount_point = sys.argv[1]
    
    print(f"Mounting YouTube API filesystem at {mount_point}")
    
    os.makedirs(mount_point, exist_ok=True)
    
    try:
        fuse = FUSE(YouTubeAPIFUSE(), mount_point, nothreads=True, foreground=True, allow_other=True)
    except KeyboardInterrupt:
        print("\nUnmounting...")

if __name__ == '__main__':
    main()