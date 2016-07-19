"""Shopelectro Admin page only template tags."""

from django.conf import settings
from django import template
from django.apps import apps

from ..images import get_images_without_small

register = template.Library()


@register.inclusion_tag('admin/includes/images_list.html')
def entity_images(entity):
    """:return: Entity images without small variant"""

    model_type = type(entity).__name__
    app_name = settings.MODEL_TYPES.get(model_type)

    if not app_name:
        return

    instance = apps.get_model(app_label=app_name['app_name'],
                              model_name=model_type)
    model = instance.objects.get(id=entity.id)
    images_folder = app_name['dir_name']

    return {
        'images': get_images_without_small(model, images_folder)
    }
