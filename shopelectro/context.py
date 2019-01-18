from functools import partial

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
            'skip_canonical': tags_qs.exists(),
        }
