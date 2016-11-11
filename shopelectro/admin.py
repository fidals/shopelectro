from django.contrib.redirects.models import Redirect

from pages.models import CustomPage, FlatPage
from generic_admin import models, inlines, sites

from shopelectro.models import CategoryPage, ProductPage, Product, Category


class SEAdminSite(sites.TableEditor):
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


se_admin_site = SEAdminSite(name='se_admin')

se_admin_site.register(CustomPage, models.CustomPageAdmin)
se_admin_site.register(FlatPage, models.FlatPageAdmin)
se_admin_site.register(ProductPage, ProductPageAdmin)
se_admin_site.register(CategoryPage, CategoryPageAdmin)
se_admin_site.register(Redirect)
