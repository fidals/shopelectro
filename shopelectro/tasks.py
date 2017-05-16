from datetime import timedelta

from django.core.management import call_command

from shopelectro.celery import app
from shopelectro.management.commands._update_catalog import utils


@app.task
def generate_price_files():
    call_command('price')
    print('Generate prices complete.')


@app.task
def generate_excel_file():
    call_command('excel')
    print('Generate excel complete.')


@app.task
def collect_static():
    call_command('collectstatic', '--noinput')


@app.task
def update_catalog_command():
    call_command('update_catalog')


@app.task
def update_default_templates():
    call_command('update_default_templates')


@app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=60*10)
def update_catalog():
    # http://docs.celeryproject.org/en/latest/userguide/canvas.html#map-starmap
    try:
        return [
            update_catalog_command(),
            update_default_templates(),
            generate_price_files(),
            generate_excel_file(),
            collect_static()
        ]
    except Exception as exc:
        utils.report(exc)
        raise exc
