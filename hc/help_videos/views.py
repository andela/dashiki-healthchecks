from django.shortcuts import render

# Create your views here.


def index(request):
    ctx = {
        'section': "help-videos"
    }
    return render(request, 'help_videos/videos.html', ctx)


def upload(request):
    if request.method == 'POST':
        pass
    pass
