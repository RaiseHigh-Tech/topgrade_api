#!/bin/bash
# Force kill all Celery workers
# Run on server: bash force_kill_celery.sh

echo "=========================================="
echo "FORCE KILLING ALL CELERY WORKERS"
echo "=========================================="
echo ""

echo "1. Listing all Celery processes:"
ps aux | grep "[c]elery.*worker"
echo ""

echo "2. Force killing with SIGKILL..."
pkill -9 -f "celery.*worker"
sleep 3
echo ""

echo "3. Verify all killed:"
REMAINING=$(ps aux | grep "[c]elery.*worker" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✓ All Celery workers killed"
else
    echo "⚠ Still $REMAINING processes remaining"
    ps aux | grep "[c]elery.*worker"
fi
echo ""

echo "4. Clean up any orphaned processes:"
pkill -9 -f "celery"
sleep 2
echo ""

echo "5. Start fresh worker in background:"
cd ~/topgrade_api
source .venv/bin/activate
nohup celery -A topgrade worker --loglevel=info --logfile=celery.log 2>&1 &
NEW_PID=$!
echo "✓ Started new worker with PID: $NEW_PID"
sleep 5
echo ""

echo "6. Verify only ONE worker running:"
ps aux | grep "[c]elery.*worker" | grep -v grep
echo ""

echo "7. Check worker can connect:"
celery -A topgrade inspect ping
echo ""

echo "=========================================="
echo "READY - Run your tasks now"
echo "=========================================="
