from django.conf import settings
from django.shortcuts import get_object_or_404

from catalog import context, typing
from images.models import Image
from pages import models as pages_models, context as pages_context
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


class Catalog(context.Context):

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

    def context(self) -> typing.ContextDict:
        all_tags = context.Tags(models.Tag.objects.all())

        selected_tags = context.tags.ParsedTags(
            tags=all_tags,
            raw_tags=self.request_data.tags,
        )
        if self.request_data.tags:
            selected_tags = context.tags.Checked404Tags(selected_tags)

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
        # @todo #683:30m Remove *Tags and *Products suffixes from catalog.context classes.
        #  Rename Checked404Tags to ExistingOr404.
        paginated = context.products.PaginatedProducts(
            products=products,
            url=self.request_data.request.path,
            page_number=self.request_data.pagination_page_number,
            per_page=self.request_data.pagination_per_page,
        )

        images = context.products.ProductImages(paginated.products, Image.objects.all())
        brands = context.products.ProductBrands(paginated.products, all_tags)
        grouped_tags = context.tags.GroupedTags(
            tags=context.tags.TagsByProducts(all_tags, products)
        )
        page = context.pages.Page(self.page, selected_tags)
        category = context.category.Context(self.category)
        params = {
            'view_type': self.request_data.get_view_type(),
            'sorting_options': settings.CATEGORY_SORTING_OPTIONS.values(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
            'sort': self.request_data.sorting_index,
        }

        return {
            **params,
            **pages_context.Contexts([
                page, category, paginated,
                images, brands, grouped_tags
            ]).context()
        }
