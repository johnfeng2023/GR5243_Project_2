from django.urls import path
from .views import home

urlpatterns = [
    path("", home, name="home"),  # This will load index.html at the home page
]

