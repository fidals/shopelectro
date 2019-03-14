import typing

from django import http
from django_user_agents.utils import get_user_agent

from pages.request_data import Request
from shopelectro.exception import Http400


class Catalog(Request):
    PRODUCTS_ON_PAGE_PC = 48
    PRODUCTS_ON_PAGE_MOB = 12
    VIEW_TYPES = ['list', 'tile']

    @property
    def slug(self):
        return self.url_kwargs.get('slug', '')

    @property
    def sorting_index(self):
        return int(self.url_kwargs.get('sorting', 0))

    @property
    def tags(self) -> str:
        """:return: 'color=red&size=large' for example."""
        return self.url_kwargs.get('tags')

    @property
    def length(self):
        """Max size of products list depends on the device type."""
        is_mobile = get_user_agent(self.request).is_mobile
        return (
            self.PRODUCTS_ON_PAGE_MOB
            if is_mobile else self.PRODUCTS_ON_PAGE_PC
        )

    def get_view_type(self):
        view_type = self.request.session.get('view_type', 'tile')
        assert view_type in self.VIEW_TYPES
        return view_type

    @property
    def pagination_page_number(self):
        return int(self.request.GET.get('page', 1))

    @property
    def pagination_per_page(self):
        return int(self.request.GET.get('step', self.length))


# @todo #723:60m  Create separated request_data.Pagination class.
#  And may be remove `LoadMoreRequestData` class.
class LoadMore(Catalog):

    def __init__(
        self, request: http.HttpRequest, url_kwargs: typing.Dict[str, str]
    ):
        super().__init__(request, url_kwargs)
        self.offset = int(self.url_kwargs.get('offset', 0))
        if self.offset < 0:
            raise Http400()

    @property
    def pagination_page_number(self):
        # increment page number because:
        # 11 // 12 = 0, 0 // 12 = 0 but it should be the first page
        # 12 // 12 = 1, 23 // 12 = 1, but it should be the second page
        return (self.offset // self.pagination_per_page) + 1
