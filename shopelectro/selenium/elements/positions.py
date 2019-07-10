from contextlib import contextmanager

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from shopelectro.selenium import SiteDriver, elements


class Positions:

    def __init__(self, driver: SiteDriver, position_type: elements.Product, locator):
        self.driver = driver
        self.position_type = position_type
        self.condition = EC.presence_of_all_elements_located(locator)

    @contextmanager
    def wait_changes(self):
        def are_changed(_):
            try:
                return positions_before != self.all()
            except TimeoutException:
                # An exception can be raised from a position's equality method.
                # In most cases this means that some positions are stale,
                # so we continue waiting changes.
                return False

        positions_before = self.all()
        yield
        self.driver.wait.until(are_changed)

    def first(self) -> elements.Product:
        return self.position_type(self.driver, 0)

    def all(self) -> [elements.Product]:
        try:
            # use short_wait to avoid long pauses in case of the empty cart
            positions_count = len(self.driver.short_wait.until(
                self.condition
            ))
        except TimeoutException:
            positions_count = 0

        return [self.position_type(self.driver, i) for i in range(positions_count)]
