from collections import namedtuple

from django.conf import settings
from django.shortcuts import _get_queryset
from django.urls import reverse_lazy

from search import views as search_views, search as search_engine
from pages.models import Page
from pages.models import Page

from shopelectro.models import Product, Category


class AdminAutocomplete(search.AdminAutocomplete):
    """Override model_map for autocomplete."""

    model_map = MODEL_MAP


def search_entities_factory(fields, redirect_field=None):
    """
    Makes tuple of Search class instances. Elements depend on models to be
    searched for.
    :param fields: dictionary of lists of query lookups corresponding to models
    :param redirect_field: query lookup for instant redirect to custom page
    """
    entities = namedtuple('SearchEntities', 'category, product, pages')

    entities.category = search_engine.Search(
        name='category',
        qs=Category.objects.all(),
        fields=fields['category'],
    )

    entities.product = search_engine.Search(
        name='product',
        qs=Product.objects.all(),
        fields=fields['product'],
        redirect_field=redirect_field
    )

    entities.pages = search_engine.Search(
        name='page',
        qs=Page.objects.all(),
        fields=fields['pages'],
    )
    return entities

class Search(search.Search):
    """Override model references to SE-specific ones."""

    model_map = MODEL_MAP




class AdminAutocomplete(search_views.AdminAutocomplete):

    search_entity_objects = search_entities_factory({
        'category': ['name'],
        'product': ['name'],
        'pages': ['name']
    })

    search_entities = [
        search_entity_objects.category,
        search_entity_objects.product,
        search_entity_objects.pages
    ]


class Search(search_views.SearchView):

    search_entity_objects = search_entities_factory({
        'category': ['name'],
        'product': ['name'],
        'pages': ['name']
    }, 'vendor_code')

    redirect_search_entity = search_entity_objects.product
    search_entities = [
        search_entity_objects.category,
        search_entity_objects.product,
        search_entity_objects.pages
    ]

    redirect_field = 'vendor_code'


class Autocomplete(search_views.Autocomplete):

    search_entity_objects = search_entities_factory({
        'category': ['name'],
        'product': ['name', 'vendor_code'],
        'pages': ['name']
    })

    search_entities = [
        search_entity_objects.category,
        search_entity_objects.product,
        search_entity_objects.pages
    ]

    entity_fields = {
        'category': ['name', 'url'],
        'product': ['name', 'price', 'url']
    }

    see_all_label = settings.SEARCH_SEE_ALL_LABEL
