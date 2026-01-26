#!/bin/bash
# Clean restart of Celery worker
# Run on server: bash restart_celery_clean.sh

echo "Killing all Celery processes..."
pkill -9 -f celery
sleep 3

echo "Starting new Celery worker..."
celery -A topgrade worker --loglevel=info --logfile=celery.log &

echo "Waiting for worker to start..."
sleep 5

echo ""
echo "Checking worker status:"
celery -A topgrade inspect ping

echo ""
echo "Worker processes:"
ps aux | grep "[c]elery.*worker"
