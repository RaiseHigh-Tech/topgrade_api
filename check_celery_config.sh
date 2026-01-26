#!/bin/bash
# Check Celery configuration and connectivity
# Run on server: bash check_celery_config.sh

echo "=========================================="
echo "CELERY CONFIGURATION CHECK"
echo "=========================================="
echo ""

echo "1. Redis Connection:"
redis-cli ping
echo ""

echo "2. Celery Broker URL from settings:"
python manage.py shell << 'EOF'
from django.conf import settings
print(f"CELERY_BROKER_URL: {getattr(settings, 'CELERY_BROKER_URL', 'NOT SET')}")
print(f"CELERY_RESULT_BACKEND: {getattr(settings, 'CELERY_RESULT_BACKEND', 'NOT SET')}")
EOF
echo ""

echo "3. Test Redis connection from Python:"
python << 'EOF'
import redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✓ Redis connection OK")
except Exception as e:
    print(f"✗ Redis connection FAILED: {e}")
EOF
echo ""

echo "4. Celery Worker Status:"
celery -A topgrade inspect stats
echo ""

echo "5. Check if tasks are registered:"
celery -A topgrade inspect registered | grep calculate_video_duration
echo ""

echo "6. Check Celery queue in Redis:"
redis-cli llen celery
echo ""
