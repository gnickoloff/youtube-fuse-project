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

class YouTubeDemoFUSE(Operations):
    def __init__(self, config_file='youtube_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.playlists = {}  # Cache playlist metadata
        self.cache_lock = threading.Lock()
        
        # Create demo playlists to test permissions
        self.create_demo_playlists()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "filesystem": {
                "uid": 121,  # mythtv user ID
                "gid": 130,  # mythtv group ID
                "dir_mode": 0o2775,  # rwxrwsr-x with setgid bit
                "file_mode": 0o664   # rw-rw-r--
            }
        }
        
        # Try to load config file
        config = default_config.copy()
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
                # Merge file config with defaults
                for key, value in file_config.items():
                    if key in config:
                        config[key] = value
        except FileNotFoundError:
            print(f"Using default config (no {self.config_file} found)")
        
        return config
    
    def create_demo_playlists(self):
        """Create demo playlists to test filesystem permissions"""
        current_time = time.time()
        
        # Demo playlist 1
        self.playlists['demo1'] = {
            'title': 'Demo Playlist 1',
            'sanitized_name': 'Demo_Playlist_1',
            'videos': {
                'Sample_Video_1.mp4': {
                    'id': 'demo1',
                    'title': 'Sample Video 1',
                    'url': 'https://www.youtube.com/watch?v=demo1',
                    'size': 50 * 1024 * 1024,  # 50MB
                    'mtime': current_time - 3600,  # 1 hour ago
                },
                'Sample_Video_2.mp4': {
                    'id': 'demo2',
                    'title': 'Sample Video 2',
                    'url': 'https://www.youtube.com/watch?v=demo2',
                    'size': 75 * 1024 * 1024,  # 75MB
                    'mtime': current_time - 7200,  # 2 hours ago
                }
            }
        }
        
        # Demo playlist 2
        self.playlists['demo2'] = {
            'title': 'Watch Later Demo',
            'sanitized_name': 'Watch_Later_Demo',
            'videos': {
                'Another_Video.mp4': {
                    'id': 'demo3',
                    'title': 'Another Video',
                    'url': 'https://www.youtube.com/watch?v=demo3',
                    'size': 100 * 1024 * 1024,  # 100MB
                    'mtime': current_time - 1800,  # 30 minutes ago
                }
            }
        }
        
        print(f"✅ Created {len(self.playlists)} demo playlists for testing")

    # FUSE Operations
    def getattr(self, path, fh=None):
        """Get file/directory attributes with proper permissions"""
        if path == '/':
            # Root directory with setgid bit (rwxrwsr-x = 2775)
            filesystem_config = self.config.get('filesystem', {})
            dir_mode = filesystem_config.get('dir_mode', 0o2775)
            st = dict(st_mode=(stat.S_IFDIR | dir_mode), st_nlink=2)
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
                    filesystem_config = self.config.get('filesystem', {})
                    dir_mode = filesystem_config.get('dir_mode', 0o2775)
                    st = dict(st_mode=(stat.S_IFDIR | dir_mode), st_nlink=2)
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
                    filesystem_config = self.config.get('filesystem', {})
                    file_mode = filesystem_config.get('file_mode', 0o664)
                    st = dict(
                        st_mode=(stat.S_IFREG | file_mode),
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

        # Set ownership to mythtv:mythtv
        filesystem_config = self.config.get('filesystem', {})
        st['st_uid'] = filesystem_config.get('uid', 121)
        st['st_gid'] = filesystem_config.get('gid', 130)
        return st

    def readdir(self, path, fh):
        """List directory contents"""
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
        """Read data from file - return demo content"""
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
        
        # Return demo content (repeating pattern)
        demo_content = f"DEMO VIDEO CONTENT FOR {video['title']}\n".encode() * 1000
        
        # Handle range request
        if offset >= len(demo_content):
            return b''
        
        end = min(offset + length, len(demo_content))
        return demo_content[offset:end]

    # Write operations (read-only filesystem)
    def write(self, path, data, offset, fh):
        raise FuseOSError(errno.EROFS)
    
    def truncate(self, path, length, fh=None):
        raise FuseOSError(errno.EROFS)
    
    def chmod(self, path, mode):
        raise FuseOSError(errno.EROFS)
    
    def chown(self, path, uid, gid):
        raise FuseOSError(errno.EROFS)
    
    def utimens(self, path, times=None):
        raise FuseOSError(errno.EROFS)
    
    def create(self, path, mode, fi=None):
        raise FuseOSError(errno.EROFS)
    
    def mkdir(self, path, mode):
        raise FuseOSError(errno.EROFS)
    
    def rmdir(self, path):
        raise FuseOSError(errno.EROFS)
    
    def unlink(self, path):
        raise FuseOSError(errno.EROFS)
    
    def rename(self, old, new):
        raise FuseOSError(errno.EROFS)
    
    def link(self, target, source):
        raise FuseOSError(errno.EROFS)
    
    def symlink(self, target, source):
        raise FuseOSError(errno.EROFS)
    
    def flush(self, path, fh):
        return 0
    
    def release(self, path, fh):
        return 0
    
    def fsync(self, path, datasync, fh):
        return 0
    
    def access(self, path, mode):
        # Allow read access, deny write access
        if mode & os.W_OK:
            raise FuseOSError(errno.EACCES)
        return 0

    def statfs(self, path):
        """Get filesystem statistics"""
        return dict(
            f_bsize=4096,
            f_frsize=4096,
            f_blocks=1000000,
            f_bfree=0,
            f_bavail=0,
            f_files=100000,
            f_ffree=0,
            f_favail=0,
            f_flag=0,
            f_namemax=255
        )

def main():
    if len(sys.argv) != 2:
        print("Usage: python youtube_demo_fuse.py <mount_point>")
        print("\nThis is a demo version that doesn't require YouTube API quota.")
        print("It creates fake playlists to test filesystem permissions.")
        sys.exit(1)
    
    mount_point = sys.argv[1]
    
    print(f"🔧 Mounting YouTube Demo FUSE at {mount_point}")
    print("📺 This demo version creates fake playlists to test permissions")
    print("🚫 No YouTube API quota required!")
    
    os.makedirs(mount_point, exist_ok=True)
    
    try:
        fuse_system = YouTubeDemoFUSE()
        
        mount_options = {
            'nothreads': True,
            'foreground': True,
            'allow_other': True,
            'default_permissions': False,
            'ro': False,
            'big_writes': True,
            'max_read': 131072,
        }
        
        print(f"🔧 Mount options: {mount_options}")
        fuse = FUSE(fuse_system, mount_point, **mount_options)
    except KeyboardInterrupt:
        print("\nUnmounting...")

if __name__ == '__main__':
    main()
