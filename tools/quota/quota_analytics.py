#!/usr/bin/env python3
"""
YouTube FUSE Quota Analytics
Tracks and reports quota usage patterns and savings from incremental refresh
"""

import json
import time
from datetime import datetime, timedelta
import os

class QuotaAnalytics:
    def __init__(self, config_file='youtube_config.json'):
        self.config_file = config_file
        self.analytics_file = 'quota_analytics.json'
        self.load_analytics()
    
    def load_analytics(self):
        """Load historical quota analytics data"""
        try:
            with open(self.analytics_file, 'r') as f:
                self.analytics = json.load(f)
        except FileNotFoundError:
            self.analytics = {
                'daily_usage': {},
                'refresh_history': [],
                'quota_savings': {
                    'total_saved': 0,
                    'incremental_refreshes': 0,
                    'full_refreshes': 0,
                    'change_detection_hits': 0,
                    'change_detection_misses': 0
                }
            }
    
    def save_analytics(self):
        """Save analytics data to file"""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.analytics, f, indent=2)
    
    def record_refresh(self, refresh_type, playlists_checked, playlists_changed, quota_used):
        """Record a refresh operation for analytics"""
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        
        # Record daily usage
        if date_str not in self.analytics['daily_usage']:
            self.analytics['daily_usage'][date_str] = 0
        self.analytics['daily_usage'][date_str] += quota_used
        
        # Record refresh details
        refresh_record = {
            'timestamp': timestamp,
            'type': refresh_type,  # 'full', 'incremental', 'change_check'
            'playlists_checked': playlists_checked,
            'playlists_changed': playlists_changed,
            'quota_used': quota_used,
            'efficiency_ratio': playlists_changed / max(playlists_checked, 1)
        }
        
        self.analytics['refresh_history'].append(refresh_record)
        
        # Update savings counters
        if refresh_type == 'incremental':
            self.analytics['quota_savings']['incremental_refreshes'] += 1
            # Estimate quota saved vs full refresh
            estimated_full_cost = playlists_checked * 2  # Rough estimate
            saved = max(0, estimated_full_cost - quota_used)
            self.analytics['quota_savings']['total_saved'] += saved
        elif refresh_type == 'full':
            self.analytics['quota_savings']['full_refreshes'] += 1
        
        if playlists_changed == 0 and refresh_type == 'incremental':
            self.analytics['quota_savings']['change_detection_hits'] += 1
        elif playlists_changed > 0:
            self.analytics['quota_savings']['change_detection_misses'] += 1
        
        # Keep only last 30 days of history
        cutoff_time = timestamp - (30 * 24 * 60 * 60)
        self.analytics['refresh_history'] = [
            r for r in self.analytics['refresh_history'] 
            if r['timestamp'] > cutoff_time
        ]
        
        self.save_analytics()
    
    def get_quota_efficiency_report(self):
        """Generate a comprehensive quota efficiency report"""
        savings = self.analytics['quota_savings']
        recent_refreshes = [
            r for r in self.analytics['refresh_history']
            if r['timestamp'] > time.time() - (7 * 24 * 60 * 60)  # Last 7 days
        ]
        
        report = {
            'summary': {
                'total_quota_saved': savings['total_saved'],
                'incremental_refreshes': savings['incremental_refreshes'],
                'full_refreshes': savings['full_refreshes'],
                'efficiency_rate': (
                    savings['change_detection_hits'] / 
                    max(1, savings['change_detection_hits'] + savings['change_detection_misses'])
                ) * 100
            },
            'recent_activity': {
                'last_7_days_refreshes': len(recent_refreshes),
                'avg_quota_per_refresh': (
                    sum(r['quota_used'] for r in recent_refreshes) / 
                    max(1, len(recent_refreshes))
                ),
                'avg_efficiency_ratio': (
                    sum(r['efficiency_ratio'] for r in recent_refreshes) / 
                    max(1, len(recent_refreshes))
                )
            }
        }
        
        return report
    
    def print_efficiency_report(self):
        """Print a human-readable efficiency report"""
        report = self.get_quota_efficiency_report()
        
        print("📊 YouTube FUSE Quota Efficiency Report")
        print("=" * 50)
        
        print(f"\n💰 Total Quota Saved: {report['summary']['total_quota_saved']}")
        print(f"⚡ Incremental Refreshes: {report['summary']['incremental_refreshes']}")
        print(f"🔄 Full Refreshes: {report['summary']['full_refreshes']}")
        print(f"🎯 Change Detection Efficiency: {report['summary']['efficiency_rate']:.1f}%")
        
        print(f"\n📈 Recent Activity (Last 7 Days)")
        print(f"🔄 Total Refreshes: {report['recent_activity']['last_7_days_refreshes']}")
        print(f"📊 Avg Quota per Refresh: {report['recent_activity']['avg_quota_per_refresh']:.1f}")
        print(f"⚡ Avg Efficiency Ratio: {report['recent_activity']['avg_efficiency_ratio']:.2f}")
        
        if report['summary']['total_quota_saved'] > 0:
            print(f"\n🎉 Incremental refresh has saved you {report['summary']['total_quota_saved']} quota units!")
            print("   This means more API calls available for other operations.")
        
        # Daily usage chart
        recent_usage = {}
        for date_str, usage in self.analytics['daily_usage'].items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj > datetime.now() - timedelta(days=7):
                recent_usage[date_str] = usage
        
        if recent_usage:
            print(f"\n📅 Daily Quota Usage (Last 7 Days)")
            for date_str in sorted(recent_usage.keys()):
                usage = recent_usage[date_str]
                bar = "█" * min(20, usage // 10)
                print(f"  {date_str}: {usage:4d} {bar}")

def main():
    import sys
    
    analytics = QuotaAnalytics()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'report':
            analytics.print_efficiency_report()
        elif sys.argv[1] == 'reset':
            analytics.analytics = {
                'daily_usage': {},
                'refresh_history': [],
                'quota_savings': {
                    'total_saved': 0,
                    'incremental_refreshes': 0,
                    'full_refreshes': 0,
                    'change_detection_hits': 0,
                    'change_detection_misses': 0
                }
            }
            analytics.save_analytics()
            print("🔄 Analytics data reset")
        else:
            print("Usage: python quota_analytics.py [report|reset]")
    else:
        analytics.print_efficiency_report()

if __name__ == '__main__':
    main()
