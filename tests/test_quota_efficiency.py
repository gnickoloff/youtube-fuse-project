#!/usr/bin/env python3
"""
Test script to demonstrate quota savings from incremental refresh
"""

import time
import json
from youtube_api_fuse import YouTubeAPIFUSE

def test_quota_efficiency():
    """Test and compare full vs incremental refresh quota usage"""
    
    print("🧪 YouTube FUSE Quota Efficiency Test")
    print("=" * 50)
    
    # Create FUSE instance
    fuse = YouTubeAPIFUSE()
    
    print(f"\n📊 Initial quota usage: {fuse.quota_usage}")
    
    # Test 1: Full refresh
    print("\n🔄 Testing FULL refresh...")
    start_quota = fuse.quota_usage
    fuse.refresh_videos(force_full_refresh=True)
    full_refresh_cost = fuse.quota_usage - start_quota
    print(f"💰 Full refresh quota cost: {full_refresh_cost}")
    
    # Wait a moment then test incremental
    time.sleep(2)
    
    # Test 2: Incremental refresh (should be much cheaper)
    print("\n⚡ Testing INCREMENTAL refresh...")
    start_quota = fuse.quota_usage
    fuse.refresh_videos(force_full_refresh=False)
    incremental_cost = fuse.quota_usage - start_quota
    print(f"💰 Incremental refresh quota cost: {incremental_cost}")
    
    # Calculate savings
    if full_refresh_cost > 0:
        savings_percent = ((full_refresh_cost - incremental_cost) / full_refresh_cost) * 100
        print(f"\n🎉 QUOTA SAVINGS: {savings_percent:.1f}%")
        print(f"   Full refresh: {full_refresh_cost} quota units")
        print(f"   Incremental:  {incremental_cost} quota units")
        print(f"   Saved:        {full_refresh_cost - incremental_cost} quota units")
    
    # Show change detection stats
    if hasattr(fuse, 'playlist_etags') and fuse.playlist_etags:
        print(f"\n📈 Change Detection Stats:")
        print(f"   Tracked playlists: {len(fuse.playlist_etags)}")
        print(f"   ETag cache size: {len([k for k in fuse.playlist_etags.keys() if '_items' in k])}")
    
    print(f"\n📊 Total quota used in test: {fuse.quota_usage}")
    daily_limit = fuse.config.get('quota_management', {}).get('daily_quota_limit', 10000)
    usage_percent = (fuse.quota_usage / daily_limit) * 100
    print(f"📈 Daily quota usage: {usage_percent:.2f}%")

if __name__ == '__main__':
    test_quota_efficiency()
