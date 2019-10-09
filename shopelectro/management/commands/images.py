"""Create Image objects from folder with image files."""
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
        return (dir_ for dir_ in os.scandir(path) if dir_.is_dir())

    def iter_files(path: str):
        return (file_ for file_ in os.scandir(path) if file_.is_file())

    def get_page(product_id: int) -> Page:
        product_ = Product.objects.filter(vendor_code=product_id).first()
        return product_.page if product_ else None

    def create_image_model(file_, product_id: int, slug):
        file_short_name, _ = os.path.splitext(file_.name)

        # skip images, resized to small size
        if file_short_name == 'small':
            return

        # create Image model object based on current image
        page = get_page(product_id=product_id)
        if not page:
            return
        # don't use bulk create, because save() isn't hooked with it
        # http://bit.ly/django_bulk_create
        Image.objects.create(
            model=page,
            # autoincrement file names: '1.jpg', '2.jpg' and so on
            slug=slug,
            # copies file with to the new path on create
            image=ImageFile(open(file_.path, mode='rb')),
            is_main=(file_short_name == 'main')
        )

    if not os.path.isdir(IMAGES_ROOT_FOLDER_NAME) or len(Image.objects.all()):
        return

    # run over every image in every folder
    for dir_ in iter_dirs(IMAGES_ROOT_FOLDER_NAME):
        for slug_index, file in enumerate(iter_files(dir_.path)):
            create_image_model(
                file_=file,
                product_id=int(dir_.name),
                slug=str(slug_index)
            )
    # old folder stays in fs as backup of old photos


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        create_image_models()
