"""
shopelectro.ru urlconf.

NOTE: it's better to group related sets of urls into
distinct lists and then include them all at once.
"""

from collections import OrderedDict

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page

from pages.models import Page
from pages.views import robots, SitemapPage

from shopelectro import sitemaps, config, views
from shopelectro.admin import se_admin_site

admin_urls = [
    url(r'^', se_admin_site.urls),
    url(r'^autocomplete/$', views.AdminAutocomplete.as_view()),
    url(r'^get-tree-items/$', views.Tree.as_view()),
    url(r'^redirect-to-product/$', views.RedirectToProduct.as_view()),
    url(r'^table-editor-api/$', views.TableEditorAPI.as_view()),
]

catalog_urls = [
    url(r'^categories/(?P<slug>[\w-]+)/$',
        views.CategoryPage.as_view(), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/(?P<sorting>[0-9]*)/$',
        views.CategoryPage.as_view(), name='category'),
    url(r'categories/(?P<category_slug>[\w-]+)/load-more/'
        r'(?P<offset>[0-9]+)/(?P<sorting>[0-9]*)/$',
        views.load_more, name='load_more'),
    url(r'^no-images/$', views.ProductsWithoutImages.as_view(),
        name='products_without_images'),
    url(r'^no-text/$', views.ProductsWithoutText.as_view(),
        name='products_without_text'),
    url(r'^products/(?P<product_id>[0-9]+)/$',
        views.ProductPage.as_view(), name='product'),
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
]

ecommerce_urls = [
    url(r'^cart-add/$', views.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', views.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', views.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', views.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order-call/$', views.order_call),
    url(r'^one-click-buy/$', views.one_click_buy),
    url(r'^yandex-order/$', views.YandexOrder.as_view()),
    url(r'', include('ecommerce.urls')),
]

url_name = Page.CUSTOM_PAGES_URL_NAME
custom_pages = [
    url(r'^(?P<page>)$', views.IndexPage.as_view(), name=url_name),
    url(r'^(?P<page>search)/$', views.Search.as_view(), name=url_name),
    url(r'^(?P<page>catalog)/$', views.CategoryTree.as_view(), name=url_name),
    url(r'^shop/(?P<page>order)/$', views.OrderPage.as_view(), name=url_name),
    url(r'^shop/(?P<page>order-success)/$', views.OrderSuccess.as_view(), name=url_name),
    url(r'^(?P<page>sitemap)/$', SitemapPage.as_view(), name=url_name),
]

urlpatterns = [
    url('', include(custom_pages)),
    url(r'^admin/', include(admin_urls)),
    url(r'^catalog/', include(catalog_urls)),
    url(r'^pages/', include('pages.urls')),
    url(r'^robots\.txt$', robots),
    url(r'^save-feedback/$', views.save_feedback),
    url(r'^delete-feedback/$', views.delete_feedback),
    url(r'^set-view-type/$', views.set_view_type, name='set_view_type'),
    url(r'^shop/', include(ecommerce_urls)),
    url(r'^search/', include(search_urls)),
    url(r'^service/', include(service_urls)),
    url(r'^sitemap\.xml$', cached_view(sitemap), {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
