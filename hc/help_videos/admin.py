from django.contrib import admin
from .models import Video
from hc.help_videos.models import Video

# Register your models here.
admin.site.register(Video)
