from django.conf.urls import url

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^(?P<prefix>[/w/d_-]{7,32})/$', views.download, name='download_alias'),
    url(r'^(?P<prefix>[0-9a-zA-Z]{40})/$', views.download, name='download_hash')
] +  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
