# urlpatterns = [
#     # Main page to load sign recognition interface

#     path('', views.index, name='index'),
#     path('sign_language/', views.index, name='sign_language'),  # Fixed to load the page
#     # API endpoint to handle sign recognition from video frame
#     path('sign_recognition/', views.sign_recognition, name='sign_recognition'),
#     path('get_model_output/', views.get_model_output, name='get_model_output'),
#     path('upload_sign/', views.upload_sign, name='upload_sign'),
# ]

from django.urls import path
from . import views

app_name = "sign_language"

urlpatterns = [
    path('', views.index, name='index'),
    path('sign_language/', views.index, name='sign_language'),  # Loads the page
    path('video_feed/', views.video_feed, name='video_feed'),   # For video streaming
    path('detect_sign/', views.detect_sign, name='detect_sign'),  # Detect sign button
]
