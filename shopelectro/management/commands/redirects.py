"""Management command for transfer data to django_redirect table."""

import os
import json
import psycopg2

from django.core.management.base import BaseCommand
from django.conf import settings

from catalog.models import Category

class Command(BaseCommand):
    """
    Redirects command class.

    Insert the old and new path to django_redirect table and update default
    domain name to the actual.
    """
    JSON = 'redirect_links.json'
    CATALOG_ROOT = '/catalog/categories/'
    DB_CONFIG = settings.DATABASES['default']

    def handle(self, *args, **kwargs):
        links = self.get_data_from_json()
        categories = self.fetch_categories(links)
        conn, cur = self.connect_to_the_db()
        self.change_domain_name_in_the_db(cur)
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

    def change_domain_name_in_the_db(self, cur):
        """Change default domain name to the actual."""
        DOMAIN_NAME = settings.BASE_URL

        print("Domain name changed on {}.".format(DOMAIN_NAME))
        cur.execute(
            "UPDATE django_site SET domain=(%s), name=(%s);",
            (DOMAIN_NAME, DOMAIN_NAME)
        )

    def insert_data_to_django_redirect(self, cur, links, categories):
        """Insert new records in a django_redirect."""
        SITE_ID = settings.SITE_ID

        from_old_path = lambda category: self.CATALOG_ROOT + \
                                         links[str(category.id)] + "/"
        to_new_path = lambda category: self.CATALOG_ROOT + category.slug + "/"

        insertions_data = [(category.id,
                            SITE_ID,
                            from_old_path(category),
                            to_new_path(category)) for category in categories]

        print("Insert {} rows to django_redirect.".format(len(insertions_data)))
        cur.executemany(
            "INSERT INTO django_redirect VALUES (%s, %s, %s, %s);",
            insertions_data
        )

