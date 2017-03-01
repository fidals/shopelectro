from django.core.management import call_command

from shopelectro.celery import app


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
def update_products():
    call_command('update_products')


@app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=30)
def update_catalog():
    # http://docs.celeryproject.org/en/latest/userguide/canvas.html#map-starmap
    return [
        update_products(),
        generate_price_files(),
        generate_excel_file(),
        collect_static()
    ]
