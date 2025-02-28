from django.urls import path
from .views import gesture_quiz

urlpatterns = [
    path('', gesture_quiz, name='gesture_quiz'),
]