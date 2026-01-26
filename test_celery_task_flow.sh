#!/bin/bash
# Test complete Celery task flow
# Run on server: bash test_celery_task_flow.sh

echo "=========================================="
echo "CELERY TASK FLOW TEST"
echo "=========================================="
echo ""

echo "1. Check queue before:"
BEFORE=$(redis-cli llen celery)
echo "Queue length: $BEFORE"
echo ""

echo "2. Send task and monitor Redis:"
python manage.py shell << 'EOF'
from dashboard.tasks import calculate_video_duration_task
from topgrade_api.models import Topic
import time

# Get topic
topic = Topic.objects.filter(
    video_file__isnull=False,
    video_duration__isnull=True
).exclude(video_file='').first()

if topic:
    print(f"Sending task for Topic ID: {topic.id}")
    
    # Send task
    result = calculate_video_duration_task.delay(topic.id)
    print(f"Task ID: {result.id}")
    print(f"Task backend: {result.backend}")
    
    # Wait a moment
    time.sleep(1)
    
    # Check state immediately
    print(f"Task state after 1s: {result.state}")
    
    # Try to get result (will timeout if still running)
    try:
        res = result.get(timeout=5)
        print(f"Task result: {res}")
    except Exception as e:
        print(f"Task still running or failed: {type(e).__name__}")
        
    # Check final state
    print(f"Final task state: {result.state}")
else:
    print("No topic found")
EOF
echo ""

echo "3. Check queue after:"
AFTER=$(redis-cli llen celery)
echo "Queue length: $AFTER"
echo ""

echo "4. Check if anything in Redis:"
redis-cli keys "celery*"
echo ""

echo "5. Check active tasks in worker:"
celery -A topgrade inspect active
echo ""
