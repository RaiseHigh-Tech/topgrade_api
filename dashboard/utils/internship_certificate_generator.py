import os
from io import BytesIO
from datetime import datetime
from django.core.files.base import ContentFile
from django.conf import settings
from django.template.loader import render_to_string

from weasyprint import HTML


def generate_certificate_pdf(user, program, certificate_number, completion_date=None):
    """
    Generate a PDF certificate for a student using HTML template
    
    Args:
        user: CustomUser object (student)
        program: Program object
        certificate_number: Unique certificate number
        completion_date: Date of course completion (defaults to today)
    
    Returns:
        ContentFile object containing the PDF
    """
    # Set completion date
    if completion_date:
        date_str = completion_date.strftime("%B %d, %Y")
    else:
        date_str = datetime.now().strftime("%B %d, %Y")
    
    # Student name
    student_name = user.fullname or user.email.split('@')[0]
    
    # Program name
    program_name = f"{program.title} {program.subtitle}"
    
    # Prepare context for template
    context = {
        'student_name': student_name,
        'program_name': program_name,
        'certificate_number': certificate_number,
        'completion_date': date_str,
    }
    
    # Render HTML template
    html_string = render_to_string('certificates/internship_certificate_template.html', context)
    
    # Generate PDF from HTML
    html = HTML(string=html_string)
    pdf_bytes = html.write_pdf()
    
    # Create a ContentFile from the PDF data
    filename = f"certificate_{certificate_number}.pdf"
    return ContentFile(pdf_bytes, name=filename)
