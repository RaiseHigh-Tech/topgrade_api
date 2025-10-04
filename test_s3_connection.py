#!/usr/bin/env python
"""
Test script to verify AWS S3 connection and configuration
Run this script from the Django project root directory
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topgrade.settings')
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def test_s3_connection():
    """Test AWS S3 connection and configuration"""
    print("🔧 Testing AWS S3 Configuration...")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Checking Environment Variables:")
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = getattr(settings, var, None)
        if value:
            if var == 'AWS_SECRET_ACCESS_KEY':
                print(f"  ✅ {var}: {'*' * min(len(str(value)), 20)}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or environment configuration.")
        return False
    
    # Test S3 connection
    print(f"\n🔌 Testing S3 Connection:")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Test connection by listing buckets
        response = s3_client.list_buckets()
        print("  ✅ S3 connection successful!")
        
        # Check if our bucket exists
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        
        if bucket_name in buckets:
            print(f"  ✅ Bucket '{bucket_name}' found!")
        else:
            print(f"  ❌ Bucket '{bucket_name}' not found!")
            print(f"  Available buckets: {', '.join(buckets)}")
            return False
            
    except NoCredentialsError:
        print("  ❌ Invalid AWS credentials!")
        return False
    except ClientError as e:
        print(f"  ❌ AWS Client Error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False
    
    # Test bucket permissions
    print(f"\n🔐 Testing Bucket Permissions:")
    try:
        # Test if we can list objects in the bucket
        s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, MaxKeys=1)
        print("  ✅ List objects permission: OK")
        
        # Test if we can put objects
        test_key = 'test/connection_test.txt'
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key,
            Body=b'Test file for connection verification',
            ContentType='text/plain'
        )
        print("  ✅ Put object permission: OK")
        
        # Clean up test file
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=test_key
        )
        print("  ✅ Delete object permission: OK")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"  ❌ Permission error ({error_code}): {e}")
        return False
    
    # Test Django storage backend
    print(f"\n🐍 Testing Django Storage Backend:")
    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        # Test file upload
        test_content = ContentFile(b'Hello from Django S3 test!')
        file_name = default_storage.save('test/django_test.txt', test_content)
        file_url = default_storage.url(file_name)
        
        print(f"  ✅ File uploaded successfully!")
        print(f"  📁 File name: {file_name}")
        print(f"  🔗 File URL: {file_url}")
        
        # Test file exists
        if default_storage.exists(file_name):
            print("  ✅ File exists check: OK")
        else:
            print("  ❌ File exists check: Failed")
            
        # Clean up test file
        default_storage.delete(file_name)
        print("  ✅ File cleanup: OK")
        
    except Exception as e:
        print(f"  ❌ Django storage test failed: {e}")
        return False
    
    print(f"\n🎉 All tests passed! AWS S3 is properly configured.")
    print(f"📊 Configuration Summary:")
    print(f"  - Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"  - Region: {settings.AWS_S3_REGION_NAME}")
    print(f"  - Use S3: {getattr(settings, 'USE_S3', False)}")
    print(f"  - Media URL: {settings.MEDIA_URL}")
    
    return True


if __name__ == '__main__':
    print("AWS S3 Connection Test")
    print("=" * 50)
    
    success = test_s3_connection()
    
    if success:
        print("\n✅ S3 configuration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ S3 configuration has issues. Please check the errors above.")
        sys.exit(1)