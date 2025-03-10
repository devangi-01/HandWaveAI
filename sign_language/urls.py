from django.urls import path
from .views import sign_language_recognition
from .views import video_feed, index

urlpatterns = [
    # path('', sign_language_recognition, name='sign_language_recognition'),
    path('', index, name='index'),
    path('sign-language/', sign_language_recognition, name='sign_language_recognition'),
    path('detect/', video_feed, name='detect_asl'),
]




# from django.urls import path
# from .views import stream_video, index

# urlpatterns = [
#     path('', index, name="index"),  # Renders HTML page
#     path('video_feed/', stream_video, name="video_feed"),  # Streams ASL recognition
# ]
