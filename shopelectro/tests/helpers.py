import base64
import re
from contextlib import contextmanager

from django.conf import settings
from django.test import LiveServerTestCase, override_settings
from selenium.common.exceptions import InvalidElementStateException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Remote  # We use this instead of standard selenium

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

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Remote(
            command_executor=settings.SELENIUM_URL,
            desired_capabilities=DesiredCapabilities.CHROME
        )
        # @todo #371:15m Move selenium timeout to env var. stb2
        #  To be able to change it from drone without touching code.
        cls.wait = WebDriverWait(cls.browser, 60)
        cls.browser.implicitly_wait(30)
        cls.browser.set_page_load_timeout(30)
        # Fresh created browser failures on maximizing window.
        # This bug is won't fixed by selenium guys https://goo.gl/6Ttguf
        # Ohh, so selenium is so selenium ...
        # UPD 19.05.18: Seems it works, so we enable it to reduce number of errors
        cls.browser.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()

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

    # @todo #300:60m Use or create clear selenium.WebElement behaviour system.from
    #  Currently we return element from click method.
    #  It's not clear design decision. Use or create your own behaviour system.
    #  Some pipeline like WebElement or custom one.
    #  Maybe page objects pattern will be helpful:
    #  http://selenium-python.readthedocs.io/page-objects.html
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
