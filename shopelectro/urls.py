"""
shopelectro.ru urlconf.

NOTE: it's better to group related sets of urls into
distinct lists and then include them all at once.
"""

from collections import OrderedDict
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

from pages.views import robots
from pages.models import Page

from shopelectro import sitemaps, config
from shopelectro.admin import custom_admin_site
from shopelectro.views import admin, catalog, ecommerce, search, helpers, service


admin_urls = [
    url(r'^', custom_admin_site.urls),
    url(r'^autocomplete/$', search.AdminAutocomplete.as_view()),
    url(r'^get-table-editor-data/$', admin.admin_table_editor_data),
    url(r'^get-tree-items/$', admin.admin_tree_items),
    url(r'^product-create/$', admin.admin_create_product),
    url(r'^product-update/$', admin.admin_update_product),
    url(r'^product-delete/$', admin.admin_delete_product),
    url(r'^remove-image/$', admin.admin_remove_image),
    url(r'^uploads/(?P<model_name>[\w-]+)/(?P<entity_id>[0-9]+)$', admin.admin_upload_images,
        name='admin_upload'),
]

catalog_urls = [
    url(r'^categories/(?P<slug>[\w-]+)/$',
        catalog.CategoryPage.as_view(), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/(?P<sorting>[0-9]*)/$',
        catalog.CategoryPage.as_view(), name='category'),
    url(r'categories/(?P<category_slug>[\w-]+)/load-more/'
        r'(?P<offset>[0-9]+)/(?P<sorting>[0-9]*)/$',
        catalog.load_more, name='load_more'),
    url(r'^products/(?P<product_id>[0-9]+)/$',
        catalog.ProductPage.as_view(), name='product'),
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
    url(r'^ya-kassa/aviso/$', service.yandex_aviso, name='yandex_aviso'),
    url(r'^ya-kassa/check/$', service.yandex_check, name='yandex_check'),
    url(r'^ya-feedback/redirect/$',
        service.ya_feedback_with_redirect, name='ya_feedback_with_redirect'),
    url(r'^ya-feedback/request/$',
        service.ya_feedback_request, name='ya_feedback_request'),
]

search_urls = [
    url(r'^autocomplete/$', search.Autocomplete.as_view(), name='autocomplete'),
]

ecommerce_urls = [
    url(r'^cart-add/$', ecommerce.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', ecommerce.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', ecommerce.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', ecommerce.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order-call/$', ecommerce.order_call),
    url(r'^one-click-buy/$', ecommerce.one_click_buy),
    url(r'^yandex-order/$', ecommerce.YandexOrder.as_view()),
    url(r'', include('ecommerce.urls')),
]

url_name = Page.CUSTOM_PAGES_URL_NAME
custom_pages = [
    url(r'^(?P<page>)$', catalog.IndexPage.as_view(), name=url_name),
    url(r'^(?P<page>search)/$', search.Search.as_view(), name=url_name),
    url(r'^(?P<page>catalog)/$', catalog.CategoryTree.as_view(), name=url_name),
    url(r'^shop/(?P<page>order)/$', ecommerce.OrderPage.as_view(), name=url_name),
    url(r'^shop/(?P<page>success-order)/$', ecommerce.SuccessOrder.as_view(), name=url_name),
]

urlpatterns = [
    url('', include(custom_pages)),
    url(r'^admin/', include(admin_urls)),
    url(r'^catalog/', include(catalog_urls)),
    url(r'^pages/', include('pages.urls')),
    url(r'^robots\.txt$', robots),
    url(r'^set-view-type/$', helpers.set_view_type, name='set_view_type'),
    url(r'^shop/', include(ecommerce_urls)),
    url(r'^search/', include(search_urls)),
    url(r'^service/', include(service_urls)),
    url(r'^sitemap\.xml$', cached_view(sitemap), {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
