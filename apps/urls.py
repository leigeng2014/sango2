#-*- coding: utf-8 -*-

from django.conf.urls.defaults import include, patterns, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'^admin/',include('apps.admin.urls'),name = "admin"),
)
#基础页面跳转配置
urlpatterns += patterns('apps.views.main',
    url(r'^index/$','index',name = 'index'),
    url(r'^api/$','api',name = 'api'),
    url(r'^info/$','info',name = 'info'),
    url(r'^select_role/$','select_role',name = 'select_role'),
    url(r'^language_version/$','language_version',name = 'language_version'),
)
#充值
urlpatterns += patterns('apps.views.charge',
    url(r'^charge_ios/$','charge_ios',name = 'charge_ios'),
)

urlpatterns += patterns('',
    (r'^images/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
)

urlpatterns += patterns('',
    url(r'^(?P<path>.*)$','apps.templates_handler',name = 'static_handler'),
)

handler404 = 'apps.views.main.page_not_found'
handler500 = 'apps.views.main.server_error'
