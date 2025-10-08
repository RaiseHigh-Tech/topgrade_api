"""
Carousel and website content API views
"""
from django.http import JsonResponse
from topgrade_api.models import Carousel
from .common import api

@api.get("/carousel")
def get_carousel_data(request):
    """
    Get carousel data for the website
    No authentication required - public endpoint
    """
    try:
        # Get all active carousel items ordered by position
        carousel_items = Carousel.objects.filter(is_active=True).order_by('order', 'id')
        
        carousel_data = []
        for item in carousel_items:
            item_data = {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "image": item.image.url if item.image else None,
                "button_text": item.button_text,
                "button_link": item.button_link,
                "order": item.order,
                "is_active": item.is_active
            }
            carousel_data.append(item_data)
        
        return {
            "success": True,
            "count": len(carousel_data),
            "carousel_items": carousel_data
        }
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error fetching carousel data: {str(e)}"}, status=500)