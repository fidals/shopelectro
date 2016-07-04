"""
Shopelectro image module for getting Model images
from media root.
"""

import os
from django.conf import settings


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
