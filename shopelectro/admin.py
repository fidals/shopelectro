from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.redirects.models import Redirect
from django.db import models as django_models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from pages.models import CustomPage, FlatPage, PageTemplate
from generic_admin import inlines, models, sites

from shopelectro import models as se_models
from shopelectro.views.admin import TableEditor


class SEAdminSite(sites.SiteWithTableEditor):

    site_header = 'Shopelectro administration'
    table_editor_view = TableEditor


def prepare_has_filter_queryset(value, db_table, queryset):
    if not value:
        return

    query = '{}__tags__isnull'.format(db_table)

    # Use brackets, because `Explicit is better than implicit`.
    return queryset.filter(**{query: value != 'yes'})


class HasTagsFilter(admin.SimpleListFilter):

    product_model = se_models.Product
    title = _('has tags')
    parameter_name = 'has_tags'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has tags')),
            ('no', _('Has no tags')),
        )

    def queryset(self, request, queryset):
        return prepare_has_filter_queryset(
            self.value(),
            self.product_model._meta.db_table,
            queryset
        )


class HasCategoryFilter(admin.SimpleListFilter):

    product_model = se_models.Product
    title = _('has category')
    parameter_name = 'has_category'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has category')),
            ('no', _('Has no category')),
        )

    def queryset(self, request, queryset):
        return prepare_has_filter_queryset(
            self.value(),
            self.product_model._meta.db_table,
            queryset
        )


class TagInline(admin.StackedInline):

    model = se_models.Tag
    extra = 0


class CategoryInline(inlines.CategoryInline):

    model = se_models.Category

    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('parent', 'correct_parent_id'),
        )
    }),)


class ProductInline(inlines.ProductInline):

    model = se_models.Product

    formfield_overrides = {
        django_models.ManyToManyField: {
            'widget': FilteredSelectMultiple(verbose_name='Tags', is_stacked=False)
        },
    }

    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'in_stock'),
            'is_popular',
            ('purchase_price', 'wholesale_small'),
            ('wholesale_medium', 'wholesale_large'),
            'tags',
        )
    }),)


class CategoryPageAdmin(models.CategoryPageAdmin):

    add = False
    delete = False
    inlines = [CategoryInline, inlines.ImageInline]

    def get_queryset(self, request):
        return (
            super(CategoryPageAdmin, self)
            .get_queryset(request)
            .select_related('shopelectro_category')
        )


class ProductPageAdmin(models.ProductPageAdmin):

    add = False
    delete = False
    category_page_model = se_models.CategoryPage
    list_filter = [*models.ProductPageAdmin.list_filter, HasTagsFilter, HasCategoryFilter]
    inlines = [ProductInline, inlines.ImageInline]
    search_fields = [
        'shopelectro_product__vendor_code', 'name', 'slug',
    ]

    def model_id(self, obj):
        return obj.model.vendor_code

    model_id.short_description = _('Vendor code')
    model_id.admin_order_field = 'shopelectro_product__vendor_code'

    def get_queryset(self, request):
        return (
            super(ProductPageAdmin, self)
            .get_queryset(request)
            .select_related('shopelectro_product')
        )


class ProductFeedbackPageAdmin(admin.ModelAdmin):

    add = False
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

    def get_queryset(self, request):
        return (
            super(ProductFeedbackPageAdmin, self)
            .get_queryset(request)
            .select_related('product')
        )


class TagGroupAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'position', 'count_tags']
    list_display_links = ['name']

    inlines = [TagInline]

    def get_queryset(self, request):
        return super(TagGroupAdmin, self).get_queryset(request).prefetch_related('tags')

    def count_tags(self, obj):
        return obj.tags.count()


class TagAdmin(admin.ModelAdmin):

    search_fields = ['id', 'name']
    list_display = ['id', 'name', 'position', 'custom_group']
    list_display_links = ['name']

    def get_queryset(self, request):
        return super(TagAdmin, self).get_queryset(request).prefetch_related('group')

    def custom_group(self, obj):
        group = obj.group

        return format_html(
            '<a href="{url}">{group}</a>',
            group=group,
            url=reverse('admin:shopelectro_taggroup_change', args=(group.id, ))
        )

    custom_group.admin_order_field = 'group'
    custom_group.short_description = _('Group')


se_admin = SEAdminSite(name='se_admin')
se_admin.register(CustomPage, models.CustomPageAdmin)
se_admin.register(FlatPage, models.FlatPageAdmin)
se_admin.register(PageTemplate, models.CustomPageTemplateAdmin)

se_admin.register(se_models.CategoryPage, CategoryPageAdmin)
se_admin.register(se_models.ProductPage, ProductPageAdmin)
se_admin.register(se_models.ProductFeedback, ProductFeedbackPageAdmin)
se_admin.register(se_models.TagGroup, TagGroupAdmin)
se_admin.register(se_models.Tag, TagAdmin)

se_admin.register(Redirect)
