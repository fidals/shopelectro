import typing

from catalog.context import AbstractProductsListContext
from catalog.models import ProductQuerySet
from images.models import Image

# @todo #683:60m Remove the ProductImages in favor of catalog.newcontext.ProductImages


class ProductImages(AbstractProductsListContext):

    @property
    def images(self) -> typing.Dict[int, Image]:
        assert isinstance(self.products, ProductQuerySet)

        images = {}
        if self.product_pages:
            images = Image.objects.get_main_images_by_pages(
                self.product_pages.filter(shopelectro_product__in=self.products)
            )

        return {
            product.id: images.get(product.page)
            for product in self.products
        }

    def get_context_data(self):
        return {
            'product_images': self.images,
            **(
                self.super.get_context_data()
                if self.super else {}
            ),
        }
