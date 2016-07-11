"""
Shopelectro image module for getting Model images
from media root.
"""

import os
from PIL import Image

from django.conf import settings

DEFAULT_SIZE = 800, 800
PREVIEW_SIZE = 300, 300

def upload(type_, id_, files):
    """Upload image for an entity of a given type_ with given id_."""
    def create_file(file, dir, name=None, size=DEFAULT_SIZE):
        """
        Create file (physically) in a given directory.

        Accepts:
                file - InMemoryFileObject
                dir - path to directory where the file will be saved
                name - non-default name for a file.
                       If not specified, file will be saved with uploaded name.
                size - tuple of sizes. File will be resized if its sizes > given size.
        """
        uploaded_name, ext = str(file).split('.')
        name = name or uploaded_name

        if not os.path.exists(dir):
            os.makedirs(dir)

        image = Image.open(file)

        if image.size > size:
            image.resize(size)

        return image.save(os.path.join(dir, '{}.{}'.format(name, ext)))

    def is_main_image(file):
        """Main image is an image which name contains 'main' substring."""
        return 'main' in str(file)

    upload_dir = os.path.join(settings.MEDIA_ROOT, '{}/{}'.format(type_, id_))

    for file in files:
        create_file(file, upload_dir)
        if is_main_image(file):
            create_file(file, upload_dir, name='small', size=PREVIEW_SIZE)


def get_all_images(model, url='products'):
    """Return all Model images"""

    images_folder = '{}/{}'.format(url, model.id)
    media_dir = os.path.join(settings.MEDIA_ROOT, images_folder)

    try:
        images_array = [os.path.normpath(os.path.join(images_folder, file))
                        for file in os.listdir(media_dir)]
    except FileNotFoundError:
        return []

    return list(reversed(images_array))


def get_image(model, size=settings.IMAGES['large']):
    """
    Return main Model image in small|large variant.

    :return: large\small variant of Product image
    """

    image = [img for img in get_all_images(model) if img.find(size) != -1]
    return image[0] if image else settings.IMAGES['thumbnail']


def get_images_without_small(model, url='products'):
    """Return Model images without small variant"""

    return [img for img in get_all_images(model, url)
            if img.find(settings.IMAGES['small']) == -1]
