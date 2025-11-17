# SQLite to PostgreSQL Migration Guide

## Quick Migration (Automated)

The easiest way to migrate your data from SQLite to PostgreSQL:

```bash
# 1. Install PostgreSQL adapter
pip install -r requirements.txt

# 2. Setup PostgreSQL database (automated)
chmod +x setup_postgres.sh
./setup_postgres.sh

# 3. Run the migration script
python migrate_sqlite_to_postgres.py

# 4. Update your .env file
# Set USE_POSTGRES=True

# 5. Test your application
python manage.py runserver
```

## What Gets Migrated?

The migration script will transfer:
- ✓ All user accounts and authentication data
- ✓ Custom user profiles
- ✓ All application data (programs, categories, testimonials, etc.)
- ✓ Media file references (files themselves need separate handling)
- ✓ Permissions and groups

**Note**: Content types and permissions are automatically recreated by Django migrations, so they're excluded from the dump to avoid conflicts.

## Prerequisites

1. **Backup your data** (automatically done by the script)
2. **PostgreSQL installed and running**
3. **Python packages installed**: `pip install -r requirements.txt`
4. **Environment variables configured** in `.env` file

## Step-by-Step Process

### Step 1: Prepare Environment

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:
```env
USE_POSTGRES=False  # Keep False for now
DB_NAME=topgrade_db
DB_USER=topgrade_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 2: Setup PostgreSQL

Run the automated setup script:
```bash
./setup_postgres.sh
```

This will:
- Check if PostgreSQL is installed
- Create the database
- Create the database user
- Grant necessary privileges
- Configure timezone (Asia/Kolkata)

### Step 3: Run Migration

Execute the migration script:
```bash
python migrate_sqlite_to_postgres.py
```

The script will guide you through:
1. **Prerequisites check** - Verifies everything is ready
2. **Backup creation** - Creates timestamped backup of SQLite
3. **Data export** - Dumps all data from SQLite
4. **Database setup** - Confirms PostgreSQL is ready
5. **Migrations** - Runs Django migrations on PostgreSQL
6. **Data import** - Loads data into PostgreSQL
7. **Verification** - Checks data integrity
8. **Cleanup** - Optionally removes temporary files

### Step 4: Update Configuration

Edit `.env` and change:
```env
USE_POSTGRES=True
```

### Step 5: Test Application

```bash
# Run the development server
python manage.py runserver

# Test admin panel
# Visit: http://localhost:8000/admin

# Test API endpoints
# Check all critical features
```

## Manual Migration (Alternative)

If you prefer manual control:

### Export from SQLite
```bash
# Ensure using SQLite
export USE_POSTGRES=False

# Create data dump
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.Permission \
  --indent 2 > data_dump.json
```

### Setup PostgreSQL Database
```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database and user
CREATE DATABASE topgrade_db;
CREATE USER topgrade_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE topgrade_db TO topgrade_user;

-- Configure user settings
ALTER ROLE topgrade_user SET client_encoding TO 'utf8';
ALTER ROLE topgrade_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE topgrade_user SET timezone TO 'Asia/Kolkata';

-- For PostgreSQL 15+, grant schema privileges
\c topgrade_db
GRANT ALL ON SCHEMA public TO topgrade_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO topgrade_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO topgrade_user;
```

### Import to PostgreSQL
```bash
# Switch to PostgreSQL
export USE_POSTGRES=True

# Run migrations
python manage.py migrate

# Load data
python manage.py loaddata data_dump.json
```

## Handling Media Files

Media files (uploaded images, videos, etc.) are not included in the database dump. They need to be handled separately:

### If using local storage:
```bash
# Media files are already in the media/ directory
# No action needed - they'll work with PostgreSQL too
```

### If using AWS S3:
```bash
# Media files are in S3
# Update .env with S3 credentials
USE_S3=True
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
```

## Rollback Plan

If something goes wrong, you can easily rollback:

### Option 1: Switch back to SQLite
```env
# In .env file
USE_POSTGRES=False
```

Your original SQLite database is untouched, and a backup was created.

### Option 2: Restore from backup
```bash
# List available backups
ls -la db.sqlite3.backup_*

# Restore a specific backup
cp db.sqlite3.backup_YYYYMMDD_HHMMSS db.sqlite3
```

## Verification Checklist

After migration, verify:

- [ ] Can login to admin panel
- [ ] User accounts are present
- [ ] Programs and categories are visible
- [ ] Images and media files load correctly
- [ ] API endpoints respond correctly
- [ ] Permissions work as expected
- [ ] Timestamps are in correct timezone

## Common Issues and Solutions

### Issue: "psycopg2" not found
```bash
pip install psycopg2-binary
```

### Issue: PostgreSQL connection refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Enable auto-start on boot
sudo systemctl enable postgresql
```

### Issue: Authentication failed
```bash
# Check PostgreSQL authentication method
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Change 'peer' to 'md5' for local connections
# local   all   all   md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Issue: Database already exists
```bash
# Drop and recreate
sudo -u postgres psql -c "DROP DATABASE topgrade_db;"
sudo -u postgres psql -c "CREATE DATABASE topgrade_db;"
```

### Issue: Foreign key violations during loaddata
```bash
# This shouldn't happen with --natural-foreign flag
# But if it does, load data in specific order:

# 1. Load auth and user data first
python manage.py loaddata auth_data.json

# 2. Load application data
python manage.py loaddata app_data.json
```

## Performance Considerations

### For Large Databases

If you have a large database (>1GB or >100k records):

1. **Increase timeout in settings.py**:
```python
DATABASES = {
    'default': {
        # ... other settings ...
        'OPTIONS': {
            'connect_timeout': 60,  # Increase from 10
        },
    }
}
```

2. **Use bulk operations**:
```bash
# Split data into smaller chunks
python manage.py dumpdata app1 > app1_data.json
python manage.py dumpdata app2 > app2_data.json

# Load separately
python manage.py loaddata app1_data.json
python manage.py loaddata app2_data.json
```

3. **Disable constraints temporarily**:
```sql
-- During large imports
SET CONSTRAINTS ALL DEFERRED;
```

## Production Deployment

### Environment Variables for Production
```env
# Production settings
DEBUG=False
USE_POSTGRES=True
SECRET_KEY=your_production_secret_key

# Database
DB_NAME=topgrade_prod
DB_USER=topgrade_prod_user
DB_PASSWORD=strong_password_here
DB_HOST=your_db_host
DB_PORT=5432

# Allowed hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# AWS S3 (recommended for production)
USE_S3=True
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
```

### Security Best Practices

1. **Use environment-specific settings**:
   - Development: SQLite, DEBUG=True
   - Staging: PostgreSQL, DEBUG=True
   - Production: PostgreSQL, DEBUG=False

2. **Database security**:
   - Use strong passwords
   - Restrict database access by IP
   - Use SSL for database connections
   - Regular backups

3. **Never commit sensitive data**:
   ```bash
   # Add to .gitignore
   .env
   db.sqlite3
   *.backup
   data_dump.json
   ```

## Backup Strategy

### Automated Backups

Create a backup script (`backup_postgres.sh`):
```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U topgrade_user topgrade_db > "$BACKUP_DIR/backup_$DATE.sql"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

Add to crontab for daily backups:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup_postgres.sh
```

## Support and Resources

- **Django Databases**: https://docs.djangoproject.com/en/5.2/ref/databases/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **psycopg2 Docs**: https://www.psycopg.org/docs/

For project-specific issues, see `DATABASE_SETUP.md` or contact the development team.
