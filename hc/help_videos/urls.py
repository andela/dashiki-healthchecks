#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: urls.py
# Author: Collins Abitekaniza <abtcolns@gmail.com>
# Date: 03.07.2017
# Last Modified: 03.07.2017

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='hc-help-videos'),
    url(r'^upload$', views.upload, name="hc-help-videos-upload")
]
