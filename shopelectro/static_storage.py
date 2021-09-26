import os
import subprocess as sb
from django.conf import settings

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class DroppedPricesManifestStaticFilesStorage(ManifestStaticFilesStorage):
    def post_process(self, *args, **kwargs):
        yield from super().post_process(*args, **kwargs)
        sb.run(_drop_unused_prices_cmd(path=self.location), shell=True)


def _drop_unused_prices_cmd(path: str) -> str:
    def put_star_on(s: str) -> str:
        """
        Change the last point chat to chars '.*.'.

        >>> put_star_on('yandex.yml')
        'yandex.*.yml'
        >>> put_star_on('yandex.some.yml')
        'yandex.some.*.yml'
        """
        return s[::-1].replace('.', '.*.', 1)[::-1]
    return 'rm -f ' + ' '.join([
        os.path.join(path, put_star_on(name))
        for name in settings.UTM_PRICE_MAP.values()
    ])
