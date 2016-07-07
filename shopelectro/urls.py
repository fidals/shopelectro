"""
shopelectro.ru urlconf.

NOTE: it's better to group related sets of urls into
distinct lists and then include them all at once.
"""

from collections import OrderedDict
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

from . import views, sitemaps, config
from .cart import recalculate_price
from shopelectro import views, sitemaps, config


category_urls = [
    url(r'^$', views.CategoryTree.as_view(), name='category_tree'),
    url(r'^categories/(?P<slug>[\w-]+)/$',
        views.CategoryPage.as_view(), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/(?P<sorting>[0-9]*)/$',
        views.CategoryPage.as_view(), name='category'),
    url(r'categories/^(?P<category_slug>[\w-]+)/load-more/'
        r'(?P<offset>[0-9]+)/(?P<sorting>[0-9]*)/$',
        views.load_more, name='load_more'),
]

# Orders sitemaps instances
sitemaps = OrderedDict([
    ('index', sitemaps.IndexSitemap),
    ('category', sitemaps.CategorySitemap),
    ('products', sitemaps.ProductSitemap),
    ('site', sitemaps.PagesSitemap)
])

cached_view = cache_page(config.cached_time())

service_urls = [
    url(r'^ya-kassa/aviso/$', views.yandex_aviso, name='yandex_aviso'),
    url(r'^ya-kassa/check/$', views.yandex_check, name='yandex_check'),
    url(r'^ya-feedback/redirect/$',
        views.ya_feedback_with_redirect, name='ya_feedback_with_redirect'),
    url(r'^ya-feedback/request/$',
        views.ya_feedback_request, name='ya_feedback_request'),
]

search_urls = [
    url(r'^autocomplete/$', views.Autocomplete.as_view(), name='autocomplete'),
    url(r'^$', views.Search.as_view(), name='search'),
]

ecommerce_urls = [
    url(r'^cart-add/$', views.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', views.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', views.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', views.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order/$', views.OrderPage.as_view(), name='order_page'),
    url(r'^order-call/$', views.order_call),
    url(r'^one-click-buy/$', views.one_click_buy),
    url(r'^yandex-order/$', views.yandex_order),
]

admin_urls = [
    url(r'^remove-image/$', views.admin_remove_image),
    url(r'^autocomplete/', views.AdminAutocomplete.as_view()),
    url(r'^uploads/$', views.admin_upload_images, name='admin_upload'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^test-ya-kassa/$', views.test_yandex, name='test_yandex'),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/', include(admin_urls)),
    url(r'^set-view-type/$', views.set_view_type, name='set_view_type'),
    url(r'^catalog/', include(category_urls)),
    url(r'^catalog/products/(?P<product_id>[0-9]+)/$',
        views.ProductPage.as_view(), name='product'),
    url(r'^pages/', include('pages.urls')),
    url(r'^shop/', include(ecommerce_urls)),
    url(r'^shop/', include('ecommerce.urls')),
    url(r'^sitemap\.xml$', cached_view(sitemap), {
        'sitemaps': sitemaps
    }),
    url(r'^search/', include(search_urls)),
    url(r'^service/', include(service_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
