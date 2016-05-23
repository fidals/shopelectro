"""
shopelectro.ru urlconf.

NOTE: it's better to group related sets of urls into
distinct lists and then include them all at once.
"""

from django.contrib import admin
from django.conf.urls import url, include
from . import views


category_urls = [
    url(r'^(?P<category_slug>[\w-]+)/$',
        views.category_page, name='category'),
    url(r'^(?P<category_slug>[\w-]+)/(?P<sorting>[0-9]*)/$',
        views.category_page, name='category'),
    url(r'^(?P<category_slug>[\w-]+)/load-more/(?P<offset>[0-9]+)/(?P<sorting>[0-9]*)/$',
        views.load_more, name='load_more'),
]

product_urls = [
    url(r'^(?P<product_id>[0-9]+)/$', views.product_page, name='product'),
]

urlpatterns = [
    url(r'^$', views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^set-view-type/$', views.set_view_type, name='set_view_type'),
    url(r'^catalog/categories/', include(category_urls)),
    url(r'^catalog/products/', include(product_urls)),
    url(r'^catalog/', views.catalog_tree, name='catalog'),
    url(r'^blog/', include('blog.urls')),
]
