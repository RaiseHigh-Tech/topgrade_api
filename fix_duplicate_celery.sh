#!/bin/bash
# Fix duplicate Celery workers
# Run on server: bash fix_duplicate_celery.sh

echo "=========================================="
echo "FIXING DUPLICATE CELERY WORKERS"
echo "=========================================="
echo ""

echo "1. Current Celery processes:"
ps aux | grep "celery.*worker" | grep -v grep
echo ""

echo "2. Killing ALL Celery workers..."
pkill -f "celery.*worker"
sleep 2
echo ""

echo "3. Verify all killed:"
ps aux | grep "celery.*worker" | grep -v grep || echo "✓ All Celery workers stopped"
echo ""

echo "4. Starting fresh Celery worker..."
nohup celery -A topgrade worker --loglevel=info > celery_worker.log 2>&1 &
NEW_PID=$!
echo "✓ New Celery worker started with PID: $NEW_PID"
sleep 3
echo ""

echo "5. Verify new worker is running:"
ps aux | grep "celery.*worker" | grep -v grep
echo ""

echo "6. Check worker status:"
celery -A topgrade inspect stats | head -20
echo ""

echo "=========================================="
echo "DONE - Now test your tasks again"
echo "=========================================="
echo "Run: bash test_single_task.sh"
echo "Then wait 10 seconds and run: bash check_task_completion.sh"
