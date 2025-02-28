from django.urls import path
from .views import sign_language_recognition

urlpatterns = [
    path('', sign_language_recognition, name='sign_language_recognition'),
]
# from django.urls import path
# from .views import stream_video, index

# urlpatterns = [
#     path('', index, name="index"),  # Renders HTML page
#     path('video_feed/', stream_video, name="video_feed"),  # Streams ASL recognition
# ]
