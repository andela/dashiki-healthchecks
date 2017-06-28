from django.conf.urls import url, include

from hc.api import views
from hc.api.v1.channels_endpoint import channels_router

urlpatterns = [
    url(r'^ping/([\w-]+)/$', views.ping, name="hc-ping-slash"),
    url(r'^ping/([\w-]+)$', views.ping, name="hc-ping"),
    url(r'^api/v1/checks/$', views.checks),
    url(r'^api/v1/checks/([\w-]+)/pause$', views.pause, name="hc-api-pause"),
    url(r'^api/v1/', include(channels_router.urls)),
    url(r'^badge/([\w-]+)/([\w-]{8})/([\w-]+).svg$', views.badge, name="hc-badge"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
