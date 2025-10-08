from django.urls import path
from .views import api, auth_api

# Import views to register all endpoints
from . import views

urlpatterns = [
    path("", api.urls),
    path("auth/", auth_api.urls),
]