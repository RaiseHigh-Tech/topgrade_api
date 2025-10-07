
from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('programs/', views.programs, name='programs'),
    path('advance_programs/', views.advance_programs, name='advance_programs'),
    path('contact/', views.contact, name='contact'),
    path('programs/<int:program_id>/', views.program_detail, name='program_detail'),
    path('all_programs/', views.program_list, name='program_list'),
    path('certificate-verification/', views.certificate_check, name='certificate_check'),
    path('api/submit-enquiry/', views.submit_program_enquiry, name='submit_program_enquiry'),
    path('api/verify-certificate/', views.verify_certificate, name='verify_certificate'),
]
    
    