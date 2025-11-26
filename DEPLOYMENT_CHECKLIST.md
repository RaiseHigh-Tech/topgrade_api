# 📋 Deployment Checklist - Email Certificate System

## ✅ Pre-Deployment Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected packages:**
- celery==5.4.0
- redis==5.0.1
- django-celery-results==2.5.1

### 2. Install Redis Server

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis
sudo systemctl status redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Verify Redis:**
```bash
redis-cli ping
# Expected output: PONG
```

### 3. Configure Environment Variables

Create `.env` file in project root (copy from `.env.example`):

```env
# Email Configuration (REQUIRED)
EMAIL_HOST_USER=noreply@topgradeinnovations.com
EMAIL_HOST_PASSWORD=your_google_app_specific_password_here

# Celery & Redis (REQUIRED)
CELERY_BROKER_URL=redis://localhost:6379/0

# Database (existing)
USE_POSTGRES=false
# ... other existing variables
```

**Get Google App Password:**
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification if not already enabled
3. Click "App Passwords"
4. Select "Mail" and generate
5. Copy the 16-character password
6. Paste into `.env` as `EMAIL_HOST_PASSWORD`

### 4. Run Database Migrations

```bash
python manage.py migrate
```

**Expected output:**
```
Running migrations:
  Applying django_celery_results.0001_initial... OK
  Applying django_celery_results.0002_add_task_name... OK
  ...
```

## ✅ Testing Before Production

### Test 1: Redis Connection
```bash
redis-cli ping
```
✅ Should return: `PONG`

### Test 2: Email Configuration
```bash
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test message',
    'noreply@topgradeinnovations.com',
    ['your-test-email@example.com'],
    fail_silently=False,
)
# If successful, you'll receive a test email
```

### Test 3: Celery Task
```bash
# Terminal 1: Start Celery
celery -A topgrade worker --loglevel=info

# Terminal 2: Test task
python manage.py shell
```
```python
from dashboard.tasks import send_certificates_email_task
from topgrade_api.models import UserCourseProgress

# Get a test course progress
cp = UserCourseProgress.objects.filter(is_completed=True).first()
if cp:
    result = send_certificates_email_task.delay(cp.id)
    print(f"Task ID: {result.id}")
    print(f"Status: {result.status}")
```

Watch Terminal 1 for task execution logs.

### Test 4: Full Workflow
1. Start Django: `python manage.py runserver`
2. Start Celery: `./start_celery.sh`
3. Navigate to: http://localhost:8000/dashboard/student-certificates/
4. Click "Generate All" on a completed course
5. Verify certificates appear with download links
6. Click "Send All"
7. Verify toast notification shows success
8. Check student email for certificate attachments

## ✅ Production Deployment

### Option A: Manual Start (Development/Testing)

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery:**
```bash
./start_celery.sh
```

### Option B: Systemd Service (Production - Linux)

1. Create Celery service file:
```bash
sudo nano /etc/systemd/system/topgrade-celery.service
```

2. Add content:
```ini
[Unit]
Description=TopGrade Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/topgrade
EnvironmentFile=/path/to/topgrade/.env
ExecStart=/path/to/venv/bin/celery -A topgrade worker --loglevel=info --logfile=/var/log/celery/topgrade.log --pidfile=/var/run/celery/topgrade.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Create log directory:
```bash
sudo mkdir -p /var/log/celery
sudo mkdir -p /var/run/celery
sudo chown www-data:www-data /var/log/celery /var/run/celery
```

4. Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable topgrade-celery
sudo systemctl start topgrade-celery
sudo systemctl status topgrade-celery
```

### Option C: Supervisor (Production - Alternative)

1. Install Supervisor:
```bash
sudo apt-get install supervisor
```

2. Create config:
```bash
sudo nano /etc/supervisor/conf.d/topgrade-celery.conf
```

3. Add content:
```ini
[program:topgrade-celery]
command=/path/to/venv/bin/celery -A topgrade worker --loglevel=info
directory=/path/to/topgrade
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/topgrade-worker.log
environment=DJANGO_SETTINGS_MODULE="topgrade.settings"
```

4. Start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start topgrade-celery
sudo supervisorctl status
```

## ✅ Monitoring & Maintenance

### Monitor Celery Worker
```bash
# View logs
tail -f /var/log/celery/topgrade.log

# Check status
ps aux | grep celery

# Systemd status
sudo systemctl status topgrade-celery
```

### Monitor Redis
```bash
# Check if running
redis-cli ping

# Monitor memory
redis-cli info memory

# Check active connections
redis-cli client list
```

### Monitor Email Sending
Check Django admin:
```
http://your-domain.com/admin/django_celery_results/taskresult/
```

Filter by:
- Task name: `dashboard.tasks.send_certificates_email_task`
- Status: SUCCESS, FAILURE, PENDING

### Check Logs
```bash
# Celery worker logs
tail -f /var/log/celery/topgrade.log

# Django logs (if configured)
tail -f /var/log/django/topgrade.log

# Redis logs
tail -f /var/log/redis/redis-server.log
```

## ✅ Troubleshooting

### Problem: Celery worker not starting
**Solution:**
```bash
# Check Python path
which python

# Check Celery installation
pip show celery

# Check Redis connection
redis-cli ping

# Try starting manually with verbose output
celery -A topgrade worker --loglevel=debug
```

### Problem: Tasks not being picked up
**Solution:**
```bash
# Restart Celery worker
sudo systemctl restart topgrade-celery

# Check task queue in Redis
redis-cli
> KEYS *
> LLEN celery

# Check worker is registered
celery -A topgrade inspect active
```

### Problem: Emails not sending
**Solution:**
```bash
# Check email settings in .env
cat .env | grep EMAIL

# Test SMTP connection
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail('Test', 'Test', 'noreply@topgradeinnovations.com', ['test@example.com'])
```

### Problem: Redis connection refused
**Solution:**
```bash
# Check Redis is running
sudo systemctl status redis

# Start Redis
sudo systemctl start redis

# Check Redis port
netstat -tuln | grep 6379
```

## ✅ Security Checklist

- [ ] `.env` file has correct permissions (600)
- [ ] `.env` is in `.gitignore`
- [ ] Email password is app-specific, not main password
- [ ] Redis is not exposed to public internet
- [ ] Celery worker runs as non-root user
- [ ] SSL/TLS enabled for email (port 587)
- [ ] CSRF protection enabled (already configured)
- [ ] Admin panel requires authentication (already configured)

## ✅ Performance Optimization

### For High Volume (1000+ emails/day):

1. **Use Multiple Workers:**
```bash
# Start 4 worker processes
celery -A topgrade worker --concurrency=4 --loglevel=info
```

2. **Use Professional Email Service:**
- AWS SES (Amazon Simple Email Service)
- SendGrid
- Mailgun

Update settings.py:
```python
# For AWS SES
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-1'
```

3. **Redis Optimization:**
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Increase max memory
maxmemory 256mb
maxmemory-policy allkeys-lru
```

4. **Monitor with Flower:**
```bash
pip install flower
celery -A topgrade flower --port=5555
```
Access: http://localhost:5555

## ✅ Backup & Recovery

### Backup Task Results
```bash
# Export task results
python manage.py dumpdata django_celery_results > celery_tasks_backup.json

# Restore
python manage.py loaddata celery_tasks_backup.json
```

### Redis Backup
```bash
# Enable Redis persistence
sudo nano /etc/redis/redis.conf
# Uncomment: save 900 1

# Manual backup
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backup/redis-backup-$(date +%Y%m%d).rdb
```

## ✅ Final Verification

Before going live, verify:

- [ ] Redis server running and accessible
- [ ] Celery worker running and processing tasks
- [ ] Email credentials configured correctly
- [ ] Test email sent successfully
- [ ] AJAX endpoints responding correctly
- [ ] Loading spinners working
- [ ] Toast notifications appearing
- [ ] Certificates generating correctly
- [ ] Emails received with attachments
- [ ] Verification link in email correct
- [ ] Task monitoring accessible in admin
- [ ] Logs being written correctly
- [ ] Error handling working
- [ ] Retry mechanism tested

## 📊 Success Indicators

Your system is working correctly if:

✅ Celery worker shows "ready" in logs  
✅ Redis responds to PING  
✅ "Send All" button shows loading spinner  
✅ Toast notification appears within 1 second  
✅ Certificate status changes to "Sent"  
✅ Student receives email within 1-2 minutes  
✅ Email contains all certificate attachments  
✅ Task appears as "SUCCESS" in admin  

## 📞 Support

If you encounter issues:

1. Check logs first
2. Verify all checklist items
3. Test individual components
4. Contact support:
   - 📧 support@topgradeinnovations.com
   - 📞 +91 76194 68135 | +91 89044 65305

## 📚 Additional Resources

- Quick Start: `QUICK_START_EMAIL_CERTIFICATES.md`
- Detailed Setup: `CELERY_EMAIL_SETUP.md`
- Implementation: `IMPLEMENTATION_SUMMARY.md`
- Celery Docs: https://docs.celeryproject.org/
- Redis Docs: https://redis.io/documentation

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Ready for Deployment
