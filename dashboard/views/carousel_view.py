from .auth_view import admin_required
from django.shortcuts import render

@admin_required
def carousel_view(request):
    """Carousel view for dashboard"""
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/carousel.html', context)