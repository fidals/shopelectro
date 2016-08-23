"""
Django admin module.
For injection your models in Page app, you should define INJECTION_MODELS
"""


from collections import namedtuple
from itertools import chain
from typing import Dict, Tuple

from django.contrib.admin import AdminSite
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.db.models import Model
from django.db.models.expressions import Q
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from shopelectro.models import Category, Product
from pages.models import Page


INJECTION_MODELS = (Category, Product) # Global variables


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
            return queryset.filter(shopelectro_product__price__exact=0)

        if self.value() == '10':
            return queryset.filter(shopelectro_product__price__gt=10000)

        price_ranges = {i: (i * 1000, (i + 1) * 1000)
                        for i in range(0, 10)}
        range_for_query = price_ranges[int(self.value())]
        return queryset.filter(shopelectro_product__price__in=range(*range_for_query))


class CustomAdminSite(AdminSite):
    """Override AdminSite method """
    site_header = 'Shopelectro administration'

    def extend_app_list_model(self, to_model: Model, add_models: INJECTION_MODELS, app_list):
        """
        Extend app list's models field.
        The App list looks like this [{..., models:[{...}, {...}]: app's models, ...}: app, {...}].
        """
        assert len(app_list), 'You should register model to admin site'

        def find_certain_app(app):
            for model in app['models']:
                if model['object_name'] == to_model._meta.object_name:
                    return True

        app = list(filter(find_certain_app, app_list))

        assert app, 'You should register model to admin site'

        app_model = app[0]['models'][0]
        custom_app_model = [{
                                'name': capfirst(model._meta.verbose_name_plural),
                                'object_name': model._meta.object_name,
                                'perms': app_model['perms'],
                                'admin_url': app_model['admin_url'] + model._meta.model_name,
                                'add_url': app_model['add_url'] + model._meta.model_name,
                            } for model in add_models]

        for model in custom_app_model:
            app[0]['models'].append(model)

        return app_list


    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        app_list = self.extend_app_list_model(
            Page, INJECTION_MODELS, self.get_app_list(request))
        extra_context['app_list'] = app_list
        return super(CustomAdminSite, self).index(request, extra_context)

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
            'title': 'Table editor'
        }

        return TemplateResponse(request, 'admin/table_editor.html', context)


custom_admin_site = CustomAdminSite(name='custom_admin')


class AbstractModelAdmin(admin.ModelAdmin):
    """
    Model admin with injection models related by any db-relations

    All options should look like Dict[Model name: Any-options]
    ex.:
        list_filter_options = {
            'page': ['is_active'],
            'product': ['is_active', PriceRange],
            'category': ['is_active'],
        }

    We have two custom urls(add, changelist) for every models,
    they look like `model_name_add`, (ex. `product_changelist`)
    """

    # Custom settings
    model = None # List [self.model]
    injection_models = None # List[Model, Model,...]
    extra_queries = {} # Dict[Model, query]
    list_filter_options = {} # Example of options in PageAdmin class
    search_fields_options = {}
    list_display_options = {}
    list_display_links_options = {}
    inlines_fieldset_options = {}

    # ModelAdmin setting
    list_per_page = 50
    save_on_top = True

    @property
    def inlines_options(self):
        return self.init_inlines_options()

    @property
    def change_view_options(self):
        """The change_view contain custom crumb options"""
        return self.init_view_options('crumb', 'changelist')

    @property
    def changelist_view_options(self):
        """The changelist_view contain custom crumb and add entity button options"""
        return self.init_view_options('add', 'add'), self.init_view_options('crumb', 'changelist')

    @property
    def add_view_options(self):
        """The changelist_view contain custom crumb options"""
        return self.init_view_options('crumb', 'changelist')

    @property
    def extra_queries_options(self):
        return {self.get_model_name_from_model(model): query
                for model, query in self.extra_queries.items()}

    @property
    def query_strategy(self)-> Dict[str, Dict[str, str] or Q]:
        """Dict look like { model_name: filter's kwargs}"""
        return {
            **{self.get_model_name_from_model(model): {'type': model._meta.db_table}
               for model in self.injection_models},
            **self.extra_queries_options,
        }

    # Helpers
    def get_model_name_from_request_path(self, path: str) -> str:
        """Get last path's item, it must be model_name, else return None"""
        url_part = path.rstrip('/').split('/')[-1]
        models_names = ([self.get_model_name_from_model(model) for model in self.injection_models]
                        + [self.get_model_name_from_model(self.model)])

        if url_part in models_names:
            return url_part

    def get_model_name_from_model(self, model: Model) -> str:
        """Shortcut for model._meta.model_name"""
        return model._meta.model_name # (model name could be 'product', 'page' etc.)

    def get_injection_urls(self, injection_model: Model, extra_url=None) -> Dict[str, type(url)]:
        """Get new urls for injection models"""
        extra_url = extra_url or {}
        model_name = self.get_model_name_from_model(injection_model)
        return {
            'changelist': url(r'^{}/$'.format(model_name), self.changelist_view,
                              name='{}_changelist'.format(model_name)),
            'add': url(r'^add/{}/$'.format(model_name), self.add_view,
                       name='{}_add'.format(model_name)),
            **extra_url
        }

    def init_inlines_options(self) -> Tuple[admin.StackedInline]:
        """Lazy initialization for inlines' class"""
        def __init_inline(injection_model):
            class Inline(admin.StackedInline):
                model = injection_model
                readonly_fields = ['id']
                fieldsets = self.inlines_fieldset_options.get(
                    self.get_model_name_from_model(injection_model), None)
            return Inline

        return tuple(__init_inline(model) for model in self.injection_models)

    def init_view_options(self, option_name, url_name) -> Dict[str, Dict[str, str]]:
        """
        Initialization view options
        :return {
            Model name:
                {option's name (ex. crumb): option's url (ex. custom_admin:product_add)}
        }
        """
        get_url_name = lambda model: self.get_injection_urls(model)[url_name].name
        admin_name = self.admin_site.name

        return {
            self.get_model_name_from_model(model): {
                '{}_name'.format(option_name): capfirst(model._meta.verbose_name),
                '{}_url'.format(option_name): '{}:{}'.format(admin_name, get_url_name(model))
            } for model in self.injection_models
            }

    def patch_by_options(self, request_path,
                         options: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        current_model = self.get_model_name_from_request_path(request_path)
        if current_model in options:
            return options[current_model]

    # Override admin methods
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add extra context for crumbs"""
        extra_context = extra_context or {}
        current_model = self.model.objects.get(id=object_id) # (ex. shopelectro_product)

        # The crumb options contain a injection model's name only
        for model_name in self.change_view_options:
            if model_name in current_model.type:
                crumb = self.change_view_options[model_name]
                extra_context.update(
                    {**crumb,
                     'model_name': current_model.model._meta.model_name, # context for upload image
                     'entity_id': current_model.model.id,
                     'show_save': False})

        return super(AbstractModelAdmin, self).change_view(request, object_id, form_url,
                                                           extra_context)

    def changelist_view(self, request, extra_context=None):
        """Add extra context for crumbs"""
        extra_context = extra_context or {}

        add, crumb = [self.patch_by_options(request.path, option)
                      for option in self.changelist_view_options]

        if crumb and add:
            extra_context.update(**crumb, **add)

        return super(AbstractModelAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        crumb = self.patch_by_options(request.path, self.add_view_options)

        if crumb:
            extra_context.update(**crumb)

        return super(AbstractModelAdmin, self).add_view(request, form_url, extra_context)

    def get_urls(self):
        """Inject custom urls for INJECTION_MODELS"""
        admin_urls = super(AbstractModelAdmin, self).get_urls()
        custom_urls = list(chain(*[self.get_injection_urls(model).values()
                                   for model in self.injection_models]))
        return custom_urls + admin_urls

    def get_queryset(self, request):
        """Inject the logic definition of queryset"""
        queryset = super(AbstractModelAdmin, self).get_queryset(request)
        current_model = self.get_model_name_from_request_path(request.path)
        strategy = self.query_strategy

        if current_model in strategy:
            query = strategy[current_model]
            queryset = (queryset.filter(**query) if isinstance(query, dict)
                        else queryset.filter(query))

        return queryset

    def get_inline_instances(self, request, obj=None):
        """Inject the logic definition of inlines"""
        current_model = self.get_model_name_from_request_path(request.path)
        if not obj and not current_model:
            self.inlines = [] # Page with create Pages' entity
        elif obj:
            # obj is Pages entity with field type (ex. shopelectro_product)
            page_type = obj.type
            # Page with change Product or Category entity
            self.inlines = [inline for inline in self.inlines_options
                            if self.get_model_name_from_model(inline.model) in page_type]
        else:
            # Page with create Product or Category entity
            self.inlines = [inline for inline in self.inlines_options
                            if self.get_model_name_from_model(inline.model) == current_model]

        return super(AbstractModelAdmin, self).get_inline_instances(request, obj)

    def get_list_display(self, request):
        """Inject the logic definition of list_display"""
        self.list_display = self.patch_by_options(request.path, self.list_display_options)
        return super(AbstractModelAdmin, self).get_list_display(request)

    def get_list_display_links(self, request, list_display):
        """Inject the logic definition of list_display_links"""
        self.list_display_links = self.patch_by_options(request.path, self.list_display_links_options)
        return super(AbstractModelAdmin, self).get_list_display_links(request, list_display)

    def get_search_fields(self, request):
        """Inject the logic definition of search_fields"""
        self.search_fields = self.patch_by_options(request.path, self.search_fields_options)
        return super(AbstractModelAdmin, self).get_search_fields(request)

    def get_list_filter(self, request):
        """Inject the logic definition of list_filter"""
        self.list_filter = self.patch_by_options(request.path, self.list_filter_options)
        return super(AbstractModelAdmin, self).get_list_filter(request)


class PageAdmin(AbstractModelAdmin):

    model = Page
    injection_models = INJECTION_MODELS
    extra_queries = {model: Q(type='custom') | Q(type='page')}

    # Filters
    list_filter_options = {
        'page': ['is_active'],
        'product': ['is_active', PriceRange],
        'category': ['is_active'],
    }

    # Search
    search_fields_options = {
        'page': ['title', '_parent__title'],
        'product': ['title', '_parent__title', 'shopelectro_product__price'],
        'category': ['title', '_parent__title']
    }

    # List display
    list_display_options = {
        'page': ['id', 'title', 'custom_parent', 'is_active'],
        'product': ['id', 'title', 'custom_category', 'price', 'links', 'is_active'],
        'category': ['id', 'title', 'custom_category_parent', 'is_active']
    }
    list_display_links_options = {
        'page': ['title'],
        'product': ['title'],
        'category': ['title'],
    }

    # Custom fields
    def price(self, model):
        return model.model.price

    price.short_description = 'Price'
    price.admin_order_field = 'shopelectro_product__price'

    def links(self, model):
        context = {
            'site_url': model.get_absolute_url(),
        }

        return render_to_string('admin/includes/items_list_row.html', context)

    links.short_description = 'Link'

    def custom_parent(self, model):
        if not model.parent:
            return

        parent = model.parent
        url = reverse('custom_admin:pages_page_change', args=(parent.id,))

        return format_html(
            '<a href="{url}">{parent}</a>',
            parent=parent,
            url=url
        )

    custom_parent.short_description = 'Parent'
    custom_parent.admin_order_field = '_parent__title'

    def custom_category(self, model):
        if not model.model.category:
            return

        category = model.model.category
        url = reverse('custom_admin:pages_page_change', args=(category.id,))

        return format_html(
            '<a href="{url}">{category}</a>',
            category=category.name,
            url=url
        )

    custom_category.short_description = 'Category'
    custom_category.admin_order_field = '_parent__title'

    def custom_category_parent(self, model):
        if not model.model.parent:
            return

        category = model.model.parent
        url = reverse('custom_admin:pages_page_change', args=(category.id,))

        return format_html(
            '<a href="{url}">{category}</a>',
            category=category.name,
            url=url
        )

    custom_category_parent.short_description = 'Parent'
    custom_category_parent.admin_order_field = '_parent__title'

    # Fieldsets
    fieldsets = (
        ('Дополнительные характеристики', {
            'classes': ('seo-chars'),
            'fields': (
                'position',
                'content',
            )
        }),
        ('Параметры страницы', {
            'classes': ('secondary-chars',),
            'fields': (
                ('title', 'id',),
                ('keywords', '_h1'),
                'is_active',
                'description',
                'seo_text'
            )
        })
    )

    inlines_fieldset_options = {
        'product':
            ((None, {
                'classes': ('primary-chars'),
                'fields': (
                    ('name', 'id',),
                    'category',
                    'price',
                    ('purchase_price', 'wholesale_small', 'wholesale_medium', 'wholesale_large',),
                    ('in_stock', 'is_popular')
                )
            }),),
        'category':
            ((None, {
                'classes': ('primary-chars'),
                'fields': (
                    ('name', 'id',),
                    'parent',
                    'position'
                )
            }),),
    }

    readonly_fields = ['id']

    # Actions
    actions = ['make_items_active', 'make_items_non_active']

    def make_items_active(self, request, queryset):
        updated_rows = queryset.update(is_active=1)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request,
                          '{} marked as active.'.format(message_prefix))

    make_items_active.short_description = 'Активировать страницы'

    def make_items_non_active(self, request, queryset):
        updated_rows = queryset.update(is_active=0)
        message_prefix = after_action_message(updated_rows)

        self.message_user(request,
                          '{} marked as non-active.'.format(message_prefix))

    make_items_non_active.short_description = 'Деактивировать страницы'


custom_admin_site.register(Page, PageAdmin)
