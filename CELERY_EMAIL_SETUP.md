# Celery Email Setup for Certificate Distribution

## Overview
This implementation uses Celery with Redis to send certificate emails in the background, ensuring the admin dashboard remains responsive while emails are being sent.

## Prerequisites

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

New packages added:
- `celery==5.4.0` - Distributed task queue
- `redis==5.0.1` - Message broker
- `django-celery-results==2.5.1` - Store task results in Django database

### 2. Install and Start Redis Server

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Windows:
Download from: https://github.com/microsoftarchive/redis/releases

#### Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 3. Configure Email Settings

Add these environment variables to your `.env` file:

```env
# Email Configuration (Google Workspace)
EMAIL_HOST_USER=noreply@topgradeinnovations.com
EMAIL_HOST_PASSWORD=your_app_specific_password

# Celery/Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
```

#### Google Workspace App Password Setup:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate new app password for "Mail"
5. Use this password in `EMAIL_HOST_PASSWORD`

### 4. Run Database Migrations

```bash
python manage.py migrate
```

This creates tables for Celery task results.

## Running the System

### Development Environment

You need **3 terminal windows**:

#### Terminal 1: Django Server
```bash
python manage.py runserver
```

#### Terminal 2: Celery Worker
```bash
# Linux/macOS
celery -A topgrade worker --loglevel=info

# Windows
celery -A topgrade worker --loglevel=info --pool=solo
```

Or use the provided script:
```bash
chmod +x start_celery.sh
./start_celery.sh
```

#### Terminal 3: Redis Server (if not running as service)
```bash
redis-server
```

### Production Environment

Use process managers like **Supervisor** or **systemd**:

#### Using Supervisor

1. Install Supervisor:
```bash
sudo apt-get install supervisor
```

2. Create config file `/etc/supervisor/conf.d/topgrade_celery.conf`:
```ini
[program:topgrade_celery]
command=/path/to/venv/bin/celery -A topgrade worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/topgrade_worker.log
environment=DJANGO_SETTINGS_MODULE="topgrade.settings"

[program:topgrade_redis]
command=/usr/bin/redis-server
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/redis/redis.log
```

3. Start services:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start topgrade_celery
```

## How It Works

### Flow Diagram
```
Admin clicks "Send All" 
    ↓
AJAX Request to /api/send-certificate/
    ↓
View updates certificate status to "sent"
    ↓
Celery task queued in Redis
    ↓
View returns success response immediately
    ↓
Celery worker picks up task from Redis
    ↓
Worker sends email with attachments
    ↓
Task result stored in database
```

### Email Template

**Subject:** Certificates of Completion - TopGrade Innovation

**Body:**
```
Dear {Student Name},

Congratulations on successfully completing your program with TopGrade Innovation Pvt. Ltd.

Your Certificates of Completion are attached to this email.
Every certificate includes a unique verification ID.

Verification Portal: https://www.topgradeinnovation.com/certificate-verification/

Important Notice:
This is an automated message from noreply@topgradeinnovations.com
Please do not reply to this email.

Support:
📧 support@topgradeinnovations.com
📞 +91 76194 68135 | +91 89044 65305
```

**Attachments:**
- Internship Certificate
- Training Certificate
- Credit Certificate
- Letter of Recommendation
- Placement Certificate (if Goldpass)

## Features

### 1. Background Processing
- Emails sent asynchronously
- No page reload or waiting
- Dashboard remains responsive

### 2. Retry Mechanism
- Automatic retry on failure (up to 3 times)
- 60-second delay between retries
- Error logging for debugging

### 3. Task Monitoring
You can monitor tasks in Django admin:
```
http://localhost:8000/admin/django_celery_results/taskresult/
```

### 4. Progress Indicators
- Loading spinner during operations
- Toast notifications for success/error
- Real-time UI updates

## Testing

### Test Celery Connection:
```bash
python manage.py shell
```

```python
from dashboard.tasks import send_certificates_email_task
from topgrade_api.models import UserCourseProgress

# Get a course progress ID
cp = UserCourseProgress.objects.filter(is_completed=True).first()
if cp:
    # Queue the task
    result = send_certificates_email_task.delay(cp.id)
    print(f"Task ID: {result.id}")
    
    # Check task status
    print(f"Status: {result.status}")
    
    # Get result (this will wait for task to complete)
    print(f"Result: {result.get(timeout=10)}")
```

### Monitor Celery Worker Logs:
```bash
# Watch in real-time
tail -f /var/log/celery/topgrade_worker.log
```

## Troubleshooting

### Issue: Celery worker not picking up tasks
**Solution:**
```bash
# Check Redis connection
redis-cli ping

# Restart Celery worker
pkill -f "celery worker"
celery -A topgrade worker --loglevel=info
```

### Issue: Email not sending
**Solution:**
1. Check email credentials in `.env`
2. Verify Google Workspace app password
3. Check Celery worker logs
4. Test email settings:
```python
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail(
    'Test',
    'Test message',
    'noreply@topgradeinnovations.com',
    ['your-email@example.com'],
    fail_silently=False,
)
```

### Issue: Certificate files not attaching
**Solution:**
- Verify certificate files exist in storage
- Check S3 permissions if using AWS S3
- Review task logs for specific errors

### Issue: Redis connection refused
**Solution:**
```bash
# Start Redis
sudo systemctl start redis

# Or on macOS
brew services start redis
```

## Performance Considerations

### Email Rate Limits
Google Workspace limits:
- **500 emails per day** for free accounts
- **2000 emails per day** for paid accounts

If you exceed limits, consider:
1. Batch processing with delays
2. Using professional email service (SendGrid, AWS SES)
3. Queuing emails across multiple days

### Celery Concurrency
Adjust worker concurrency based on your server:
```bash
# 4 concurrent processes
celery -A topgrade worker --concurrency=4 --loglevel=info
```

### Redis Memory
Monitor Redis memory usage:
```bash
redis-cli info memory
```

## Security Notes

1. **Never commit `.env` file** with credentials
2. Use **app-specific passwords** for Google Workspace
3. Keep Redis **behind firewall** (don't expose to public)
4. Use **SSL/TLS** for Redis in production:
   ```env
   CELERY_BROKER_URL=rediss://localhost:6379/0
   ```

## Monitoring & Logging

### View Task Results:
Django Admin → Django Celery Results → Task Results

### Custom Logging:
Check logs in:
```bash
# Application logs
tail -f /var/log/topgrade/celery.log

# Django logs
tail -f /var/log/topgrade/django.log
```

## Scaling

For high-volume email sending:

1. **Multiple Celery Workers:**
```bash
# Worker 1
celery -A topgrade worker -Q email_queue --loglevel=info

# Worker 2
celery -A topgrade worker -Q email_queue --loglevel=info
```

2. **Separate Queue for Emails:**
```python
@shared_task(bind=True, max_retries=3, queue='email_queue')
def send_certificates_email_task(self, course_progress_id):
    ...
```

3. **Use Professional Email Service:**
- AWS SES
- SendGrid
- Mailgun

## Support

For issues or questions:
- Email: support@topgradeinnovations.com
- Phone: +91 76194 68135 | +91 89044 65305
