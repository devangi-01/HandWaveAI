from django.urls import path
from . import views

app_name = "sign_language"

urlpatterns = [
    path('', views.index, name='index'),
    path('sign_language/', views.index, name='sign_language'),  # Loads the page
    path('video_feed/', views.video_feed, name='video_feed'),   # For video streaming
    path('detect_sign/', views.detect_sign, name='detect_sign'),  # Detect sign button
]
