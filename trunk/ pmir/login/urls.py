# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'input', 'pms.login.views.user_login'),
    (r'register/$', 'pms.login.views.user_register'),
    (r'loaddata/$', 'pms.login.views.loadData'),
    (r'logout/$', 'pms.login.views.user_logout'),
)
