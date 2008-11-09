from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login, logout, password_change

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'music_server.views.index', name='index'),
    url(r'^a/youtube', 'music_server.views.youtube', name='youtube'),
    url(r'^a/xhr_queue', 'music_server.views.xhr_queue', name='xhr-queue'),

    url(r'^a/item/delete/(?P<item_id>\d+)$', 'music_server.views.delete', name='delete-item'),
    url(r'^a/item/(?P<direction>(up|down))/(?P<item_id>\d+)$', 'music_server.views.move', name='move-item'),

    url(r'^a/register', 'music_server.views.register', name='register'),

    url(r'^a/login$', login, name='login'),
    url(r'^a/logout$', logout, {'template_name': 'registration/logged_out.html'}, name='logout'),
    url(r'^a/password_change$', password_change, {
        'template_name' : 'registration/password_change.html',
        'post_change_redirect': 'done/',
    }, name='password_change'),
    url(r'^a/password_changed$', direct_to_template,
        {'template': 'registration/password_changed.html'}, name='password_change_success'),

    url(r'^a/admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': './site_media/', 'show_indexes': True}),
    )
