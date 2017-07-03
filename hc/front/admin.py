from django.contrib import admin
from hc.front.models import (FaqCategory, FaqItem)

admin.site.register([FaqCategory, FaqItem])
