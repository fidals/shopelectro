"""
Provide abstraction to work with selenium.

It is based on `pages` and `elements`.

`pages` contains representations of site's pages.
A page doesn't work directly with the selenium driver,
but combines the `elements`.

`elements` contains representation of page's elements.
An element provides interface to perform actions on it
and can be used on different pages.

https://selenium-python.readthedocs.io/page-objects.html
"""

from .driver import SiteDriver
from .pages import CategoryPage, OrderPage
