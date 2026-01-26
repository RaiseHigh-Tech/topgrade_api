#!/bin/bash
# Check Celery broker configuration issue
# Run on server: bash check_celery_broker.sh

echo "=========================================="
echo "CELERY BROKER CONFIGURATION DEBUG"
echo "=========================================="
echo ""

echo "1. Check Django settings for Celery:"
python manage.py shell << 'EOF'
from django.conf import settings
import os

print("CELERY_BROKER_URL:", getattr(settings, 'CELERY_BROKER_URL', 'NOT SET'))
print("CELERY_RESULT_BACKEND:", getattr(settings, 'CELERY_RESULT_BACKEND', 'NOT SET'))
print("CELERY_TASK_ALWAYS_EAGER:", getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False))
print("")
print("Environment CELERY_BROKER_URL:", os.getenv('CELERY_BROKER_URL', 'NOT SET'))
EOF
echo ""

echo "2. Check what Celery sees at startup:"
python << 'EOF'
from topgrade.celery import app

print("Celery Broker URL:", app.conf.broker_url)
print("Celery Result Backend:", app.conf.result_backend)
print("Task always eager:", app.conf.task_always_eager)
print("Task serializer:", app.conf.task_serializer)
EOF
echo ""

echo "3. Test sending a simple task to broker:"
python << 'EOF'
from topgrade.celery import app
import redis

# Test Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)
print("Redis PING:", r.ping())

# Check celery queue before
queue_before = r.llen('celery')
print(f"Queue length before: {queue_before}")

# Try to push a test message directly to Redis
import json
import uuid
task_id = str(uuid.uuid4())
message = {
    "body": "test",
    "headers": {},
    "content-type": "application/json",
    "properties": {
        "correlation_id": task_id,
        "reply_to": task_id
    }
}
r.lpush('celery', json.dumps(message))

queue_after = r.llen('celery')
print(f"Queue length after: {queue_after}")
print("Task pushed to queue:", queue_after > queue_before)
EOF
echo ""

echo "4. Check if worker sees the test task:"
sleep 2
redis-cli llen celery
echo ""
