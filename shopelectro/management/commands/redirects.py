"""Management command for transfer data to django_redirect table."""

import os
import json
import psycopg2
from itertools import chain

from django.core.management.base import BaseCommand
from django.conf import settings

from shopelectro.models import Category


class Command(BaseCommand):
    """
    Redirects command class.

    Insert the old and new path to django_redirect table and update default
    domain name to the actual.
    """
    JSON = 'redirect_links.json'
    CATALOG_ROOT = '/catalog/categories/'
    LEGACY_CATALOG_ROOT = '/catalog/'
    DB_CONFIG = settings.DATABASES['default']

    def handle(self, *args, **kwargs):
        links = self.get_data_from_json()
        categories = self.fetch_categories(links)
        conn, cur = self.connect_to_the_db()
        self.clear_django_redirect(cur)
        self.insert_data_to_django_redirect(cur, links, categories)
        self.disconnect_from_the_db(conn)

    def get_data_from_json(self):
        """Get id and aliases from JSON."""
        with open(os.path.join(settings.BASE_DIR, self.JSON)) as links_json:
            return json.load(links_json)

    def fetch_categories(self, links):
        """Fetch categories with new aliases, for column new_path in table
        django_redirect."""
        return Category.objects.filter(
            id__in=[int(key) for key in links]
        ).exclude(
            slug__in=links.values()
        )

    def connect_to_the_db(self):
        """Connection to the database and create the cursor."""
        conn = psycopg2.connect(user=self.DB_CONFIG['USER'],
                                password=self.DB_CONFIG['PASSWORD'],
                                dbname=self.DB_CONFIG['NAME'],
                                host=self.DB_CONFIG['HOST'],
                                port=self.DB_CONFIG['PORT'])
        return conn, conn.cursor()

    def disconnect_from_the_db(self, conn):
        """Commit pending transaction to the database and disconnection."""
        conn.commit()
        conn.close()

    def clear_django_redirect(self, cur):
        DELETE_REDIRECTS = 'DELETE FROM django_redirect;'
        cur.execute(DELETE_REDIRECTS)

    def insert_data_to_django_redirect(self, cur, links, categories):
        """Insert new records in a django_redirect."""
        SITE_ID = settings.SITE_ID
        INSERT_REDIRECTS = 'INSERT INTO django_redirect (site_id, old_path, new_path) ' \
                           'VALUES (%s, %s, %s);'

        def get_legacy_old_path(category):
            return self.LEGACY_CATALOG_ROOT + links[str(category.id)] + '/'

        def get_old_path(category):
            return self.CATALOG_ROOT + links[str(category.id)] + '/'

        def get_new_path(category):
            return self.CATALOG_ROOT + category.slug + '/'

        insertions_data = list(chain(*[
            (
                (SITE_ID, get_old_path(category), get_new_path(category)),
                (SITE_ID, get_legacy_old_path(category), get_new_path(category))
            ) for category in categories])
        )

        print('Insert {} rows to django_redirect.'.format(len(insertions_data)))
        cur.executemany(INSERT_REDIRECTS, insertions_data)
