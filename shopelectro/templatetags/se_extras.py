import datetime

from django import template

register = template.Library()


@register.simple_tag
def time_to_call():
    """Return time when SE-manager will call the client based on current datetime."""
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
