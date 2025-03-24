from django.db import models

# Create your models here.
class Video(models.Model):
    videoId = models.CharField(max_length=200)
    link = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000)
    thumbnail = models.CharField(max_length=1000)