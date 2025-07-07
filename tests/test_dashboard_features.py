#!/usr/bin/env python3
"""
Test script for enhanced YouTube FUSE Dashboard features
Tests playlist selection and sortable file display functionality
"""

import requests
import json
import time
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class DashboardTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_dashboard_accessible(self):
        """Test if dashboard is accessible"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ Dashboard is accessible")
                return True
            else:
                print(f"❌ Dashboard returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to access dashboard: {e}")
            return False
    
    def test_api_status(self):
        """Test API status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ API status endpoint works")
                print(f"   - System status: {data.get('system', {}).get('fuse_mounted', 'unknown')}")
                print(f"   - Playlists discovered: {len(data.get('playlists', {}).get('discovered_playlists', []))}")
                return True
            else:
                print(f"❌ API status failed with code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API status error: {e}")
            return False
    
    def test_api_files(self):
        """Test API files endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/files")
            if response.status_code == 200:
                data = response.json()
                print("✅ API files endpoint works")
                print(f"   - Found {len(data)} playlists")
                for playlist in data[:3]:  # Show first 3 playlists
                    print(f"   - {playlist['playlist']}: {playlist['count']} videos")
                return True
            else:
                print(f"❌ API files failed with code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API files error: {e}")
            return False
    
    def test_config_management(self):
        """Test configuration management"""
        try:
            # Get current config
            response = self.session.get(f"{self.base_url}/api/config")
            if response.status_code != 200:
                print(f"❌ Failed to get config: {response.status_code}")
                return False
            
            original_config = response.json()
            print("✅ Configuration retrieval works")
            
            # Test configuration update (safe change)
            test_config = original_config.copy()
            test_config.setdefault('playlists', {})
            test_config['playlists']['max_playlists'] = 5
            
            response = self.session.post(
                f"{self.base_url}/api/config",
                json=test_config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Configuration update works")
                
                # Restore original config
                self.session.post(
                    f"{self.base_url}/api/config",
                    json=original_config,
                    headers={'Content-Type': 'application/json'}
                )
                return True
            else:
                print(f"❌ Config update failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Config management error: {e}")
            return False
    
    def test_playlist_discovery(self):
        """Test playlist discovery endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/playlists/discover")
            
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print(f"⚠️  Playlist discovery returned error: {data['error']}")
                    print("   This is expected if YouTube API credentials are not configured")
                    return True
                else:
                    playlists = data.get('playlists', [])
                    print(f"✅ Playlist discovery works - found {len(playlists)} playlists")
                    return True
            else:
                print(f"❌ Playlist discovery failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Playlist discovery error: {e}")
            return False
    
    def test_playlist_enable_disable(self):
        """Test playlist enable/disable functionality"""
        try:
            # Test with a dummy playlist ID
            test_playlist_id = "test_playlist_123"
            
            # Enable playlist
            response = self.session.post(
                f"{self.base_url}/api/playlists/enable",
                json={"playlist_id": test_playlist_id, "enabled": True},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Playlist enable/disable endpoint works")
                
                # Disable playlist
                response = self.session.post(
                    f"{self.base_url}/api/playlists/enable",
                    json={"playlist_id": test_playlist_id, "enabled": False},
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print("✅ Playlist disable works")
                    return True
                else:
                    print(f"❌ Playlist disable failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Playlist enable failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Playlist enable/disable error: {e}")
            return False
    
    def test_dashboard_ui_features(self):
        """Test if dashboard UI includes new features"""
        try:
            response = self.session.get(self.base_url)
            html_content = response.text
            
            # Check for new features in HTML
            features_to_check = [
                'file-table',  # Sortable table
                'playlist-management',  # Playlist management section
                'toggle-switch-large',  # Large toggle switches
                'playlist-card',  # Playlist cards
                'view-toggle',  # View toggle buttons
                'search-box',  # File search box
                'sortFiles(',  # Sort function
                'filterFiles(',  # Filter function
                'togglePlaylistInCard('  # Playlist toggle function
            ]
            
            found_features = []
            missing_features = []
            
            for feature in features_to_check:
                if feature in html_content:
                    found_features.append(feature)
                else:
                    missing_features.append(feature)
            
            print(f"✅ Found {len(found_features)}/{len(features_to_check)} UI features")
            if found_features:
                print(f"   Found: {', '.join(found_features[:5])}...")
            
            if missing_features:
                print(f"⚠️  Missing: {', '.join(missing_features)}")
                return len(missing_features) == 0
                
            return True
            
        except Exception as e:
            print(f"❌ UI features test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🎥 YouTube FUSE Dashboard Feature Tests")
        print("=" * 50)
        
        tests = [
            ("Dashboard Access", self.test_dashboard_accessible),
            ("API Status", self.test_api_status),
            ("API Files", self.test_api_files),
            ("Config Management", self.test_config_management),
            ("Playlist Discovery", self.test_playlist_discovery),
            ("Playlist Enable/Disable", self.test_playlist_enable_disable),
            ("UI Features", self.test_dashboard_ui_features)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test '{test_name}' crashed: {e}")
                failed += 1
        
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if passed == len(tests):
            print("\n🎉 All tests passed! Dashboard features are working correctly.")
        elif failed == 0:
            print("\n✅ All tests completed successfully!")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        
        return failed == 0

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test YouTube FUSE Dashboard features')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Dashboard URL (default: http://localhost:5000)')
    parser.add_argument('--wait', type=int, default=5,
                       help='Seconds to wait for dashboard to start (default: 5)')
    
    args = parser.parse_args()
    
    print(f"Waiting {args.wait} seconds for dashboard to be ready...")
    time.sleep(args.wait)
    
    tester = DashboardTester(args.url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
