from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .models import Video
from django.http import HttpResponse

# Create your views here.


def index(request):
    ctx = {
        'section': "help-videos"
    }
    return render(request, 'help_videos/videos.html', ctx)


def upload(request):
    if request.method == 'POST':
        title, desc = request.POST['title'], request.POST['description']
        video = request.FILES['video-file']

        fstorage = FileSystemStorage()
        fname = fstorage.save(video.name, video)
        upload_uri = fstorage.url(fname)

        # Add entry to database
        video = Video(title=title, description=desc, resource_url=upload_uri)
        video.save()
        return HttpResponse("success")
    else:
        return HttpResponse("failed")
