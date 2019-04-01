"""
Provide abstraction to work with selenium.

It is based on `pages` and `elements`.

The page object should encapsulate the mechanics required
to find and manipulate the data and combines elements to reach it.

The element provides interface to perform actions on it
and can be used on different pages.

https://selenium-python.readthedocs.io/page-objects.html
"""

from .driver import SiteDriver
from .pages import *
