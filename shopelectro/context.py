from functools import partial

from django.conf import settings
from django.shortcuts import get_object_or_404

from catalog import newcontext
from images.models import Image
from pages import models as pages_models
from shopelectro import models, request_data


# @todo #255:60m  Improve `SortingOption` interface.
#  Now it's located in context and this is wrong.
#  Maybe refactor `CATEGORY_SORTING_OPTIONS`.
class SortingOption:
    def __init__(self, index=0):
        options = settings.CATEGORY_SORTING_OPTIONS[index]
        self.label = options['label']
        self.field = options['field']
        self.direction = options['direction']

    @property
    def directed_field(self):
        return self.direction + self.field


class Page(newcontext.Context):

    def __init__(self, page, tags: newcontext.Tags):
        self._page = page
        self._tags = tags

    def context(self):
        def template_context(page, tag_titles, tags):
            return {
                'page': page,
                'tag_titles': tag_titles,
                'tags': tags,
            }

        tags_qs = self._tags.qs()
        self._page.get_template_render_context = partial(
            template_context, self._page, tags_qs.as_title(), tags_qs
        )

        return {
            'page': self._page,
        }


class Catalog(newcontext.Context):

    def __init__(self, request_data_: request_data.Catalog):
        self.request_data = request_data_

    @property
    def page(self):
        return get_object_or_404(
            pages_models.ModelPage,
            slug=self.request_data.slug
        )

    @property
    def category(self):
        return self.page.model

    def context(self) -> dict:
        all_tags = newcontext.Tags(models.Tag.objects.all())

        selected_tags = newcontext.tags.ParsedTags(
            tags=all_tags,
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = newcontext.tags.Checked404Tags(selected_tags)

        products = (
            models.Product.objects.active()
            .filter_descendants(self.category)
            .tagged_or_all(selected_tags.qs())
            .order_by(SortingOption(index=self.request_data.sorting_index).directed_field)
        )

        """
        We have to use separated variable for pagination.

        Because paginated QuerySet can not used as QuerySet.
        It's not the most strong place of Django ORM, of course.
        :return: ProductsContext with paginated QuerySet inside
        """
        # @todo #683:30m Remove *Tags and *Products suffixes from catalog.newcontext classes.
        #  Rename Checked404Tags to ExistingOr404.
        paginated = newcontext.products.PaginatedProducts(
            products=products,
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

        images = newcontext.products.ProductImages(paginated.products, Image.objects.all())
        brands = newcontext.products.ProductBrands(paginated.products, all_tags)
        grouped_tags = newcontext.tags.GroupedTags(
            tags=newcontext.tags.TagsByProducts(all_tags, products)
        )
        page = Page(self.page, selected_tags)
        category = newcontext.category.Context(self.category)
        params = {
            'view_type': self.request_data.get_view_type(),
            'sorting_options': settings.CATEGORY_SORTING_OPTIONS.values(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
            'sort': self.request_data.sorting_index,
        }

        return {
            **params,
            **newcontext.Contexts([
                page, category, paginated,
                images, brands, grouped_tags
            ]).context()
        }
