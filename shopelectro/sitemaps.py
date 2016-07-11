from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from pages.models import Post
from .models import Product, Category


class AbstractSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9


class IndexSitemap(Sitemap):
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
        return Category.objects.filter(is_active=True)


class ProductSitemap(AbstractSitemap):

    def items(self):
        return Product.objects.filter(is_active=True)


class BlogSitemap(AbstractSitemap):

    def items(self):
        return Post.objects.filter(is_active=True)
