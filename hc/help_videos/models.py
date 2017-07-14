from django.db import models

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    resource_url = models.CharField(max_length=300, blank=False)
    time_stamp = models.DateTimeField(auto_now_add=True)
