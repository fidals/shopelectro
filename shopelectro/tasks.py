from django.core.management import call_command

from shopelectro.celery import app


@app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=30)
def update_products():
    call_command('update_products')
