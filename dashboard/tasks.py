"""
Celery tasks for dashboard operations
"""
from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from topgrade_api.models import UserCertificate, UserCourseProgress
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_certificates_email_task(self, course_progress_id):
    """
    Send certificates via email as attachments.
    This task runs in the background using Celery.
    """
    try:
        # Get course progress
        course_progress = UserCourseProgress.objects.get(id=course_progress_id, is_completed=True)
        
        # Get all certificates for this course progress
        certificates = UserCertificate.objects.filter(
            user=course_progress.user,
            course_progress=course_progress,
            program=course_progress.purchase.program,
        )
        
        if not certificates.exists():
            logger.error(f"No certificates found for course progress ID: {course_progress_id}")
            return {
                'success': False,
                'message': 'No certificates found'
            }
        
        # Prepare email
        student_name = course_progress.user.fullname or course_progress.user.email
        student_email = course_progress.user.email
        program_name = course_progress.purchase.program.title
        
        subject = f"Certificates of Completion - {program_name} - TopGrade Innovation"
        
        message = f"""Dear {student_name},

Congratulations on successfully completing the "{program_name}" program with TopGrade 
Innovation Pvt. Ltd. We appreciate your dedication and commitment throughout the training 
or internship period.

Your Certificates of Completion are attached to this email. Every certificate issued by 
TopGrade Innovation includes a unique verification ID.

To confirm the authenticity of your certificate, please visit our official verification portal:

    🔗 https://www.topgradeinnovation.com/certificate-verification/

You may enter the verification ID shown on your certificate to validate its authenticity.


═══════════════════════════════════════════════════════════════════════════════

                                ⚠️  IMPORTANT NOTICE

═══════════════════════════════════════════════════════════════════════════════

This is an automated message sent from noreply@topgradeinnovations.com
Please do not reply to this email.


For any assistance or queries, kindly contact our support team:

    📧  Email   : support@topgradeinnovations.com
    📞  Phone   : +91 76194 68135  |  +91 89044 65305


═══════════════════════════════════════════════════════════════════════════════


Thank you for being a part of TopGrade Innovation.
We wish you continued success in your future endeavors.


Best regards,
TopGrade Innovation Pvt. Ltd.
"""
        
        # Create email
        # Use EMAIL_HOST_USER as from_email to avoid SPF/DMARC issues
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[student_email],
        )
        
        # Attach all certificates
        attached_count = 0
        for certificate in certificates:
            if certificate.certificate_file:
                try:
                    # Get the file content
                    certificate.certificate_file.open('rb')
                    file_content = certificate.certificate_file.read()
                    certificate.certificate_file.close()
                    
                    # Get filename
                    filename = f"{certificate.get_certificate_type_display()}_{certificate.certificate_number}.pdf"
                    
                    # Attach to email
                    email.attach(filename, file_content, 'application/pdf')
                    attached_count += 1
                except Exception as e:
                    logger.error(f"Error attaching certificate {certificate.id}: {str(e)}")
        
        if attached_count == 0:
            logger.error(f"No certificate files could be attached for course progress ID: {course_progress_id}")
            return {
                'success': False,
                'message': 'No certificate files available to attach'
            }
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f"Successfully sent {attached_count} certificates to {student_email}")
        
        return {
            'success': True,
            'message': f'Successfully sent {attached_count} certificates to {student_name}',
            'email': student_email,
            'certificates_count': attached_count
        }
        
    except UserCourseProgress.DoesNotExist:
        logger.error(f"Course progress not found: {course_progress_id}")
        return {
            'success': False,
            'message': 'Course progress not found'
        }
    except Exception as e:
        logger.error(f"Error sending certificates email: {str(e)}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
