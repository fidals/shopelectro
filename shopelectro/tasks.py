from contextlib import contextmanager

from django.conf import settings
from django.core.management import call_command
from selenium.common.exceptions import WebDriverException

from shopelectro import selenium
from shopelectro.celery import app
from shopelectro.report import TelegramReport
from shopelectro.models import CategoryPage
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

# @todo #690:30m Schedule check_purchase in the celery beat.


@app.task(
    bind=True,
    autoretry_for=(WebDriverException, AssertionError),
    retry_kwargs={'max_retries': settings.CHECK_PURCHASE_RETRIES},
)
def check_purchase(self):
    try:
        driver = selenium.SiteDriver(site_url=settings.BASE_URL)
        category_page = selenium.CategoryPage(driver, CategoryPage.objects.first().slug)
        category_page.load()
        category_page.add_to_cart()

        order_page = selenium.OrderPage(driver)
        order_page.load()
        order_page.fill_contacts()
        order_page.make_order()

        success_page = selenium.SuccessPage(driver)
        assert success_page.is_success()
    except (WebDriverException, AssertionError) as err:
        if self.request.retries + 1 > self.max_retries:
            # report on the last attempt
            TelegramReport().send(f'Can\'t buy a product. Got the error: {err}')
        raise err
