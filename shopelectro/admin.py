from django.contrib.redirects.models import Redirect

from shopelectro.models import CategoryPage, ProductPage, Product, Category
from pages.models import CustomPage, FlatPage
from generic_admin.admin import models, inlines, sites


class ShopelectroAdminSite(sites.TableEditor):
    site_header = 'Shopelectro administration'


class CategoryInline(inlines.CategoryInline):
    model = Category


class ProductInline(inlines.ProductInline):
    model = Product
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'in_stock', 'is_popular'),
            ('purchase_price', 'wholesale_small', 'wholesale_medium', 'wholesale_large')
        )
    }),)


class ProductPageAdmin(models.ProductPageAdmin):
    add = False
    delete = False

    category_page_model = CategoryPage
    inlines = [ProductInline, inlines.ImageInline]


class CategoryPageAdmin(models.CategoryPageAdmin):
    add = False
    delete = False

    inlines = [CategoryInline, inlines.ImageInline]


custom_admin_site = ShopelectroAdminSite(name='custom_admin')

custom_admin_site.register(CustomPage, models.CustomPageAdmin)
custom_admin_site.register(FlatPage, models.FlatPageAdmin)
custom_admin_site.register(ProductPage, ProductPageAdmin)
custom_admin_site.register(CategoryPage, CategoryPageAdmin)
custom_admin_site.register(Redirect)
