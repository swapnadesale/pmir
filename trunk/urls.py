from django.conf.urls.defaults import *

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
    (r'^pms/$', 'pms.website.views.index'),
    (r'^pms/control/', 'pms.website.views.control'),
    (r'^pms/googleresult/', 'pms.website.views.googleResult'),
    (r'^pms/baiduresult/', 'pms.website.views.baiduResult'),
    #(r'^pms/control/', 'pms.website.views.control'),
    #(r'^wiki/(?P<pagename>\w+)/$', 'pms.website.views.index'),
)
