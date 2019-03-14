import base64
import re
import time
from contextlib import contextmanager

from django.conf import settings
from django.test import LiveServerTestCase, override_settings
from selenium.common.exceptions import InvalidElementStateException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium import SiteDriver

disable_celery = override_settings(USE_CELERY=False)
enable_russian_language = override_settings(
    LANGUAGE_CODE='ru-ru', LANGUAGES=(('ru', 'Russian'),)
)


def try_again_on_stale_element(try_count):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            def try_(count):
                try:
                    return func(*args, **kwargs)
                except InvalidElementStateException:
                    if count >= 0:
                        try_(count - 1)
            return try_(try_count)
        return wrapped
    return wrapper


def hover(browser, element):
    """Perform a hover over an element."""
    ActionChains(browser).move_to_element(element).perform()


def context_click(browser, element):
    ActionChains(browser).context_click(element).perform()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']
    host = settings.LIVESERVER_HOST

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super().setUpClass()
        cls.browser = SiteDriver(site_url=cls.live_server_url)
        # @todo #371:15m Move selenium timeout to env var. stb2
        #  To be able to change it from drone without touching code.
        cls.browser.implicitly_wait(30)
        cls.browser.set_page_load_timeout(settings.SELENIUM_TIMEOUT_SECONDS)
        # Fresh created browser failures on maximizing window.
        # This bug is won't fixed by selenium guys https://goo.gl/6Ttguf
        # Ohh, so selenium is so selenium ...
        # UPD 19.05.18: Seems it works, so we enable it to reduce number of errors
        # UPD 21.06.18: It does not work all times. When serv is loaded, this mech breaks.
        time.sleep(1.0)
        try:
            cls.browser.maximize_window()
        except WebDriverException:
            print('Failed to maximize window')  # Ignore CPDBear

    @property
    def wait(self):
        return self.browser.wait

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super().tearDownClass()

    @contextmanager
    def screen_fail(self, filename=''):
        """
        Save screen if WebDriverException occurred.

        :param filename: result file have name 'screen_{filename}.png'
        :return:
        """
        try:
            yield
        except WebDriverException as e:
            if settings.ENV_TYPE == 'LOCAL':
                screen_b64 = e.screen or self.browser.get_screenshot_as_base64()
                with open(f'screen__{filename}.png', 'wb') as f:
                    f.write(base64.b64decode(screen_b64.encode('ascii')))
            raise e

    def click(self, click_locator) -> WebElement:
        """Click on element in safe way and return element we clicked on."""
        dom_element = self.wait.until(
            EC.element_to_be_clickable(click_locator)
        )
        dom_element.click()
        return dom_element

    def send_keys_and_wait(self, keys: str, locator, expected_keys=''):
        """
        Safely send keys to element with given locator.

        :param keys: should consist of letters, digits and spaces. No special symbols
        """
        # `keys` should not contain special symbols.
        # For example backspace characters don't appear in input field.
        assert re.match(r'[\w\d\s\-_]+', keys, re.I | re.U), \
            'Form text should not contain special symbols'
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        str_keys = str(keys)
        el.send_keys(str_keys)
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                locator, expected_keys or str_keys
            )
        )

    def wait_page_loaded(self):
        """Wait while current page is fully loaded."""
        self.wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'html')))
