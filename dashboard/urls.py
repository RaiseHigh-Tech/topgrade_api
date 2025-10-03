from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard authentication
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.dashboard_logout, name='logout'),
    
    # Dashboard main views
    path('', views.dashboard_home, name='dashboard'),
    path('edit_category/<int:id>', views.edit_category_view, name='edit_category'),
    path('delete_category/<int:id>', views.delete_category_view, name='delete_category'),
    path('programs/', views.programs_view, name='programs'),
    path('edit_program/<int:id>', views.edit_program_view, name='edit_program'),
    path('delete_program/<int:id>', views.delete_program_view, name='delete_program'),
    path('students/', views.students_view, name='students'),
    path('student/<int:student_id>/', views.student_details_view, name='student_details'),
    path('assign-programs/', views.assign_programs_view, name='assign_programs'),
    path('chat/', views.chat_view, name='chat'),
    path('carousel/', views.carousel_view, name='carousel'),
    path('program/<int:program_id>/', views.program_details_view, name='program_details'),
    
    # Testimonials management
    path('testimonials/', views.testimonials_view, name='testimonials'),
    path('testimonials/add/', views.add_testimonial, name='add_testimonial'),
    path('testimonials/edit/<int:testimonial_id>/', views.edit_testimonial, name='edit_testimonial'),
    path('testimonials/delete/<int:testimonial_id>/', views.delete_testimonial, name='delete_testimonial'),
    path('testimonials/toggle/<int:testimonial_id>/', views.toggle_testimonial_status, name='toggle_testimonial_status')
]   