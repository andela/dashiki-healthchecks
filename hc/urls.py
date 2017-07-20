from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from hc import settings

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('hc.accounts.urls')),
    url(r'^', include('hc.api.urls')),
    url(r'^', include('hc.front.urls')),
    url(r'^', include('hc.payments.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
