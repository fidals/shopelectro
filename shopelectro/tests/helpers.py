import time

from django.test import LiveServerTestCase, override_settings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumrequests import Remote  # We use this instead of standard selenium

disable_celery = override_settings(USE_CELERY=False)
enable_russian_language = override_settings(
    LANGUAGE_CODE='ru-ru', LANGUAGES=(('ru', 'Russian'),)
)


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    ActionChains(browser).move_to_element(element).perform()


def context_click(browser, element):
    ActionChains(browser).context_click(element).perform()
    wait()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Remote(
            command_executor='http://se-selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        cls.browser.helpers.implicitly_wait(10)
        cls.browser.set_window_size(1920, 1080)

    @classmethod
    def tearDownClass(cls):
        """Close selenium session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()
