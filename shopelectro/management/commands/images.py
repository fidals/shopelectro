"""
Command in this module create Image objects from folder with image files
"""
import os

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from images.models import Image
from pages.models import Page
from shopelectro.models import Product


IMAGES_ROOT_FOLDER_NAME = os.path.join(settings.MEDIA_ROOT, 'products')


def create_image_models():

    def iter_dirs(path: str):
        return (folder_ for folder_ in os.scandir(path) if folder_.is_dir())

    def iter_files(path: str):
        return (file_ for file_ in os.scandir(path) if file_.is_file())

    def get_page(product_id: int) -> Page:
        try:
            product_ = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            # images folder can contain not existing product id
            return
        return product_.page

    def create_image_model():
        file_short_name, _ = os.path.splitext(file.name)

        # miss compressed images: 'small.jpg', for example
        if file_short_name == 'small':
            return

        # create Image model object based on current image
        page = get_page(product_id=int(folder.name))
        if not page:
            return
        # don't use bulk create, because save() isn't hooked with it
        # proof link: http://bit.ly/django_bulk_create
        image_model = Image(
            model=page,
            # autoincrement file names: '1.jpg', '2.jpg' and so on
            slug=str(slug_index),
            image=ImageFile(open(file.path, mode='rb')),
            is_main=(file_short_name == 'main')
        )
        image_model.save()

    if not os.path.isdir(IMAGES_ROOT_FOLDER_NAME):
        return

    # run over every image in every folder
    for folder in iter_dirs(IMAGES_ROOT_FOLDER_NAME):
        slug_index = 1
        for file in iter_files(folder.path):
            create_image_model()
            slug_index += 1
    # old folder stays in fs as backup of old photos


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        create_image_models()
