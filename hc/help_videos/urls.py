from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='hc-help-videos'),
    url(r'^upload$', views.upload, name="hc-help-videos-upload"),
    url(r'^delete$', views.delete_video, name="hc-delete-video")
]
