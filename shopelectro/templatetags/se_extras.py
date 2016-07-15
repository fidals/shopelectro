"""Shopelectro template tags"""

import datetime

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma

from shopelectro.models import Category
from shopelectro.images import get_images_without_small

register = template.Library()


@register.assignment_tag
def roots():
    return Category.objects.root_nodes().order_by('position')


@register.filter
def class_name(model):
    """Return Model name."""

    return type(model).__name__


@register.simple_tag
def time_to_call():
    """
    Return time when SE-manager will call the client based on
    current datetime.
    """

    def is_weekend(t):
        return t.weekday() > 4

    def is_friday(t):
        return t.weekday() == 4

    def not_yet_opened(t):
        current_time = (t.hour, t.minute)
        open_time = (10, 00)
        return current_time < open_time and not is_weekend(t)

    def is_closed(t):
        current_time = (t.hour, t.minute)
        if is_friday(t):
            closing_time = (16, 30)
        else:
            closing_time = (17, 30)
        return current_time > closing_time

    when_we_call = {
        lambda now: is_weekend(now) or (is_friday(now) and is_closed(now)): 'В понедельник в 10:30',
        lambda now: not_yet_opened(now): 'Сегодня в 10:30',
        lambda now: is_closed(now) and not (is_friday(now) or is_weekend(now)): 'Завтра в 10:30',
        lambda _: True: 'В течение 30 минут'
    }

    time_ = datetime.datetime.now()
    call = ' позвонит менеджер и обсудит детали доставки.'
    for condition, time in when_we_call.items():
        if condition(time_):
            return time + call


@register.filter
def upload_form(model):
    """Check if template with current Model should have upload form"""

    models_with_upload_form, model_type = (['Category', 'Product'],
                                           type(model).__name__)
    return model_type in models_with_upload_form


@register.inclusion_tag('prices/picture_tag.html')
def get_model_images(model):
    """Return Model images without small variant"""

    return {
        'dir_path': settings.BASE_URL + settings.MEDIA_URL,
        'images': get_images_without_small(model, url='products')
    }


@register.simple_tag
def full_url(path='index', *args):
    return settings.BASE_URL + reverse(path, args=args)


@register.filter
def humanize_price(price):
    return intcomma(floatformat(price, 0))
