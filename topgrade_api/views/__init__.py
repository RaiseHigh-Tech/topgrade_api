# Import all view modules to register their endpoints
from . import (
    auth_views,
    category_view,
    program_view,
    bookmark_view,
    purchase_view,
    learning_view,
    carousel_view,
    area_of_interest_view
)

# Export the API instances for URL configuration
from .common import api
from .auth_views import auth_api

__all__ = [
    'api',
    'auth_api',
    'auth_views',
    'category_view',
    'program_view',
    'bookmark_view',
    'purchase_view',
    'learning_view',
    'carousel_view',
    'area_of_interest_view'
]