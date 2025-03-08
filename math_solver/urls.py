from django.urls import path
from . import views
from .views import get_ai_output

app_name = "math_solver"

urlpatterns = [
    path('', views.math_solver, name='math_solver'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get-ai-output/', views.get_ai_output, name='get_ai_output'),
    path('get_ai_output/', get_ai_output, name='get_ai_output1')   
]

