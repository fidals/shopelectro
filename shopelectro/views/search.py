from django.conf import settings

from search import views as search_views, search as search_engine

from shopelectro.models import Category, Product, ExcludedModelTPage


class Search(search_views.SearchView):
    def get_redirect_search_entity(self):
        return next(s for s in self.search_entities if s.name == 'product')

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            qs=Category.objects.filter(page__is_active=True),
            fields=['name'],  # Ignore CPDBear
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=Product.actives,
            fields=['name'],
            redirect_field='vendor_code',
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='page',
            qs=ExcludedModelTPage.objects.get_active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        )
    ]

    redirect_field = 'vendor_code'


class Autocomplete(search_views.AutocompleteView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            qs=Category.objects.filter(page__is_active=True),
            fields=['name', 'id'],
            template_fields=['name', 'url'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=Product.actives,
            fields=['name', 'id', 'vendor_code'],
            template_fields=['name', 'price', 'url'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='pages',
            qs=ExcludedModelTPage.objects.get_active(),
            fields=['name'],
            template_fields=['name', 'url'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        )
    ]

    see_all_label = settings.SEARCH_SEE_ALL_LABEL


class AdminAutocomplete(search_views.AdminAutocompleteView):

    # ignore CPDBear
    search_entities = [
        search_engine.Search(
            name='category',
            qs=Category.objects.filter(page__is_active=True),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='product',
            qs=Product.actives,
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        ),
        search_engine.Search(
            name='pages',
            qs=ExcludedModelTPage.objects.get_active(),
            fields=['name'],
            min_similarity=settings.TRIGRAM_MIN_SIMILARITY,
        )
    ]
