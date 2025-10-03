
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
    path('advance_programs/<int:advance_program_id>/', views.advance_program_detail, name='advance_program_detail'),
]
