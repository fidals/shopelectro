from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic import TemplateView

from pages.urls import custom_page_url
from pages.views import RobotsView, SitemapPage
from shopelectro import sitemaps, views
from shopelectro.admin import se_admin


def cached_time(*args, **kwargs) -> int:
    """Return value of time for caching in seconds."""
    return int(timedelta(*args, **kwargs).total_seconds())


# Orders sitemaps instances
sitemaps = OrderedDict([
    ('index', sitemaps.IndexSitemap),
    ('category', sitemaps.CategorySitemap),
    ('category-with-tags', sitemaps.CategoryWithTagsSitemap),
    ('products', sitemaps.ProductSitemap),
    ('site', sitemaps.PagesSitemap)
])

# disable cache
if settings.DEBUG:
    def cache_page(arg):  # Ignore PyFlakesBear
        if callable(arg):
            return arg
        return cache_page

cached_60d = cache_page(cached_time(days=60))
cached_2h = cache_page(cached_time(hours=2))

admin_urls = [
    url(r'^', se_admin.urls),
    url(r'^autocomplete/$', views.AdminAutocomplete.as_view(), name='admin_autocomplete'),
    url(r'^get-tree-items/$', views.Tree.as_view()),
    url(r'^redirect-to-product/$', views.RedirectToProduct.as_view()),
    url(r'^table-editor-api/$', views.TableEditorAPI.as_view()),
    url(r'^select2/', include('django_select2.urls')),
]

catalog_urls = [
    # "category" group
    url(r'^categories/(?P<slug>[\w-]+)/$',
        cached_2h(views.CategoryPage.as_view()), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/tags/(?P<tags>[\w_-]+)/$',
        cached_2h(views.CategoryPage.as_view()), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/(?P<sorting>[0-9]*)/$',
        views.CategoryPage.as_view(), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/(?P<sorting>[0-9]*)/tags/(?P<tags>[\w_-]+)/$',
        views.CategoryPage.as_view(), name='category'),
    # "load more" group
    url(r'categories/(?P<slug>[\w-]+)/load-more/'
        r'(?P<offset>[0-9]+)/(?P<sorting>[0-9]*)/$',
        views.load_more, name='load_more'),
    url(r'categories/(?P<slug>[\w-]+)/load-more/'
        r'(?P<offset>[0-9]+)/(?P<sorting>[0-9]*)/tags/(?P<tags>[\w_-]+)/$',
        views.load_more, name='load_more'),
    # rest of urls
    url(r'^no-images/$', views.ProductsWithoutImages.as_view(),
        name='products_without_images'),
    url(r'^no-text/$', views.ProductsWithoutText.as_view(),
        name='products_without_text'),
    url(r'^products/(?P<product_vendor_code>[0-9]+)/$',
        views.ProductPage.as_view(), name='product'),
]

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
    url(r'^cart-get/$', never_cache(views.Cart.as_view()), name='cart_get'),
    url(r'^cart-add/$', views.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', views.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', views.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', views.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order-call/$', views.order_call),
    url(r'^one-click-buy/$', views.one_click_buy),
    url(r'^yandex-order/$', views.YandexOrder.as_view()),
    url(r'', include('ecommerce.urls')),
]

custom_pages = [
    # can't use just `r'^(?P<page>)$'` with no args to views, because reverse don't work
    custom_page_url(r'^$', cached_2h(views.IndexPage.as_view()), {'page': ''}, name='index'),
    custom_page_url(r'^(?P<page>robots\.txt)$', RobotsView.as_view()),
    custom_page_url(r'^(?P<page>search)/$', views.Search.as_view()),
    custom_page_url(r'^(?P<page>catalog)/$', cached_2h(views.category_matrix)),
    custom_page_url(r'^(?P<page>sitemap)/$', SitemapPage.as_view()),
    # these pages should show only actual state
    custom_page_url(r'^shop/(?P<page>order)/$', never_cache(views.OrderPage.as_view())),
    custom_page_url(r'^shop/(?P<page>order-success)/$', never_cache(views.OrderSuccess.as_view())),
]

urlpatterns = [
    url('', include(custom_pages)),
    url(r'^admin/', include(admin_urls)),
    url(r'^catalog/', include(catalog_urls)),
    url(r'^pages/', include('pages.urls')),
    url(r'^save-feedback/$', views.save_feedback),
    url(r'^delete-feedback/$', views.delete_feedback),
    url(r'^set-view-type/$', views.set_view_type, name='set_view_type'),
    url(r'^shop/', include(ecommerce_urls)),
    url(r'^search/', include(search_urls)),
    url(r'^service/', include(service_urls)),
    url(r'^sms/$', TemplateView.as_view(template_name='sms_landing.html'), name='sms_lending'),
    url(r'^sitemap\.xml$', cached_60d(sitemap), {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]

# Test and Debug environments replace real 404 and 500 error with stack traces.
# We expose real 404 and 500 pages with separated urls to test them.
if settings.TEST_ENV or settings.DEBUG:
    urlpatterns += [
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
    ]
