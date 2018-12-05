from typing import Generator, Tuple

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from pages.models import Page, PageManager

from shopelectro.models import Category, Product, Tag


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
        return ['']

    # location()
    # Optional. If location isn’t provided, the framework will call the get_absolute_url()
    # method on each object as returned by items().
    # https://docs.djangoproject.com/ja/1.9/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.location
    def location(self, model):
        return reverse(Page.CUSTOM_PAGES_URL_NAME, args=(model, ))


class CategorySitemap(AbstractSitemap):

    def items(self):
        return Category.objects.filter(page__is_active=True)


def get_categories_with_tags() -> Generator[
    Tuple[Category, Tag], None, None
]:
    """
    Return all unique Category+TagGroup pairs.

    Currently, tags per category is limited to 1 tag (by SEO requirements).
    So, for each tags group in each category we'll get 1 tag.
    """
    for category in Category.objects.filter(page__is_active=True):
        products = Product.objects.get_by_category(category)
        tags = Tag.objects.filter_by_products(products)
        for group_name, group_tags in tags.get_group_tags_pairs():
            for group_tag in group_tags:
                yield category, group_tag


class CategoryWithTagsSitemap(AbstractSitemap):

    def items(self):
        # `items` method can't return generator (by django design)
        # so we moved items collection code to dedicated function
        return list(get_categories_with_tags())

    def location(self, item):
        category, tag = item
        return reverse('category', kwargs={
            'slug': category.page.slug,
            'tags': tag.slug,
        })


class ProductSitemap(AbstractSitemap):

    def items(self):
        return Product.objects.filter(page__is_active=True)


class PagesSitemap(AbstractSitemap):

    def items(self):
        assert(isinstance(Page.objects, PageManager))
        return Page.objects.active()
