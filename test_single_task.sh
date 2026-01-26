#!/bin/bash
# Test if a single task can run
# Run on server: bash test_single_task.sh

python manage.py shell << 'EOF'
from dashboard.tasks import calculate_video_duration_task
from topgrade_api.models import Topic

# Get one topic without duration
topic = Topic.objects.filter(
    video_file__isnull=False,
    video_duration__isnull=True
).exclude(video_file='').first()

if topic:
    print(f"Testing with Topic ID: {topic.id}")
    print(f"Video file: {topic.video_file}")
    
    # Try to run task
    result = calculate_video_duration_task.delay(topic.id)
    print(f"Task ID: {result.id}")
    print(f"Task state: {result.state}")
else:
    print("No topics without duration found")
EOF
