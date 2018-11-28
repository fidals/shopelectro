from django.test.runner import DiscoverRunner

# @todo #639:15m Move CheckedTagsRunner to refarm-site.
#  Reuse it in SE and STB.


class CheckedTagsRunner(DiscoverRunner):
    """Every test must be tagged."""

    def build_suite(self, *args, **kwargs):
        suite = super().build_suite(*args, **kwargs)
        check_tagged_tests(suite)
        return suite


def check_tagged_tests(suite):
    # get the tags processing from:
    # django.test.runner.filter_tests_by_tags
    # https://github.com/django/django/blob/master/django/test/runner.py#L717
    suite_class = type(suite)
    for test in suite:
        if isinstance(test, suite_class):
            check_tagged_tests(test)
        else:
            test_tags = set(getattr(test, 'tags', set()))
            test_fn_name = getattr(test, '_testMethodName', str(test))
            test_fn = getattr(test, test_fn_name, test)
            test_fn_tags = set(getattr(test_fn, 'tags', set()))
            if not test_tags.union(test_fn_tags):
                raise Exception(
                    f'{test_fn_name} is not tagged. You have to decorate it '
                    'with tag("slow") or tag("fast").'
                )
