"""
Create serialized data for tests and store this data in json file.

Usage:
- create db named `test`
- fix your settings.DATABASES option
- purge your test db manually, if it had data before this usage
- launch this command
- now you have json file, that'll be used by our TDD tests
"""
import os
import shutil

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management import call_command
from django.core.management.base import BaseCommand

from images.models import Image, model_directory_path
from pages.models import Page, FlatPage, PageTemplate
from pages.utils import save_custom_pages, init_redirects_app

from shopelectro import models as se_models, tests as se_tests


class Command(BaseCommand):

    FIRST_IMAGE = os.path.join(
        os.path.dirname(os.path.abspath(se_tests.__file__)),
        'assets/deer.jpg'
    )
    SECOND_IMAGE = os.path.join(
        os.path.dirname(os.path.abspath(se_tests.__file__)),
        'assets/gold_deer.jpg'
    )

    PRODUCTS_WITH_IMAGE = [1, 113]

    def __init__(self):
        super(BaseCommand, self).__init__()
        self._product_id = 0
        self.group_names = [
            'Напряжение', 'Сила тока',
            'Мощность', settings.BRAND_TAG_GROUP_NAME,
        ]
        self.tag_names = [
            ['6 В', '24 В'],
            ['1.2 А', '10 А'],
            ['7.2 Вт', '240 Вт'],
            ['Apple', 'Microsoft'],
        ]

    def handle(self, *args, **options):
        self.prepare_db()
        save_custom_pages()
        init_redirects_app()

        roots = self.create_root(2)
        children = self.create_children(2, roots)
        deep_children = self.create_children(2, children)

        groups = self.create_tag_groups()
        tags = self.create_tags(groups)

        self.create_products(deep_children, tags)
        self.create_page()
        self.create_order()
        self.create_feedbacks()
        self.create_templates()
        self.rebuild_mptt_tree()
        self.save_dump()

    def prepare_db(self):
        # @todo #389:60m Set db name in `test_db` command. stb2
        #  Set name instead of asserting.
        #  You also should create/drop it with postgres driver.
        is_test_db = settings.DATABASES['default']['NAME'] == 'test'
        assert is_test_db, 'To create fixtures you have to create a database named "test".'
        call_command('migrate')
        self.purge_tables()

    @staticmethod
    def save_dump():
        """Save .json dump to fixtures."""
        call_command(
            'dumpdata',
            '--all',
            # I don't understand why we should use this options.
            # As well as ContentType model above.
            # I just followed this: http://bit.ly/so-contenttype-dump-solving
            '--natural-foreign',
            '--natural-primary',
            '--exclude', 'sites',
            output='shopelectro/fixtures/dump.json'
        )

    # @todo #645:30m Move test_db's product_id to generator. stb2
    #  Now it uses dirty autoincrement.
    @property
    def product_id(self):
        self._product_id += 1
        return self._product_id

    @staticmethod
    def create_root(count):
        get_name = 'Category #{}'.format
        return [
            se_models.Category.objects_.create(name=get_name(i))
            for i in range(count)
        ]

    @staticmethod
    def create_children(count, parents):
        name = 'Category #{} of #{}'

        def create_categories(name, parent):
            return se_models.Category.objects_.create(name=name, parent=parent)

        def get_name(number, parent=None):
            return name.format(number, parent)

        return list(
            create_categories(get_name(i, parent), parent)
            for i in range(count)
            for parent in parents
        )

    def create_products(self, categories, tags):
        def create_images(page: Page):
            def create_image(file_path, slug):
                # save files to media folder
                with open(file_path, mode='rb') as file_src:
                    # product "/catalog/products/2/" contains image
                    image = Image.objects.create(
                        model=page,
                        slug=slug,
                        image=ImageFile(file_src)
                    )
                    file_name = os.path.basename(file_src.name)
                    file_dst_path = os.path.join(
                        settings.MEDIA_ROOT,
                        model_directory_path(image, file_name)
                    )
                    shutil.copyfile(file_src.name, file_dst_path)

            create_image(file_path=self.FIRST_IMAGE, slug='deer')
            create_image(file_path=self.SECOND_IMAGE, slug='gold')

        def create_product(parent: se_models.Category, tags_, price_factor):
            product = se_models.Product.objects.create(
                id=self.product_id,
                # vendor_code should be differ from id for tests.
                vendor_code=self._product_id + 1,
                name='Product #{} of {}'.format(price_factor, parent),
                in_stock=price_factor % 3,
                price=price_factor * 100,
                category=parent,
                wholesale_small=price_factor * 75,
                wholesale_medium=price_factor * 50,
                wholesale_large=price_factor * 25
            )

            for tag in tags_:
                product.tags.add(tag)

            if product.id in self.PRODUCTS_WITH_IMAGE:
                create_images(product.page)
                create_images(product.page)

        def fill_with_products(to_fill, tags_, count):
            for category in to_fill:
                for i in range(1, count + 1):
                    create_product(category, tags_, price_factor=i)

        zipped_tags = list(zip(*tags))
        fill_with_products(
            to_fill=categories[4:], tags_=zipped_tags[0], count=25)
        fill_with_products(
            to_fill=categories[:4], tags_=zipped_tags[1], count=50)

    def create_tag_groups(self):
        for i, name in enumerate(self.group_names, start=1):
            yield se_models.TagGroup.objects.create(
                name=name,
                position=i,
            )

    def create_tags(self, groups):
        def create_tag(group_, position, name):
            return se_models.Tag.objects.create(
                group=group_,
                name=name,
                position=position,
            )

        for group, names in zip(groups, self.tag_names):
            yield [
                create_tag(group, i, name)
                for i, name in enumerate(names, start=1)
            ]

    @staticmethod
    def create_page():
        """Create only one page with type=FLAT_PAGE."""
        FlatPage.objects.create(
            slug='flat',
        )

    @staticmethod
    def create_order():
        se_models.Order.objects.create(
            pk=7,
            name='Test Name',
            phone='88005553535',
        )

    @staticmethod
    def create_feedbacks():
        feedbacks_count = 5

        def generate_feedback_data(index):
            return {
                'product': se_models.Product.objects.get(id=1),
                'rating': index,
                'name': 'User #{}'.format(index),
                'dignities': 'Some dignities.',
                'limitations': 'Some limitations.',
                'general': 'Some general opinion.'
            }

        for i in range(1, feedbacks_count + 1):
            se_models.ProductFeedback.objects.create(
                **generate_feedback_data(i)
            )

    @staticmethod
    def create_templates():
        page_template = PageTemplate.objects.create(
            name='{{ page.name }} name.',
            h1='{{ page.name }}{{ tag_titles }} h1.',
            keywords='{{ page.name }} keywords.',
            description='{{ page.name }} description.',
            title='{{ page.name }} title.',
            seo_text=(
                '{{ page.name }} seotext.'
                '{% for tag in tags %}{{ tag.name }}, {% endfor %}'
            )
        )

        se_models.ProductPage.objects.update(template=page_template)
        se_models.CategoryPage.objects.update(template=page_template)

    @staticmethod
    def rebuild_mptt_tree():
        se_models.Category.objects_.rebuild()
        Page.objects.rebuild()

    @staticmethod
    def purge_tables():
        call_command('flush', '--noinput')
