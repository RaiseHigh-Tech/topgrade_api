# AWS S3 Configuration Guide

This guide will help you set up AWS S3 for storing media files in your Django project.

## Prerequisites

1. AWS Account
2. AWS CLI installed (optional but recommended)
3. Python packages installed: `boto3` and `django-storages`

## Step 1: Create S3 Bucket

1. Log into AWS Console
2. Navigate to S3 service
3. Click "Create bucket"
4. Choose a unique bucket name (e.g., `topgrade-media-files`)
5. Select your preferred region
6. Keep default settings or configure as needed
7. Create the bucket

## Step 2: Create IAM User

1. Navigate to IAM service in AWS Console
2. Click "Users" → "Add user"
3. Choose a username (e.g., `topgrade-s3-user`)
4. Select "Programmatic access"
5. Attach policy: `AmazonS3FullAccess` (or create custom policy for specific bucket)
6. Complete user creation
7. **Important**: Save the Access Key ID and Secret Access Key

## Step 3: Configure Django Settings

### Environment Variables

Create a `.env` file in your project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Update the following variables in your `.env` file:

```
AWS_ACCESS_KEY_ID=your_actual_access_key_id
AWS_SECRET_ACCESS_KEY=your_actual_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_bucket_region
USE_S3=true
```

### Load Environment Variables

Add this to your `settings.py` (already configured):

```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Test Configuration

### Test S3 Connection

Create a test script to verify S3 connection:

```python
import boto3
from django.conf import settings

def test_s3_connection():
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # List buckets to test connection
        response = s3.list_buckets()
        print("S3 Connection successful!")
        print("Available buckets:", [bucket['Name'] for bucket in response['Buckets']])
        return True
    except Exception as e:
        print(f"S3 Connection failed: {e}")
        return False
```

## Step 6: Bucket Policy (Optional)

For public read access to media files, add this bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/media/*"
        }
    ]
}
```

## Step 7: CORS Configuration (If needed)

Add CORS configuration to your S3 bucket:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "POST", "PUT"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## Usage

### Development Mode
Set `USE_S3=false` in your `.env` file to use local storage.

### Production Mode
Set `USE_S3=true` in your `.env` file to use S3 storage.

### File Upload Example

```python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Upload file
file_name = default_storage.save('uploads/example.txt', ContentFile(b'Hello World'))
file_url = default_storage.url(file_name)
print(f"File uploaded: {file_url}")
```

## Security Best Practices

1. **Never commit AWS credentials to version control**
2. Use IAM roles in production instead of hardcoded credentials
3. Create specific IAM policies with minimal required permissions
4. Enable S3 bucket versioning
5. Enable S3 server access logging
6. Consider using AWS Secrets Manager for credential management

## Troubleshooting

### Common Issues

1. **Access Denied**: Check IAM permissions
2. **Bucket Not Found**: Verify bucket name and region
3. **Invalid Credentials**: Verify AWS Access Key and Secret
4. **CORS Errors**: Configure CORS policy on S3 bucket

### Debug Mode

Add this to your Django settings for debugging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'boto3': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Cost Optimization

1. Use S3 lifecycle policies to transition old files to cheaper storage classes
2. Monitor usage with AWS Cost Explorer
3. Consider using CloudFront CDN for frequently accessed files
4. Set up S3 request metrics to track usage patterns