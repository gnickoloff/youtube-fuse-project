#!/usr/bin/env python3
"""
YouTube FUSE Dashboard
Web-based control panel for managing YouTube FUSE filesystem
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import subprocess
import psutil
import time
from datetime import datetime, timedelta
import threading
import pytz

app = Flask(__name__)

class YouTubeFUSEDashboard:
    def __init__(self, config_file='youtube_config.json'):
        self.config_file = config_file
        self.mount_point = '/srv/youtube'
        self.service_name = 'youtube-fuse'
        
    def load_config(self):
        """Load current configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_config(self, config):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_system_status(self):
        """Get system and FUSE status"""
        status = {
            'fuse_mounted': False,
            'service_status': 'unknown',
            'mount_point': self.mount_point,
            'disk_usage': None,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'uptime': None
        }
        
        # Check if FUSE is mounted
        try:
            result = subprocess.run(['mountpoint', '-q', self.mount_point], 
                                  capture_output=True, text=True)
            status['fuse_mounted'] = result.returncode == 0
        except:
            pass
        
        # Check systemd service status
        try:
            result = subprocess.run(['systemctl', 'is-active', self.service_name], 
                                  capture_output=True, text=True)
            status['service_status'] = result.stdout.strip()
        except:
            pass
        
        # Get disk usage of mount point
        if status['fuse_mounted']:
            try:
                stat_info = os.statvfs(self.mount_point)
                total = stat_info.f_frsize * stat_info.f_blocks
                free = stat_info.f_frsize * stat_info.f_bavail
                used = total - free
                status['disk_usage'] = {
                    'total': total,
                    'used': used,
                    'free': free,
                    'percent': (used / total) * 100 if total > 0 else 0
                }
            except:
                pass
        
        # Get system uptime
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                status['uptime'] = str(timedelta(seconds=int(uptime_seconds)))
        except:
            pass
        
        return status
    
    def get_quota_status(self):
        """Get quota status and estimates"""
        config = self.load_config()
        quota_config = config.get('quota_management', {})
        playlist_config = config.get('playlists', {})
        
        # Calculate estimated usage
        max_playlists = playlist_config.get('max_playlists', 10)
        max_videos = playlist_config.get('max_videos_per_playlist', 50)
        refresh_interval = config.get('refresh_interval', 1800)
        
        # Quota cost estimation
        playlist_discovery_cost = max(1, max_playlists // 50)
        playlist_metadata_cost = len(playlist_config.get('custom_playlists', []))
        video_fetch_cost = max_playlists * max(1, max_videos // 50)
        estimated_cost_per_refresh = playlist_discovery_cost + playlist_metadata_cost + video_fetch_cost
        
        daily_refreshes = (24 * 3600) // refresh_interval
        estimated_daily_usage = daily_refreshes * estimated_cost_per_refresh
        
        daily_limit = quota_config.get('daily_quota_limit', 10000)
        
        return {
            'enabled': quota_config.get('enabled', True),
            'daily_limit': daily_limit,
            'rate_limit_delay': quota_config.get('rate_limit_delay', 1.0),
            'emergency_mode': quota_config.get('emergency_mode', False),
            'cache_duration': quota_config.get('cache_duration', 3600),
            'estimated_cost_per_refresh': estimated_cost_per_refresh,
            'estimated_daily_usage': estimated_daily_usage,
            'estimated_percentage': (estimated_daily_usage / daily_limit) * 100 if daily_limit > 0 else 0,
            'daily_refreshes': daily_refreshes,
            'refresh_interval': refresh_interval
        }
    
    def get_playlist_info(self):
        """Get playlist configuration and discovered playlists"""
        config = self.load_config()
        playlist_config = config.get('playlists', {})
        
        # Try to get discovered playlists using the enhanced API
        discovered_playlists = []
        if config.get('use_oauth', False):
            try:
                # Run enhanced playlist manager to get JSON list
                result = subprocess.run(['python3', 'playlist_manager_api.py', 'discover-json'], 
                                      capture_output=True, text=True, cwd='.')
                if result.returncode == 0:
                    playlist_data = json.loads(result.stdout)
                    if not playlist_data.get('error'):
                        discovered_playlists = playlist_data.get('playlists', [])
            except Exception as e:
                print(f"Error getting playlists: {e}")
        
        return {
            'auto_discover': playlist_config.get('auto_discover', False),
            'watch_later': playlist_config.get('watch_later', True),
            'custom_playlists': playlist_config.get('custom_playlists', []),
            'enabled_playlists': playlist_config.get('enabled_playlists', []),
            'max_playlists': playlist_config.get('max_playlists', 10),
            'max_videos_per_playlist': playlist_config.get('max_videos_per_playlist', 50),
            'discovered_playlists': discovered_playlists
        }
    
    def get_file_list(self):
        """Get current files in the FUSE mount"""
        files = []
        if os.path.exists(self.mount_point) and os.path.ismount(self.mount_point):
            try:
                for playlist_dir in os.listdir(self.mount_point):
                    playlist_path = os.path.join(self.mount_point, playlist_dir)
                    if os.path.isdir(playlist_path):
                        playlist_files = []
                        try:
                            for video_file in os.listdir(playlist_path):
                                if video_file.endswith('.mp4'):
                                    file_path = os.path.join(playlist_path, video_file)
                                    stat_info = os.stat(file_path)
                                    playlist_files.append({
                                        'name': video_file,
                                        'size': stat_info.st_size,
                                        'mtime': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                                    })
                        except:
                            pass
                        files.append({
                            'playlist': playlist_dir,
                            'files': playlist_files,
                            'count': len(playlist_files)
                        })
            except:
                pass
        return files

dashboard = YouTubeFUSEDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        'system': dashboard.get_system_status(),
        'quota': dashboard.get_quota_status(),
        'playlists': dashboard.get_playlist_info(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/files')
def api_files():
    """Get file listing"""
    return jsonify(dashboard.get_file_list())

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify(dashboard.load_config())
    
    elif request.method == 'POST':
        try:
            new_config = request.json
            if dashboard.save_config(new_config):
                return jsonify({'success': True, 'message': 'Configuration saved'})
            else:
                return jsonify({'success': False, 'message': 'Failed to save configuration'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/emergency', methods=['POST'])
def api_emergency():
    """Toggle emergency mode"""
    try:
        enable = request.json.get('enable', False)
        config = dashboard.load_config()
        
        if 'quota_management' not in config:
            config['quota_management'] = {}
        
        config['quota_management']['emergency_mode'] = enable
        
        if dashboard.save_config(config):
            return jsonify({
                'success': True, 
                'emergency_mode': enable,
                'message': f"Emergency mode {'enabled' if enable else 'disabled'}"
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update configuration'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/service/<action>')
def api_service(action):
    """Control systemd service"""
    try:
        if action in ['start', 'stop', 'restart']:
            result = subprocess.run(['sudo', 'systemctl', action, dashboard.service_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return jsonify({'success': True, 'message': f'Service {action} successful'})
            else:
                return jsonify({'success': False, 'message': f'Service {action} failed: {result.stderr}'}), 500
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mount/<action>')
def api_mount(action):
    """Control FUSE mount"""
    try:
        if action == 'mount':
            # Start the service instead of mounting directly
            return api_service('start')
        elif action == 'unmount':
            # Stop the service
            return api_service('stop')
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/playlists/discover')
def api_discover_playlists():
    """Discover available playlists"""
    try:
        result = subprocess.run(['python3', 'playlist_manager_api.py', 'discover-json'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            playlist_data = json.loads(result.stdout)
            return jsonify(playlist_data)
        else:
            return jsonify({'error': 'Failed to discover playlists', 'playlists': []}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'playlists': []}), 500

@app.route('/api/playlists/enable', methods=['POST'])
def api_enable_playlist():
    """Enable or disable a specific playlist"""
    try:
        playlist_id = request.json.get('playlist_id')
        enabled = request.json.get('enabled', True)
        
        config = dashboard.load_config()
        if 'playlists' not in config:
            config['playlists'] = {}
        
        enabled_playlists = config['playlists'].get('enabled_playlists', [])
        
        if enabled and playlist_id not in enabled_playlists:
            enabled_playlists.append(playlist_id)
        elif not enabled and playlist_id in enabled_playlists:
            enabled_playlists.remove(playlist_id)
        
        config['playlists']['enabled_playlists'] = enabled_playlists
        
        if dashboard.save_config(config):
            return jsonify({
                'success': True, 
                'message': f"Playlist {'enabled' if enabled else 'disabled'}",
                'enabled_playlists': enabled_playlists
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to save configuration'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    print("Starting YouTube FUSE Dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
