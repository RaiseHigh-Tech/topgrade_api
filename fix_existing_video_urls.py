#!/usr/bin/env python
"""
Script to fix existing video URLs in the database
Converts full S3 URLs to relative paths for CloudFront compatibility

Run: python fix_existing_video_urls.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topgrade.settings')
django.setup()

from topgrade_api.models import Topic

def fix_video_urls():
    """Fix video URLs in the database"""
    print("=" * 70)
    print("Fixing Video URLs in Database")
    print("=" * 70)
    
    # Get all topics with video files
    topics = Topic.objects.exclude(video_file='')
    total = topics.count()
    
    if total == 0:
        print("\n✓ No videos found in database")
        return
    
    print(f"\nFound {total} topics with videos")
    print("-" * 70)
    
    fixed_count = 0
    skipped_count = 0
    
    for topic in topics:
        video_path = str(topic.video_file.name)
        
        # Check if it's a full URL (starts with http:// or https://)
        if video_path.startswith('http://') or video_path.startswith('https://'):
            print(f"\n✗ Topic ID {topic.id}: {topic.topic_title}")
            print(f"  Old: {video_path[:80]}...")
            
            # Extract the S3 key from the full URL
            # Handle different URL formats
            if '.amazonaws.com/' in video_path:
                # Extract path after .amazonaws.com/
                s3_key = video_path.split('.amazonaws.com/')[-1]
            elif 'topgradeinnovation.com/' in video_path:
                # Extract path after domain
                s3_key = video_path.split('topgradeinnovation.com/')[-1]
            else:
                # Unknown format
                print(f"  ⚠️  Warning: Unknown URL format, skipping")
                skipped_count += 1
                continue
            
            # Remove "media/" prefix if present
            if s3_key.startswith('media/'):
                s3_key = s3_key[6:]  # Remove "media/"
            
            # Update the video file
            topic.video_file = s3_key
            topic.save()
            
            print(f"  New: {s3_key}")
            print(f"  ✓ Fixed!")
            fixed_count += 1
        else:
            # Already a relative path
            print(f"\n✓ Topic ID {topic.id}: {topic.topic_title}")
            print(f"  Path: {video_path}")
            print(f"  Already correct (relative path)")
            skipped_count += 1
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total videos: {total}")
    print(f"Fixed: {fixed_count}")
    print(f"Already correct/skipped: {skipped_count}")
    print("=" * 70)
    
    if fixed_count > 0:
        print("\n✓ Database updated successfully!")
        print("\nNew videos will render as:")
        print("https://media.topgradeinnovation.com/media/programs/...")
    else:
        print("\n✓ All video paths are already correct!")

if __name__ == '__main__':
    try:
        # Confirm before proceeding
        print("\n⚠️  This script will update video URLs in the database")
        print("   Converting full URLs to relative paths")
        print("\nPress Enter to continue, or Ctrl+C to cancel...")
        input()
        
        fix_video_urls()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n✗ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
