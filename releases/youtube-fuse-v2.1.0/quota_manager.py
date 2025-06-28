#!/usr/bin/env python3
"""
YouTube FUSE Quota Manager
Utility script for monitoring and managing YouTube API quotas
"""

import json
import sys
import argparse
from datetime import datetime
import pytz

def load_config(config_file='youtube_config.json'):
    """Load configuration file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {config_file} not found")
        return None

def show_quota_status(config):
    """Display current quota configuration and estimated usage"""
    quota_config = config.get('quota_management', {})
    playlist_config = config.get('playlists', {})
    
    print("📊 YouTube API Quota Configuration")
    print("=" * 50)
    
    # Quota limits
    daily_limit = quota_config.get('daily_quota_limit', 10000)
    print(f"Daily Quota Limit: {daily_limit}")
    print(f"Rate Limit Delay: {quota_config.get('rate_limit_delay', 1.0)}s")
    print(f"Cache Duration: {quota_config.get('cache_duration', 3600)}s")
    print(f"Quota Management: {'Enabled' if quota_config.get('enabled', True) else 'Disabled'}")
    print(f"Emergency Mode: {'ON' if quota_config.get('emergency_mode', False) else 'OFF'}")
    
    # Estimate quota usage
    print("\n📈 Estimated Quota Usage")
    print("=" * 50)
    
    max_playlists = playlist_config.get('max_playlists', 10)
    max_videos_per_playlist = playlist_config.get('max_videos_per_playlist', 50)
    
    # Quota costs (approximate):
    # - List playlists: 1 unit per request (50 playlists per request)
    # - List playlist items: 1 unit per request (50 items per request)
    # - Get playlist metadata: 1 unit per playlist
    
    playlist_discovery_cost = max(1, max_playlists // 50)
    playlist_metadata_cost = len(playlist_config.get('custom_playlists', []))
    video_fetch_cost = max_playlists * max(1, max_videos_per_playlist // 50)
    
    estimated_cost = playlist_discovery_cost + playlist_metadata_cost + video_fetch_cost
    
    print(f"Max Playlists: {max_playlists}")
    print(f"Max Videos per Playlist: {max_videos_per_playlist}")
    print(f"Estimated Cost per Refresh: {estimated_cost} units")
    print(f"Estimated Daily Refreshes: {daily_limit // estimated_cost if estimated_cost > 0 else '∞'}")
    
    refresh_interval = config.get('refresh_interval', 1800)
    daily_refreshes = (24 * 3600) // refresh_interval
    estimated_daily_usage = daily_refreshes * estimated_cost
    
    print(f"Current Refresh Interval: {refresh_interval}s ({refresh_interval//60}min)")
    print(f"Scheduled Daily Refreshes: {daily_refreshes}")
    print(f"Estimated Daily Usage: {estimated_daily_usage} units ({estimated_daily_usage/daily_limit*100:.1f}%)")
    
    if estimated_daily_usage > daily_limit:
        print("⚠️  WARNING: Estimated usage exceeds daily limit!")
        print("💡 Consider:")
        print("   - Reducing max_playlists")
        print("   - Reducing max_videos_per_playlist")
        print("   - Increasing refresh_interval")
        print("   - Using enabled_playlists to limit which playlists to fetch")

def suggest_optimizations(config):
    """Suggest quota optimizations"""
    print("\n💡 Quota Optimization Suggestions")
    print("=" * 50)
    
    quota_config = config.get('quota_management', {})
    playlist_config = config.get('playlists', {})
    
    daily_limit = quota_config.get('daily_quota_limit', 10000)
    
    # Conservative recommendations
    safe_daily_usage = daily_limit * 0.7  # Use only 70% of quota
    
    print("For Conservative Usage (70% of quota):")
    
    # Calculate optimal settings
    refresh_interval = config.get('refresh_interval', 1800)
    daily_refreshes = (24 * 3600) // refresh_interval
    quota_per_refresh = safe_daily_usage // daily_refreshes
    
    optimal_playlists = min(10, int(quota_per_refresh * 0.5))
    optimal_videos = min(50, int(quota_per_refresh * 0.3))
    
    print(f"  max_playlists: {optimal_playlists}")
    print(f"  max_videos_per_playlist: {optimal_videos}")
    print(f"  refresh_interval: {refresh_interval} ({refresh_interval//60}min)")
    print(f"  rate_limit_delay: 2.0")
    
    print("\nFor Minimal Usage:")
    print("  max_playlists: 3")
    print("  max_videos_per_playlist: 10")
    print("  refresh_interval: 3600 (1 hour)")
    print("  enabled_playlists: [\"specific_playlist_id\"]")

def set_emergency_mode(config_file, enabled):
    """Enable or disable emergency mode"""
    config = load_config(config_file)
    if not config:
        return
    
    if 'quota_management' not in config:
        config['quota_management'] = {}
    
    config['quota_management']['emergency_mode'] = enabled
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        status = "ENABLED" if enabled else "DISABLED"
        print(f"🚨 Emergency mode {status}")
        if enabled:
            print("   All YouTube API calls are now disabled")
        else:
            print("   YouTube API calls are now allowed")
            
    except Exception as e:
        print(f"❌ Error updating config: {e}")

def main():
    parser = argparse.ArgumentParser(description='YouTube FUSE Quota Manager')
    parser.add_argument('--config', default='youtube_config.json', help='Config file path')
    parser.add_argument('--status', action='store_true', help='Show quota status')
    parser.add_argument('--optimize', action='store_true', help='Show optimization suggestions')
    parser.add_argument('--emergency-on', action='store_true', help='Enable emergency mode')
    parser.add_argument('--emergency-off', action='store_true', help='Disable emergency mode')
    
    args = parser.parse_args()
    
    if args.emergency_on:
        set_emergency_mode(args.config, True)
        return
    
    if args.emergency_off:
        set_emergency_mode(args.config, False)
        return
    
    config = load_config(args.config)
    if not config:
        return
    
    if args.status or not any([args.optimize]):
        show_quota_status(config)
    
    if args.optimize:
        suggest_optimizations(config)

if __name__ == '__main__':
    main()
