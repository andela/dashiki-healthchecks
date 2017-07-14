from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .models import Video
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
import os
from hc.settings import BASE_DIR

# Create your views here.


def index(request):
    ctx = {
        'section': "help-videos",
        'videos': Video.objects.all()
    }
    return render(request, 'help_videos/videos.html', ctx)

# define admin required decorator


def admin_required(func):
    def wrap(request):
        if request.user.is_superuser:
            return func(request)
        else:
            return HttpResponseForbidden()
    return wrap


def verify_filetype(func):
    def wrap(request):
        file_name = request.FILES["video-file"].name
        ext = file_name.split(".")[-1]
        # can check for more extensions here
        if ext == 'mp4':
            return func(request)
        else:
            return HttpResponse("Only mp4 video files allowed at the moment, .{} file types not allowed".format(ext))

    return wrap


@login_required
@admin_required
@verify_filetype
def upload(request):
    if request.method == 'POST':
        title, desc = request.POST['title'], request.POST['description']
        video = request.FILES['video-file']

        if len(title) < 1 or len(desc) < 1:
            return HttpResponse("Please fill all fields")

        fstorage = FileSystemStorage()
        fname = fstorage.save(video.name, video)
        upload_uri = fstorage.url(fname)

        # Add entry to database
        video = Video(title=title, description=desc, resource_url=upload_uri)
        video.save()
        return HttpResponse("success")
    else:
        return HttpResponse("failed")


@login_required
@admin_required
def delete_video(request):
    if request.method == 'POST':
        request_id = request.POST['id']
        if request_id:
            obj = Video.objects.filter(id=request_id).first()
            # do a hard delete
            os.system("rm -r {}".format("{}{}".format(BASE_DIR,
                                                      obj.resource_url).replace("%20", "\ ")))
            Video.objects.filter(id=request_id).delete()
            return HttpResponse("success".format(BASE_DIR))
        else:
            return HttpResponse("Operation not allowed")
