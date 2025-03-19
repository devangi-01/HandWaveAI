from django.urls import path
from . import views
from .views import get_ai_output
from .views import upload_math_problem

app_name = "math_solver"

urlpatterns = [
    path('', views.math_solver, name='math_solver'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('get-ai-output/', views.get_ai_output, name='get_ai_output'),
    path('get_ai_output/', get_ai_output, name='get_ai_output1'),  
    path("upload-math-problem/", upload_math_problem, name="upload_math_problem"), 
]

