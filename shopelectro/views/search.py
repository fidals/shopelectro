"""
Shopelectro's search views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import _get_queryset

from pages.models import Page
from catalog.models import search as search_in_db
from catalog.views import search

from shopelectro.views.helpers import MODEL_MAP


# SEARCH VIEWS
class AdminAutocomplete(search.AdminAutocomplete):
    """Override model_map for autocomplete."""
    model_map = MODEL_MAP


class Search(search.Search):
    """Override model references to SE-specific ones."""
    model_map = MODEL_MAP

    def _search_product_by_id(self, term: str):
        return (
            _get_queryset(self.product).filter(vendor_code=term).first()
            if term.isdecimal() else None
        )


class Autocomplete(search.Autocomplete):
    """Override model references to SE-specific ones."""

    product_lookups = ['name__icontains', 'vendor_code__contains']

    search_url = reverse_lazy(
        Page.CUSTOM_PAGES_URL_NAME,
        kwargs={'page': 'search'}
    )

    model_map = MODEL_MAP
    see_all_label = settings.SEARCH_SEE_ALL_LABEL

    def search(self, term, limit, ordering=None):
        """Perform a search on models. Return evaluated QuerySet."""
        categories = search_in_db(
            term, self.category, lookups=self.lookups,
        )[:limit]

        products = search_in_db(
            term, self.product, self.product_lookups, ordering,
        )

        left_limit = limit - len(categories)
        products = products[:left_limit]

        return categories, products
