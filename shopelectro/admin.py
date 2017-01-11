from django.contrib import admin
from django.contrib.redirects.models import Redirect
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from pages.models import CustomPage, FlatPage
from generic_admin import inlines, models, sites

from shopelectro import models as se_models
from shopelectro.views.admin import TableEditor


class SEAdminSite(sites.SiteWithTableEditor):
    site_header = 'Shopelectro administration'
    table_editor_view = TableEditor


class CategoryInline(inlines.CategoryInline):
    model = se_models.Category


class ProductInline(inlines.ProductInline):
    model = se_models.Product
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'in_stock', 'is_popular'),
            ('purchase_price', 'wholesale_small', 'wholesale_medium', 'wholesale_large')
        )
    }),)


class CategoryPageAdmin(models.CategoryPageAdmin):
    add = False
    delete = False
    inlines = [CategoryInline, inlines.ImageInline]


class ProductPageAdmin(models.ProductPageAdmin):
    add = False
    delete = False
    category_page_model = se_models.CategoryPage
    inlines = [ProductInline, inlines.ImageInline]


class ProductFeedbackPageAdmin(admin.ModelAdmin):
    delete = False
    list_filter = ['rating']
    list_display = ['rating', 'name', 'dignities', 'limitations', 'general', 'links']

    def links(self, obj):
        return format_html(
            '''
            <a href="{url}" class="field-link" title="Посмотреть на сайте" target="_blank">
              <i class="fa fa-link" aria-hidden="true"></i>
            </a>
            '''.format(url=obj.product.url))

    links.short_description = _('Link')

se_admin = SEAdminSite(name='se_admin')
se_admin.register(CustomPage, models.CustomPageAdmin)
se_admin.register(FlatPage, models.FlatPageAdmin)
se_admin.register(se_models.CategoryPage, CategoryPageAdmin)
se_admin.register(se_models.ProductPage, ProductPageAdmin)
se_admin.register(se_models.ProductFeedback, ProductFeedbackPageAdmin)
se_admin.register(Redirect)
