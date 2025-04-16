# from django.urls import path
# from .views import gesture_quiz, video_feed, get_final_score, get_quiz_state  # Import only necessary views

# app_name = 'gesture_quiz'

# urlpatterns = [
#     path('', gesture_quiz, name='gesture_quiz'),
#     path("video_feed/", video_feed, name="video_feed"),
#     path('get_final_score/', get_final_score, name='get_final_score'),
#     path('get_quiz_state/', get_quiz_state, name='get_quiz_state'), 
# ]

from django.urls import path
from . import views

app_name = 'gesture_quiz'

urlpatterns = [
    path('', views.gesture_quiz, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get_quiz_state/', views.get_quiz_state, name='get_quiz_state'),
    path('get_final_score/', views.get_final_score, name='get_final_score'),
    # path('restart/', views.restart_quiz, name='restart_quiz'),
]
