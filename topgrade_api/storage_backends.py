"""
Custom storage backends for AWS S3 integration
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """Custom S3 storage backend for media files"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False


class StaticStorage(S3Boto3Storage):
    """Custom S3 storage backend for static files"""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True  # Static files can be overwritten