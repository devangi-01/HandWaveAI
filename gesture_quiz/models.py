from django.db import models

# Create your models here.

class QuizQuestion(models.Model):
    question = models.TextField()
    correct_answer = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
