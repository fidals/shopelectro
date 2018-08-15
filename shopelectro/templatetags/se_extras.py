import datetime
import math

from django import template
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from django.urls import reverse

from images.models import ImageMixin
from pages.models import Page

from shopelectro.models import Category

register = template.Library()


@register.simple_tag
def roots():
    return sorted(
        filter(
            lambda x: x.page.is_active,
            Category.objects
            .select_related('page')
            # about get_cached_trees: https://goo.gl/rFKiku
            .get_cached_trees()
        ),
        key=lambda x: x.page.position,
    )


@register.simple_tag
def footer_links():
    return settings.FOOTER_LINKS


@register.filter
def class_name(model):
    """Return Model name."""
    return type(model).__name__


@register.simple_tag
def time_to_call():
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
        closing_time = (16, 30) if is_friday(t) else (17, 30)
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


@register.simple_tag
def full_url(url_name, *args):
    return settings.BASE_URL + reverse(url_name, args=args)


@register.filter
def humanize_price(price):
    return intcomma(floatformat(price, 0))


# Not good code, but duker at 06/10/2016 don't know how to fix it.
# It makes Image model very complex.
@register.simple_tag
def get_img_alt(entity: ImageMixin):
    product_alt = 'Фотография {}'
    logo_alt = 'Логотип компании Shopelectro'

    if not isinstance(entity, Page):
        return logo_alt

    # try one of this attributes to get pages name
    name_attrs = ['h1', 'title', 'name']
    entity_name = next(
        getattr(entity, attr)
        for attr in name_attrs
        if getattr(entity, attr)
    )
    return product_alt.format(entity_name)


@register.simple_tag
def main_image_or_logo(page: Page):
    """Used for microdata."""
    if hasattr(page, 'main_image') and page.main_image:
        return page.main_image.url
    else:
        return settings.STATIC_URL + 'images/logo.png'


@register.inclusion_tag('catalog/product_feedbacks_icons.html')
def icon_stars(rating=0):
    """Render set of rating icons based on 1 through 5 rating values."""
    full_icons = int(math.floor(rating))
    half_icons = 0 if rating == int(rating) else 1
    empty_icons = 5 - full_icons - half_icons

    return {
        'full_icons': range(full_icons),
        'half_icons': range(half_icons),
        'empty_icons': range(empty_icons),
    }
