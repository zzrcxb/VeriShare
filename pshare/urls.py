from django.conf.urls import url

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  url(r'^upload/$', views.upload, name='upload'),
                  url(r'^(?P<prefix>[\w\d_-]{7,32})/$', views.download_page, name='download page alias'),
                  url(r'^(?P<prefix>[0-9a-zA-Z]{40})/$', views.download_page, name='download page hash'),
                  url(r'^(?P<prefix>[\w\d_-]{7,32})/(?P<method>(preview|download))/$', views.download, name='download alias'),
                  url(r'^(?P<prefix>[0-9a-zA-Z]{40})/(?P<method>(preview|download))/$', views.download, name='download hash'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
