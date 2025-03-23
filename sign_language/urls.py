# from django.urls import path
# from . import views

# app_name = "sign_language"

# urlpatterns = [
#     path('', views.index, name='index'),  # Main HandWave AI page
#     path('sign/', views.sign, name='sign'),  # Sign language recognition
#     path('detect/', views.video_feed, name='detect_asl'),  # Start camera and stream
#     path('video_feed/', views.video_feed, name='video_feed'),  # Video feed URL
#     path('predict/', views.predict, name='predict'),  # Predict sign
# ]

from django.urls import path
from . import views

app_name = "sign_language"

urlpatterns = [
    path('', views.index, name='index'),  # Main HandWave AI page
    path('sign/', views.sign, name='sign'),  # Correct path to Sign Language page
    path('detect/', views.video_feed, name='detect_asl'),  # Start camera and stream
    path('video_feed/', views.video_feed, name='video_feed'),  # Video feed URL
    path('predict/', views.predict, name='predict'),  # Predict sign
]
