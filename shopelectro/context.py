from functools import partial

from django.conf import settings

from catalog.newcontext import Context, Tags


class Page(Context):

    def __init__(self, page, tags: Tags):
        self._page = page
        self._tags = tags

    def context(self):
        def template_context(page, tag_titles, tags):
            return {
                'page': page,
                'tag_titles': tag_titles,
                'tags': tags,
            }

        tags_qs = self._tags.qs()
        self._page.get_template_render_context = partial(
            template_context, self._page, tags_qs.as_title(), tags_qs
        )

        return {
            'page': self._page,
        }


class ListParams(Context):

    def __init__(self, request_data: 'ProductListRequestData'):
        self.request_data = request_data

    def context(self) -> dict:
        return {
            'view_type': self.request_data.get_view_type(),
            'sorting_options': settings.CATEGORY_SORTING_OPTIONS.values(),
            'limits': settings.CATEGORY_STEP_MULTIPLIERS,
            'sort': self.request_data.sorting_index,
        }
