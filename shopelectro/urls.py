from django.conf.urls import url, include
from .views import index
from django.contrib import admin

urlpatterns = [
    url(r'^$', index),
    url(r'^admin/', admin.site.urls),
    url(r'^catalog/', include('catalog.urls')),
    url(r'^blog/', include('blog.urls')),
]
