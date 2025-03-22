from django.urls import path
from .views import video_feed, index
from . import views

urlpatterns = [
    # path('', sign_language_recognition, name='sign_language_recognition'),
    
    path('sign-language/', views.sign_language_recognition, name='sign_language_recognition'),
    path('detect/', views.video_feed, name='detect_asl'),
    path('', views.index, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('predict/', views.predict, name='predict'),
]


