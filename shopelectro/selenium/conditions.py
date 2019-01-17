def alphanumeric(text: str) -> str:
    return ''.join(filter(lambda c: c.isalnum(), text))


class TextPresentedInValue:
    """
    Check if the given text is present in the element's locator, text.

    Remove all non-alphanumeric characters before checking.
    """
    def __init__(self, locator, text):
        self.locator = locator
        self.text = alphanumeric(text)

    def __call__(self, driver):
        try:
            text = driver.find_element(*self.locator).get_attribute('value')
            return self.text in alphanumeric(text)
        except StaleElementReferenceException:
                return False
