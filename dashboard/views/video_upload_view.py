"""
Video upload views for direct S3 uploads
"""
import os
import boto3
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .auth_view import admin_required
import uuid


@admin_required
@require_http_methods(["POST"])
def generate_presigned_url(request):
    """
    Generate presigned URL for direct S3 upload
    """
    try:
        # Get file metadata from request
        file_name = request.POST.get('file_name')
        file_type = request.POST.get('file_type')
        program_subtitle = request.POST.get('program_name', 'untitled')  # Program subtitle
        program_type = request.POST.get('program_type', 'regular')  # 'advanced' or 'regular'
        
        if not file_name or not file_type:
            return JsonResponse({
                'success': False,
                'error': 'File name and type are required'
            }, status=400)
        
        # Check if S3 is enabled
        use_s3 = getattr(settings, 'USE_S3', False)
        
        if not use_s3:
            return JsonResponse({
                'success': False,
                'error': 'S3 upload is not enabled. Please enable USE_S3 in settings.'
            }, status=400)
        
        # Sanitize program subtitle for use in path (remove special characters, convert spaces to underscores)
        import re
        safe_program_subtitle = re.sub(r'[^\w\s-]', '', program_subtitle)
        safe_program_subtitle = re.sub(r'[\s]+', '_', safe_program_subtitle)
        safe_program_subtitle = safe_program_subtitle.lower()
        
        # Sanitize program type (ensure it's either 'advanced' or 'regular')
        program_type = program_type.lower() if program_type.lower() in ['advanced', 'regular'] else 'regular'
        
        # Generate unique file name to prevent overwrites
        file_extension = os.path.splitext(file_name)[1]
        unique_file_name = f"{uuid.uuid4()}{file_extension}"
        
        # Organize by: programs/{advanced|regular}/{program_subtitle}/{unique_filename.ext}
        # Note: No "media/" prefix - Django's MEDIA_URL will handle that
        s3_key = f"programs/{program_type}/{safe_program_subtitle}/{unique_file_name}"
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # Generate presigned URL for PUT operation
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': s3_key,
                'ContentType': file_type,
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        # Return the presigned URL and file path
        # Store only the S3 key (relative path) to work with CloudFront/media domain
        return JsonResponse({
            'success': True,
            'presigned_url': presigned_url,
            's3_key': s3_key,
            'file_url': s3_key  # Store only the key, not the full URL
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@admin_required
@require_http_methods(["POST"])
def confirm_upload(request):
    """
    Confirm that upload is complete and return the file URL
    """
    try:
        s3_key = request.POST.get('s3_key')
        
        if not s3_key:
            return JsonResponse({
                'success': False,
                'error': 'S3 key is required'
            }, status=400)
        
        # Return only the S3 key (relative path)
        # Django's MEDIA_URL will handle the full URL construction
        return JsonResponse({
            'success': True,
            'file_url': s3_key,  # Store only the key, not the full URL
            's3_key': s3_key
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
