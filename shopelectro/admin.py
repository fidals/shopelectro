import os
from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.db import models
from django.forms import TextInput
from shopelectro import models as shopelectro_models
from catalog.models import Category

# Override templates
admin.sites.AdminSite.site_header = 'Shopelectro administration'
admin.ModelAdmin.change_list_template = os.path.join(settings.BASE_DIR,
                                                     'templates/shopelectro/admin/change_list.html')


def after_action_message(updated_rows):
    if updated_rows == 1:
        return '1 item was'
    else:
        return '%s items were' % updated_rows


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
        return (
            ('0', _('0 руб.')),
            ('1', _('1 - 1 000 руб.')),
            ('2', _('1 000 - 2 000 руб.')),
            ('3', _('2 000 - 3 000 руб.')),
            ('4', _('3 000 - 4 000 руб.')),
            ('5', _('4 000 - 5 000 руб.')),
            ('6', _('5 000 - 6 000 руб.')),
            ('7', _('6 000 - 7 000 руб.')),
            ('8', _('7 000 - 8 000 руб.')),
            ('9', _('8 000 - 9 000 руб.')),
            ('10', _('9 000 - 10 000 руб.')),
            ('11', _('10 000+ руб.')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string.
        """
        if self.value() == '0':
            return queryset.filter(price__exact=0)
        if self.value() == '1':
            return queryset.filter(price__in=range(1, 1000))
        if self.value() == '2':
            return queryset.filter(price__in=range(1000, 2000))
        if self.value() == '3':
            return queryset.filter(price__in=range(2000, 3000))
        if self.value() == '4':
            return queryset.filter(price__in=range(3000, 4000))
        if self.value() == '5':
            return queryset.filter(price__in=range(4000, 5000))
        if self.value() == '6':
            return queryset.filter(price__in=range(5000, 6000))
        if self.value() == '7':
            return queryset.filter(price__in=range(6000, 7000))
        if self.value() == '8':
            return queryset.filter(price__in=range(7000, 8000))
        if self.value() == '9':
            return queryset.filter(price__in=range(8000, 9000))
        if self.value() == '10':
            return queryset.filter(price__in=range(9000, 10000))
        if self.value() == '11':
            return queryset.filter(price__gt=10000)


class AbstractChangeListAdmin(admin.ModelAdmin):
    # Settings
    save_on_top = True
    list_filter = ('is_active',)
    list_per_page = 50

    # Actions
    actions = ['make_items_active', 'make_items_non_active']

    def make_items_active(self, request, queryset):
        updated_rows = queryset.update(is_active=1)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request, '%s marked as active.' % message_prefix)

    make_items_active.short_description = 'Mark items active'

    def make_items_non_active(self, request, queryset):
        updated_rows = queryset.update(is_active=0)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request, '%s marked as non-active.' % message_prefix)

    make_items_non_active.short_description = 'Mark items NOT active'


class CategoryShopelectroAdmin(AbstractChangeListAdmin):
    # Settings
    search_fields = ['name']
    list_display = ('name', 'custom_parent', 'is_active')
    list_display_links = ('name',)

    # Custom fields
    def custom_parent(self, model):
        parent = model.parent

        if parent is not None:
            url = '/admin/catalog/category/' + str(parent.id) + '/change'

            return format_html(
                u'<a href="{url}">{parent}</a>',
                parent=parent,
                url=url
            )

    custom_parent.short_description = 'Parent'
    custom_parent.admin_order_field = 'parent'

    @staticmethod
    # View on site button
    def view_on_site(model):
        return reverse('category', args=[str(model.slug)])


class ProductsShopelectroAdmin(AbstractChangeListAdmin):
    # Settings
    search_fields = ['name', 'category__name']
    list_display = ('name', 'links', 'category', 'price', 'is_active')
    list_editable = ('name', 'category', 'price',)
    list_filter = (PriceRange, 'is_active')
    list_display_links = None

    # Input fields attributes
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'field-editable'})},
    }

    # Custom fields
    def links(self, model):
        context = {
            'site_url': model.get_absolute_url(),
            'admin_url': '/admin/shopelectro/product/' + str(model.id) + '/change',
        }

        return render_to_string('shopelectro/admin/admin_items_list_row.html', context)

    links.short_description = 'Links'
    links.admin_order_field = 'name'

    @staticmethod
    # View on site button
    def view_on_site(model):
        return reverse('product', args=[str(model.id)])

admin.site.register(Category, CategoryShopelectroAdmin)
admin.site.register(shopelectro_models.Product, ProductsShopelectroAdmin)
