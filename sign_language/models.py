from django.db import models

# Create your models here.

class Sign(models.Model):
    gesture_name = models.CharField(max_length=50)
    meaning = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

