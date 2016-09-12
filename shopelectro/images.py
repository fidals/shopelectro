"""
Shopelectro image module for getting Model images
from media root.
"""

import os
from PIL import Image

from django.conf import settings

DEFAULT_SIZE = 800, 800
PREVIEW_SIZE = 300, 300


def upload(model_type, model_id, files):
    """Upload image for an entity of a given type_ with given id_."""

    def name_and_extension(file):
        return str(file).rsplit('.', 1)

    def create_file(file, directory, name=None, size=DEFAULT_SIZE):
        """
        Create file (physically) in a given directory.

        Accepts:
            file - InMemoryFileObject
            dir - path to directory where the file will be saved
            name - non-default name for a file.
                   If not specified, file will be saved with uploaded name.
            size - tuple of sizes. File will be resized if its sizes > given size.
        """
        uploaded_name, ext = name_and_extension(file)
        name = name or uploaded_name

        if not os.path.exists(directory):
            os.makedirs(directory)

        image = Image.open(file)

        if image.size > size:
            image = image.resize(size)

        return image.save(os.path.join(directory, '{}.{}'.format(name, ext)))

    def is_main_image(file):
        """Main image is an image which name contains 'main' substring."""
        return 'main' in name_and_extension(file)[0]

    upload_dir = os.path.join(
        settings.MEDIA_ROOT, '{}/{}'.format(model_type, model_id))

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

    images = [img for img in get_all_images(model) if img.find(size) != -1]
    if images:
        image = os.path.join(settings.MEDIA_URL, images[0])
    else:
        image = os.path.join(settings.STATIC_URL, 'images', settings.IMAGES['thumbnail'])
    return image


def get_images_without_small(model, url='products'):
    """Return Model images without small variant"""

    return [img for img in get_all_images(model, url)
            if img.find(settings.IMAGES['small']) == -1]
