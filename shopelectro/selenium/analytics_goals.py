import abc

from shopelectro.selenium import SiteDriver

# @todo #929:30m Implement GoogleEcommerceGoals and YandexMetrikaGoals and use them in tests.


class Goals(abc.ABC):
    """Front-end reached goals."""

    def __init__(self, driver: SiteDriver):
        self.driver = driver

    @abc.abstractmethod
    def fetch(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, index: int):
        raise NotImplementedError

    def __bool__(self):
        return bool(list(self))


class YandexEcommerceGoals(Goals):  # Ignore PyDocStyleBear
    """
    Unwrap an excess nesting level common for every goal:
    [{"ecommerce": ...}] -> ...
    Structure docs: https://yandex.com/support/metrica/data/e-commerce.html
    """

    def __init__(self, driver: SiteDriver):
        super().__init__(driver)
        self.goals = []

    def fetch(self):
        self.goals = self.driver.execute_script('return window.dataLayer.results;')

    def __getitem__(self, index: int):
        return self.goals[index][0]

    def __iter__(self):
        for g in self.goals:
            yield g[0]
