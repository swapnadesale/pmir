from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^pms/', include('pms.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
    (r'index/$', 'pms.website.views.index'),
    (r'personal/$', 'pms.website.views.personal'),
    (r'clickrecord/$', 'pms.website.views.clickrecord'),
    (r'control/$', 'pms.website.views.control'),
    (r'google/$', 'pms.website.views.googleResult'),
    (r'baidu/$', 'pms.website.views.baiduResult'),
    (r'inputpage/$', 'pms.website.views.inputpage'),   
    (r'psudoFeedback/$', 'pms.website.views.psudoFeedback'),
    (r'userFeedback/$', 'pms.website.views.userFeedback'),
)
