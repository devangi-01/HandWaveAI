from django.urls import path
from . import views

urlpatterns = [
    path('', views.math_solver, name='math_solver'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get-ai-output/', views.get_ai_output, name='get_ai_output'),

   
]

