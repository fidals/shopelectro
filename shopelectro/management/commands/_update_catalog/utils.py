import glob
import logging
import math
import os
import shutil
import subprocess
import time
from contextlib import contextmanager
from itertools import chain
from typing import Iterator, Dict
from uuid import UUID
from xml.etree import ElementTree

import requests
from django.conf import settings

from shopelectro.exception import DownloadFilesError

logger = logging.getLogger(__name__)
DOWNLOAD_FILES_TIMEOUT = 40.0
UUID_TYPE = str
Data = Dict[str, Dict[str, dict]]
NOT_SAVE_TEMPLATE = '{entity} with name="{name}" has no {field}. It\'ll not be' \
                    ' saved'


def floor(x: float, precision=0) -> float:
    """
    The same behaviour as `math.floor`, but with precision.

    >>> floor(1.234, precision=2)  # result: 1.23
    """
    k = 10**precision
    return math.floor(x * k) / k


def is_correct_uuid(uuid_):
    try:
        val = UUID(uuid_)
    except (ValueError, TypeError):
        return False
    return str(val) == uuid_


class XmlFile:

    namespace = '{urn:1C.ru:commerceml_2}'

    def __init__(self, fetch_callback, xml_path_pattern, xpath_queries,
                 extra_options=None):
        self.fetch_callback = fetch_callback
        self.xml_path_pattern = xml_path_pattern
        self.xpath_queries = xpath_queries
        self.extra_options = extra_options or {}

    @property
    def parsed_files(self):
        """Get parsed xml files, that matched the path pattern."""
        xml_files = glob.glob(os.path.join(
            settings.ASSETS_DIR, self.xml_path_pattern
        ))
        assert xml_files, 'Files on path {} does not exist.'.format(
            self.xml_path_pattern
        )
        return [ElementTree.parse(file) for file in xml_files]

    @property
    def xpaths(self):
        """Get xpath queries for xml."""
        return {
            name: query.format(self.namespace)
            for name, query in self.xpath_queries.items()
        }

    def get_data(self) -> Iterator:
        """
        Get data from xml files.

        Example files with products names or prices.
        """
        return chain.from_iterable(
            self.fetch_callback(file, self)
            for file in self.parsed_files
        )


@contextmanager
def collect_errors(error_types: tuple):
    errors = []

    @contextmanager
    def collect():
        try:
            yield
        except error_types as error:
            errors.append(error)
    yield collect
    if errors:
        raise errors[0]


@contextmanager
def download_catalog(destination):
    """Download catalog's xml files and delete after handle them."""
    wget_command = (
        'wget -r -P {} ftp://{}:{}@{}/webdata/'
        ' 2>&1 | grep "время\|time\|Downloaded"'.format(
            destination,
            settings.FTP_USER,
            settings.FTP_PASS,
            settings.FTP_IP,
        )
    )

    try:
        subprocess.run(wget_command, timeout=DOWNLOAD_FILES_TIMEOUT, shell=True)
    except subprocess.TimeoutExpired as e:
        raise DownloadFilesError(str(e))

    assert os.path.exists(os.path.join(
        destination, settings.FTP_IP)), 'Files do not downloaded...'
    logger.info('Download catalog - completed...')

    try:
        yield
    finally:
        # remove downloaded data
        shutil.rmtree(os.path.join(destination, settings.FTP_IP))


def report(error):
    report_url = getattr(settings, 'SLACK_REPORT_URL', None)
    if report_url is not None:
        requests.post(
            url=report_url,
            json={
                'text': '*Не удалось обновить каталог Shopelectro.*\n'
                        '*Время*: {}\n'
                        '*Ошибка*: {}'.format(time.ctime(), error),
            }
        )
