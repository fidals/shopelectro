"""Django admin module."""

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from collections import namedtuple

from shopelectro.models import Category, Product

# Override templates
admin.sites.AdminSite.site_header = 'Shopelectro administration'


def after_action_message(updated_rows):
    if updated_rows == 1:
        return '1 item was'
    else:
        return '{} items were'.format(updated_rows)


class PriceRange(admin.SimpleListFilter):
    # Human-readable filter title
    title = _('price')

    # Parameter for the filter that will be used in the URL query
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        price_segment = namedtuple('price_segment', ['name', 'size'])
        price_segment_list = [
            price_segment(
                '{}'.format(i - 1),
                _('{} 000 - {} 000 руб.'.format(i - 1, i))
            )
            for i in range(2, 11)
        ]

        price_segment_list.insert(0, price_segment('0', _('0 руб.')))
        price_segment_list.append(price_segment('10', _('10 000+ руб.')))

        return price_segment_list

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string.
        """
        if not self.value():
            return

        if self.value() == '0':
            return queryset.filter(price__exact=0)

        if self.value() == '10':
            return queryset.filter(price__gt=10000)

        price_ranges = {i: (i * 1000, (i + 1) * 1000)
                        for i in range(0, 10)}
        range_for_query = price_ranges[int(self.value())]
        return queryset.filter(price__in=range(*range_for_query))


class AbstractChangeListAdmin(admin.ModelAdmin):
    # Settings
    save_on_top = True
    list_filter = ['is_active']
    list_per_page = 50

    # Actions
    actions = ['make_items_active', 'make_items_non_active']

    def make_items_active(self, request, queryset):
        updated_rows = queryset.update(is_active=1)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request,
                          '{} marked as active.'.format(message_prefix))

    make_items_active.short_description = 'Mark items active'

    def make_items_non_active(self, request, queryset):
        updated_rows = queryset.update(is_active=0)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request,
                          '{} marked as non-active.'.format(message_prefix))

    make_items_non_active.short_description = 'Mark items NOT active'


class CategoryShopelectroAdmin(AbstractChangeListAdmin):
    # Settings
    search_fields = ['name']
    list_display = ['name', 'custom_parent', 'is_active']

    # Custom fields
    def custom_parent(self, model):
        if model.parent is None:
            return

        parent = model.parent
        url = reverse('admin:shopelectro_category_change', args=(parent.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=parent,
            url=url
        )

    custom_parent.short_description = 'Parent'
    custom_parent.admin_order_field = 'parent'


class ProductsShopelectroAdmin(AbstractChangeListAdmin):
    """
    Custom Fieldsets for model
    https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """
    fieldsets = (
        ('Основные характеристики', {
            'classes': ('primary-chars',),
            'fields': (
                'name',
                'category',
                ('price', 'wholesale_small'),
                ('in_stock', 'is_popular')
            )
        }),
        ('Дополнительные характеристики', {
            'classes': ('secondary-chars',),
            'fields': (
                # TODO - will be fixed at dev-774
                # 'content',
            ),
        }),
        ('SEO', {
            'classes': ('seo-chars',),
            'fields': (
                # TODO - will be fixed at dev-774
                # 'title',
                # '_menu_title',
                # 'h1',
                # 'keywords',
                # 'description'
            ),
        }),
    )

    # Settings
    search_fields = ['name', 'category__name']
    list_display = ['name', 'custom_category', 'price', 'links', 'is_active']
    list_filter = [PriceRange, 'is_active']

    # Custom fields
    def links(self, model):
        context = {
            'site_url': model.get_absolute_url(),
        }

        return render_to_string('admin/includes/items_list_row.html', context)

    links.short_description = 'Links'
    links.admin_order_field = 'name'

    def custom_category(self, model):
        if not model.category:
            return

        category = model.category
        url = reverse('admin:shopelectro_category_change', args=(category.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=category,
            url=url
        )

    custom_category.short_description = 'Category'
    custom_category.admin_order_field = 'category'


class TableEditorAdmin(AdminSite):
    """
    Render custom view for Table editor
    https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_urls
    """
    def get_urls(self):
        original_urls = super(TableEditorAdmin, self).get_urls()

        custom_urls = [
            url(r'^editor/$', self.admin_view(self.table_editor_view))
        ]

        return custom_urls + original_urls

    def table_editor_view(self, request):
        context = {
            # Include common variables for rendering the admin template.
            **self.each_context(request),
            # Anything else you want in the context...
            'title': 'Table editor'
        }

        return TemplateResponse(request, 'admin/table_editor.html', context)

table_editor_view = TableEditorAdmin()
admin.site.register(Category, CategoryShopelectroAdmin)
admin.site.register(Product, ProductsShopelectroAdmin)
