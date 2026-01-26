#!/bin/bash
# Check if topic duration was updated
# Run on server: bash check_topic_duration.sh

python manage.py shell << 'EOF'
from topgrade_api.models import Topic

topic = Topic.objects.get(id=4)
print(f"Topic ID: {topic.id}")
print(f"Topic Title: {topic.topic_title}")
print(f"Video Duration: {topic.video_duration}")
print(f"Video File: {topic.video_file}")
EOF
