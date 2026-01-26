#!/bin/bash
# Test the task function directly (not via Celery)
# Run on server: bash test_task_directly.sh

python manage.py shell << 'EOF'
from topgrade_api.models import Topic
from dashboard.views.program_view import calculate_video_duration_from_s3

# Get one topic without duration
topic = Topic.objects.filter(
    video_file__isnull=False,
    video_duration__isnull=True
).exclude(video_file='').first()

if topic:
    print(f"Testing Topic ID: {topic.id}")
    print(f"Video file: {topic.video_file}")
    print("")
    
    # Try to calculate duration directly
    try:
        video_path = str(topic.video_file)
        print(f"Calling calculate_video_duration_from_s3('{video_path}')...")
        duration = calculate_video_duration_from_s3(video_path)
        print(f"Result: {duration}")
        
        if duration:
            print(f"✓ SUCCESS - Duration calculated: {duration}")
        else:
            print("✗ FAILED - Duration is None")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No topics without duration found")
EOF
