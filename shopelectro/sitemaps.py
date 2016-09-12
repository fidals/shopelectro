from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.conf import settings

from pages.models import Page
from shopelectro.models import Product, Category


class AbstractSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.9


class IndexSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'
    priority = 1

    # items()
    # Required. A method that returns a list of objects.
    # https://docs.djangoproject.com/ja/1.9/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.items
    def items(self):
        return ['index']

    # location()
    # Optional. If location isn’t provided, the framework will call the get_absolute_url()
    # method on each object as returned by items().
    # https://docs.djangoproject.com/ja/1.9/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.location
    def location(self, model):
        return reverse(model)


class CategorySitemap(AbstractSitemap):

    def items(self):
        return Category.objects.filter(page__is_active=True)


class ProductSitemap(AbstractSitemap):

    def items(self):
        return Product.objects.filter(page__is_active=True)


class PagesSitemap(AbstractSitemap):

    def items(self):
        return Page.objects.filter(is_active=True, type='page')
