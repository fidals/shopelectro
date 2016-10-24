from collections import namedtuple

from django.contrib import admin
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from shopelectro.models import Category, Product, CategoryPage, ProductPage
from pages.models import CustomPage, FlatPage


class CustomAdminSite(admin.AdminSite):
    site_header = 'Shopelectro administration'

    # Fields for TableEditor filters:
    FILTER_FIELDS = (
        {
            'id': 'filter-name',
            'name': 'Название',
            'checked': True,
        },
        {
            'id': 'filter-title',
            'name': 'Заголовок',
            'checked': False,
        },
        {
            'id': 'filter-category_name',
            'name': 'Категория',
            'checked': True,
        },
        {
            'id': 'filter-price',
            'name': 'Цена',
            'checked': True,
        },
        {
            'id': 'filter-purchase_price',
            'name': 'Закупочная цена',
            'checked': False,
        },
        {
            'id': 'filter-is_active',
            'name': 'Активность',
            'checked': True,
        },
        {
            'id': 'filter-is_popular',
            'name': 'Топ',
            'checked': True,
        },
        {
            'id': 'filter-in_stock',
            'name': 'Наличие',
            'checked': False,
        },
    )

    def get_urls(self):
        original_urls = super(CustomAdminSite, self).get_urls()

        custom_urls = [
            url(r'^editor/$', self.admin_view(self.table_editor_view), name='editor')
        ]
        return custom_urls + original_urls

    def table_editor_view(self, request):
        context = {
            # Include common variables for rendering the admin template.
            **self.each_context(request),
            # Anything else you want in the context...
            'title': 'Table editor',
            'filter_fields': self.FILTER_FIELDS,
        }

        return TemplateResponse(request, 'admin/table_editor.html', context)


custom_admin_site = CustomAdminSite(name='custom_admin')


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
        Return a list of tuples. The first element in each
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
            ) for i in range(2, 11)
        ]

        price_segment_list.insert(0, price_segment('0', _('0 руб.')))
        price_segment_list.append(price_segment('10', _('10 000+ руб.')))

        return price_segment_list

    def queryset(self, request, queryset):
        """
        Return the filtered queryset based on the value provided in the query string.
        """
        if not self.value():
            return

        if self.value() == '0':
            return queryset.filter(shopelectro_product__price__exact=0)

        if self.value() == '10':
            return queryset.filter(shopelectro_product__price__gt=10000)

        price_ranges = {i: (i * 1000, (i + 1) * 1000)
                        for i in range(0, 10)}
        range_for_query = price_ranges[int(self.value())]
        return queryset.filter(shopelectro_product__price__in=range(*range_for_query))


# Inline classes
class ProductInline(admin.StackedInline):
    model = Product
    can_delete = False
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            ('name', 'id'),
            ('category', 'correct_category_id'),
            ('price', 'in_stock', 'is_popular'),
            ( 'purchase_price', 'wholesale_small', 'wholesale_medium', 'wholesale_large'),
        )
    }),)

    def correct_category_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.category_id
    correct_category_id.short_description = 'Category ID'

    readonly_fields = ['id', 'correct_category_id']


class CategoryInline(admin.StackedInline):
    model = Category
    can_delete = False
    fieldsets = ((None, {
        'classes': ('primary-chars', ),
        'fields': (
            # 'slug',TODO in dev-775
            ('name', 'id'),
            ('parent', 'correct_parent_id'),
        )
    }),)

    def correct_parent_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.parent_id
    correct_parent_id.short_description = 'Parent ID'

    readonly_fields = ['id', 'correct_parent_id']


# Model admin classes
class PageAdmin(admin.ModelAdmin):
    save_on_top = True #  https://goo.gl/al9CEc

    list_filter = ['is_active']
    list_display = ['id', 'h1', 'custom_parent', 'is_active']
    list_display_links = ['h1']

    search_fields = ['id', 'h1', 'parent__h1']

    readonly_fields = ['id']

    actions = ['make_items_active', 'make_items_non_active']

    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars',),
            'fields': (
                ('id', 'is_active'),
                'date_published',
                # 'slug', TODO in dev-775
                '_menu_title',
                'seo_text',
                'position',
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                ('h1', '_title'),
                'keywords',
                'description',
                'content'
            )
        })
    )

    def make_items_active(self, request, queryset):
        updated_rows = queryset.update(is_active=1)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request,
                          '{} marked as active.'.format(message_prefix))

    make_items_active.short_description = 'Make active'

    def make_items_non_active(self, request, queryset):
        updated_rows = queryset.update(is_active=0)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request,
                          '{} marked as non-active.'.format(message_prefix))

    make_items_non_active.short_description = 'Make inactive'


class CustomPageAdmin(PageAdmin):
    # Fieldsets
    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars',),
            'fields': (
                'is_active',
                'date_published',
                '_menu_title',
                'seo_text',
                'position',
                ('parent', 'correct_parent_id')
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                ('h1', '_title'),
                ('keywords', 'id'),
                'description',
                'content'
            )
        })
    )

    def correct_parent_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.parent_id
    correct_parent_id.short_description = 'Parent ID'

    readonly_fields = ['id', 'correct_parent_id']

    def custom_parent(self, obj):
        if not obj.parent:
            return

        parent = obj.parent
        url = reverse('custom_admin:pages_custompage_change', args=(parent.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=parent,
            url=url
        )

    custom_parent.short_description = 'Parent'
    custom_parent.admin_order_field = 'parent__h1'

    def has_add_permission(self, request):
        """
        Site always should contain defined set of custom pages.
        For example SE should contain only one `/order/` page.
        This pages are created with migrate command.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Site always should contain defined set of custom pages.
        For example SE should contain only one `/order/` page.
        This pages are created with migrate command.
        """
        return False


class FlatPageAdmin(PageAdmin):
    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars',),
            'fields': (
                ('id', 'is_active'),
                'date_published',
                # 'slug', TODO in dev-775
                '_menu_title',
                'seo_text',
                'position',
                ('parent', 'correct_parent_id')
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                ('h1', '_title'),
                'keywords',
                'description',
                'content'
            )
        })
    )

    def correct_parent_id(self, obj):
        """Needed for correct short_description attr"""
        return obj.parent_id
    correct_parent_id.short_description = 'Parent ID'

    readonly_fields = ['id', 'correct_parent_id']

    def custom_parent(self, obj):
        if not obj.parent:
            return

        parent = obj.parent
        url = reverse('custom_admin:pages_flatpage_change', args=(parent.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=parent,
            url=url
        )

    custom_parent.short_description = 'Parent'
    custom_parent.admin_order_field = 'parent__h1'


class ProductPageAdmin(PageAdmin):
    inlines = [
        ProductInline,
    ]

    list_filter = ['is_active', PriceRange]

    list_display = ['product_id', 'h1', 'custom_parent', 'price', 'links', 'is_active']

    search_fields = ['shopelectro_product__id', 'h1', 'parent__h1']

    def product_id(self, obj):
        return obj.model.id

    product_id.short_description = 'Id'
    product_id.admin_order_field = 'shopelectro_product__id'

    def price(self, obj):
        return obj.model.price

    price.short_description = 'Price'
    price.admin_order_field = 'shopelectro_product__price'

    def custom_parent(self, obj):
        if not obj.parent:
            return

        parent = obj.parent
        url = reverse('custom_admin:shopelectro_categorypage_change', args=(parent.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=parent,
            url=url
        )

    custom_parent.short_description = 'Category'
    custom_parent.admin_order_field = 'parent__h1'

    def links(self, model):
        context = {
            'site_url': model.url,
        }

        return render_to_string('admin/includes/items_list_row.html', context)

    links.short_description = 'Link'

    def has_add_permission(self, request):
        return False

class CategoryPageAdmin(PageAdmin):

    inlines = [
        CategoryInline,
    ]

    search_fields = ['shopelectro_category__id', 'h1', 'parent__h1']

    list_display = ['category_model_id', 'h1', 'custom_parent', 'is_active']

    # Custom fields
    def category_model_id(self, obj):
        return obj.model.id

    category_model_id.short_description = 'Id'
    category_model_id.admin_order_field = 'shopelectro_category__id'

    def custom_parent(self, obj):
        if not obj.parent_id:
            return
        try:
            url = reverse('custom_admin:shopelectro_categorypage_change', args=(obj.parent_id,))
        except:
            url = reverse('custom_admin:pages_custompage_change', args=(obj.parent_id,))

        return format_html(
            '<a href="{url}">{parent_id}</a>',
            parent_id=obj.parent,
            url=url
        )

    custom_parent.short_description = 'Parent'
    custom_parent.admin_order_field = 'parent__h1'

    def has_add_permission(self, request):
        return False

custom_admin_site.register(CustomPage, CustomPageAdmin)
custom_admin_site.register(ProductPage, ProductPageAdmin)
custom_admin_site.register(CategoryPage, CategoryPageAdmin)
custom_admin_site.register(FlatPage, FlatPageAdmin)
