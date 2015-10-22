# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.conf import settings


urlpatterns = patterns('apps.admin.views.main',
    url(r'^$','index'),
    url(r'^api/$','api', name='admin_api'),
    url(r'^login/$','login'),
    url(r'^logout/$','logout'),
    url(r'^left/$','left'),
    url(r'^main/$','main'),
    url(r'^moderator/moderator_list/$','moderator_list'),
    url(r'^moderator/agree_inreview/$','agree_inreview'),
    url(r'^moderator/manage_moderator/$','manage_moderator'),
    url(r'^moderator/manage_moderator_done/$','manage_moderator_done'),
    url(r'^change_password/$','change_password'),
    url(r'^registration/$','registration'),
    url(r'^moderator/view_permissions/$','moderator_permissions'),
    url(r'^moderator/add_moderator/$','add_moderator'),
    url(r'^moderator/add_moderator_done/$','add_moderator_done'),
    url(r'^moderator/delete_moderator/$','delete_moderator'),
    url(r'^moderator/delete_moderator_done/$','delete_moderator_done'),
    url(r'^game_setting/$', 'game_setting'),
)

urlpatterns += patterns('apps.admin.views.user',
    url(r'^user/$', 'index'),
    url(r'^user/edit/$', 'edit_user'),
    url(r'^user/view/$', 'view_user'),
)

urlpatterns += patterns('apps.admin.views.tool',
    url(r'^tool/$', 'index'),
    url(r'^tool/gacha/$', 'gacha'),
)

urlpatterns += patterns('apps.admin.views.makegameconfig',
    url(r'^makegameconfig/$', 'makegameconfig'),
    url(r'^make_single_config/$', 'make_single_config'),
    url(r'^make_single_config_old/$', 'make_single_config_old'),
    url(r'^is_dict/$', 'is_dict'),
)

urlpatterns += patterns('',
    (r'^(?P<path>.*)$','django.views.static.serve',{'document_root':settings.BASE_ROOT + '/apps/admin/'}),
)
