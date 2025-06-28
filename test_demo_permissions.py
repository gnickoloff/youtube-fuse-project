#!/usr/bin/env python3

import os
import sys
import stat

def test_permissions(mount_point):
    """Test the permissions and ownership of the demo FUSE filesystem"""
    print(f"🧪 Testing permissions for demo FUSE mount at: {mount_point}")
    
    try:
        # Test root directory
        root_stat = os.stat(mount_point)
        print(f"\n📁 Root directory ({mount_point}):")
        print(f"   Mode: {oct(root_stat.st_mode)} (expected: 0o42775)")
        print(f"   UID: {root_stat.st_uid} (expected: 121)")
        print(f"   GID: {root_stat.st_gid} (expected: 130)")
        print(f"   Setgid bit: {'✅' if root_stat.st_mode & stat.S_ISGID else '❌'}")
        
        # List playlists
        playlists = [d for d in os.listdir(mount_point) if os.path.isdir(os.path.join(mount_point, d))]
        print(f"\n📺 Found {len(playlists)} playlists: {playlists}")
        
        # Test first playlist directory if available
        if playlists:
            playlist_path = os.path.join(mount_point, playlists[0])
            playlist_stat = os.stat(playlist_path)
            print(f"\n📁 Playlist directory ({playlists[0]}):")
            print(f"   Mode: {oct(playlist_stat.st_mode)} (expected: 0o42775)")
            print(f"   UID: {playlist_stat.st_uid} (expected: 121)")
            print(f"   GID: {playlist_stat.st_gid} (expected: 130)")
            print(f"   Setgid bit: {'✅' if playlist_stat.st_mode & stat.S_ISGID else '❌'}")
            
            # Test video files in the playlist
            videos = [f for f in os.listdir(playlist_path) if f.endswith('.mp4')]
            print(f"\n🎬 Found {len(videos)} videos in {playlists[0]}: {videos}")
            
            if videos:
                video_path = os.path.join(playlist_path, videos[0])
                video_stat = os.stat(video_path)
                print(f"\n📄 Video file ({videos[0]}):")
                print(f"   Mode: {oct(video_stat.st_mode)} (expected: 0o100664)")
                print(f"   UID: {video_stat.st_uid} (expected: 121)")
                print(f"   GID: {video_stat.st_gid} (expected: 130)")
                print(f"   Size: {video_stat.st_size:,} bytes")
                
                # Test read access
                try:
                    with open(video_path, 'rb') as f:
                        data = f.read(50)
                    print(f"   Read test: ✅ (read {len(data)} bytes)")
                    print(f"   Content preview: {data[:30]}...")
                except Exception as e:
                    print(f"   Read test: ❌ ({e})")
        
        # Test write protection
        print(f"\n🔒 Testing write protection:")
        try:
            test_file = os.path.join(mount_point, "test_write.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            print("   Write test: ❌ (write should have failed)")
            os.unlink(test_file)  # cleanup if somehow succeeded
        except OSError as e:
            print(f"   Write test: ✅ (correctly blocked: {e})")
        
        print(f"\n✅ Demo FUSE filesystem permissions test completed!")
        
    except Exception as e:
        print(f"❌ Error testing permissions: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_demo_permissions.py <mount_point>")
        sys.exit(1)
    
    mount_point = sys.argv[1]
    if not os.path.exists(mount_point):
        print(f"❌ Mount point does not exist: {mount_point}")
        sys.exit(1)
    
    success = test_permissions(mount_point)
    sys.exit(0 if success else 1)
