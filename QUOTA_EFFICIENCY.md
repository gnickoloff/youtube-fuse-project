# YouTube FUSE Quota Efficiency Guide

## 🎯 Overview

YouTube FUSE v2.0+ includes advanced **incremental refresh** capabilities that dramatically reduce API quota usage by only fetching data that has actually changed. This can save **80-95% of your daily quota**.

## 🔍 How Change Detection Works

### ETags and Conditional Requests
- **ETags**: YouTube API provides unique identifiers for playlist states
- **If-None-Match**: HTTP header that returns "304 Not Modified" if unchanged
- **Minimal Quota Cost**: Change detection costs only 1 quota unit per playlist

### Smart Caching Strategy
1. **Playlist-Level ETags**: Track when playlists are added/removed
2. **Video-Level ETags**: Track when playlist contents change
3. **Timestamp Tracking**: Avoid redundant checks with time-based intervals

## 📊 Quota Comparison

| Operation | Full Refresh | Incremental | Savings |
|-----------|--------------|-------------|---------|
| Check 10 playlists | 20-30 units | 2-5 units | **80-85%** |
| No changes detected | 20-30 units | 1-2 units | **90-95%** |
| 2 playlists changed | 20-30 units | 5-8 units | **70-75%** |

## ⚙️ Configuration

### Enable/Disable Incremental Refresh

```json
{
  "quota_management": {
    "use_incremental_refresh": true,
    "playlist_check_interval": 3600
  }
}
```

### Fine-Tuning Parameters

- **`playlist_check_interval`**: How often to check for new/deleted playlists (default: 1 hour)
- **`cache_duration`**: How long to cache data before any refresh (default: 1 hour)
- **`rate_limit_delay`**: Delay between API calls (default: 1.0 seconds)

## 🛠️ Usage Examples

### Force Full Refresh
```bash
# Mount with full refresh (useful for first run or debugging)
python3 youtube_api_fuse.py /srv/youtube --full-refresh
```

### Normal Operation (Incremental)
```bash
# Default mode - uses incremental refresh automatically
python3 youtube_api_fuse.py /srv/youtube
```

### Check Quota Efficiency
```bash
# View quota usage analytics
python3 quota_analytics.py report

# Test efficiency comparison
python3 test_quota_efficiency.py
```

## 📈 Dashboard Integration

### Quota Efficiency Widget
The dashboard shows real-time efficiency metrics:

- **Total Quota Saved**: Cumulative quota units saved
- **Efficiency Rate**: Percentage of change checks that avoided full refresh
- **Recent Activity**: Average quota usage per refresh operation

### Refresh Mode Toggle
Switch between refresh modes:
- **⚡ Incremental Mode**: Quota-optimized (recommended)
- **🔄 Full Refresh Mode**: Always fetch everything (debugging/troubleshooting)

## 🔧 Advanced Features

### Change Detection Scenarios

1. **No Changes** (Most Common)
   - Cost: 1-2 quota units
   - Result: No data fetched, cached data used

2. **New Playlist Added**
   - Cost: 2-3 quota units
   - Result: Only new playlist fetched

3. **Videos Added to Playlist**
   - Cost: 2-4 quota units per changed playlist
   - Result: Only changed playlists refreshed

4. **Playlist Deleted**
   - Cost: 1 quota unit
   - Result: Playlist removed from cache

### Emergency Mode Compatibility
- Incremental refresh respects emergency mode
- Change detection continues even in emergency mode
- Zero quota usage when emergency mode is active

## 📊 Analytics and Monitoring

### Quota Analytics Tool
```bash
# Generate efficiency report
python3 quota_analytics.py report

# Example output:
# 📊 YouTube FUSE Quota Efficiency Report
# ==================================================
# 💰 Total Quota Saved: 1,247
# ⚡ Incremental Refreshes: 156
# 🔄 Full Refreshes: 12
# 🎯 Change Detection Efficiency: 87.3%
```

### Dashboard Metrics
- Real-time quota usage
- Efficiency trends over time
- Refresh operation history
- Cost per operation breakdown

## 🚀 Best Practices

### Optimal Settings for Different Use Cases

**Home Media Server** (Stable playlists):
```json
{
  "quota_management": {
    "use_incremental_refresh": true,
    "playlist_check_interval": 7200,
    "cache_duration": 3600,
    "rate_limit_delay": 2.0
  }
}
```

**Development/Testing** (Frequent changes):
```json
{
  "quota_management": {
    "use_incremental_refresh": true,
    "playlist_check_interval": 1800,
    "cache_duration": 1800,
    "rate_limit_delay": 1.0
  }
}
```

**High-Traffic Usage** (Multiple users):
```json
{
  "quota_management": {
    "use_incremental_refresh": true,
    "playlist_check_interval": 3600,
    "cache_duration": 7200,
    "rate_limit_delay": 3.0
  }
}
```

## 🔍 Troubleshooting

### Force Full Refresh When Needed
- After major YouTube account changes
- When debugging missing content
- After long periods of downtime

### Monitor Efficiency
```bash
# Check if incremental refresh is working
python3 quota_analytics.py report

# Should show high efficiency rate (>80%)
# Low efficiency might indicate frequent playlist changes
```

### Debug Mode
```bash
# Enable verbose logging
export YOUTUBE_DEBUG=1
python3 youtube_api_fuse.py /srv/youtube
```

## 🎉 Expected Results

With incremental refresh enabled, typical quota usage patterns:

- **Daily quota usage**: 50-200 units (vs 1000-2000 without)
- **Refresh operations**: 2-5 units each (vs 20-50 units)
- **Overall savings**: 80-95% quota reduction
- **Response time**: Faster refresh cycles
- **Reliability**: Better quota headroom for peak usage

This allows you to run YouTube FUSE 24/7 with minimal quota impact while maintaining up-to-date content!
