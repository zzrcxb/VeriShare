from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^(?P<prefix>[^/]{7,32})/$', views.download, name='download_alias'),
    url(r'^(?P<prefix>[0-9a-zA-Z]{40})/$', views.download, name='download_hash')
]