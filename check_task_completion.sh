#!/bin/bash
# Check if video duration calculation tasks completed
# Run on server: bash check_task_completion.sh

python manage.py shell << 'EOF'
from topgrade_api.models import Topic

total = Topic.objects.filter(video_file__isnull=False).exclude(video_file='').count()
with_duration = Topic.objects.filter(video_duration__isnull=False).exclude(video_duration='').count()
without = total - with_duration

print(f"Total videos: {total}")
print(f"With duration: {with_duration}")
print(f"Without duration: {without}")
print(f"Progress: {(with_duration/total*100):.1f}%" if total > 0 else "No videos")
EOF
