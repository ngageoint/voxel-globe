import django.contrib.auth.views
from django.conf.urls import patterns, include, url
import voxel_globe.main.views

urlpatterns = patterns('',
    url(r'^$', voxel_globe.main.views.index, name='index'),
    url(r'^login/$', django.contrib.auth.views.login, {'template_name': 'main/html/login.html'}, name='login'),
    url(r'^logout/$', django.contrib.auth.views.logout, {'template_name': 'main/html/logout.html'}, name='logout'),
    url(r'^password_change/$', django.contrib.auth.views.password_change, 
        {'template_name': 'main/html/change_password_form.html',
         'post_change_redirect': 'main:password_change_done'}, 
        name='password_change'),
    url(r'^password_change_done/$', django.contrib.auth.views.password_change_done, {'template_name': 'main/html/change_password_done.html'}, name='password_change_done'),
)