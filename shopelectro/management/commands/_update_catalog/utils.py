import glob
import os
import shutil
import subprocess
from collections import namedtuple
from contextlib import contextmanager
from itertools import chain
from typing import Iterator
from uuid import uuid4
from xml.etree import ElementTree

from django.conf import settings


UUID4_LEN = len(str(uuid4()))
NOT_SAVE_TEMPLATE = '{entity} with name="{name}" has no {field}. It\'ll not be' \
                    ' saved'


_Config = namedtuple(
    typename='Config',
    field_names=[
        'fetch_callback',
        'xml_path_pattern',
        'xpath_queries',
        'extra_options',
    ]
)


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

        return (ElementTree.parse(file) for file in xml_files)

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
        (ex. files with products names or prices)
        """
        return chain.from_iterable(
            self.fetch_callback(file, self)
            for file in self.parsed_files
        )


@contextmanager
def download_catalog(destination):
    """
    Download catalog's xml files and delete after handle them.
    """
    wget_command = (
        'wget -r -P {} ftp://{}:{}@{}/webdata'
        ' 2>&1 | grep "время\|time\|Downloaded"'.format(
            destination,
            settings.FTP_USER,
            settings.FTP_PASS,
            settings.FTP_IP,
        )
    )

    subprocess.run(wget_command, shell=True)
    assert os.path.exists(os.path.join(destination, settings.FTP_IP)), 'Files do not downloaded...'
    print('Download catalog - completed...')

    try:
        yield
    finally:
        # remove downloaded data
        shutil.rmtree(os.path.join(destination, settings.FTP_IP))
