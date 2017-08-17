from contextlib import contextmanager

from django.core.management import call_command

from shopelectro.celery import app
from shopelectro.management.commands._update_catalog import utils


@contextmanager
def report():
    try:
        yield
    except Exception as error:
        utils.report(str(error))
        raise error


@app.task
def generate_price_files():
    with report():
        call_command('price')
        print('Generate prices complete.')


@app.task
def generate_excel_file():
    with report():
        call_command('excel')
        print('Generate excel complete.')


@app.task
def collect_static():
    with report():
        call_command('collectstatic', '--noinput')


@app.task
def update_catalog_command():
    with report():
        call_command('update_catalog')


@app.task
def update_default_templates():
    with report():
        call_command('update_default_templates')


@app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=60*10)  # Ignore PycodestyleBear (E226)
def update_catalog():
    # http://docs.celeryproject.org/en/latest/userguide/canvas.html#map-starmap
    return [
        update_catalog_command(),
        update_default_templates(),
        generate_price_files(),
        generate_excel_file(),
        collect_static()
    ]
