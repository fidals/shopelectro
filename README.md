[![Build Status](https://travis-ci.org/fidals/shopelectro.svg?branch=master)](https://travis-ci.org/fidals/shopelectro)
[![PDD status](http://www.0pdd.com/svg?name=yegor256/0pdd)](http://www.0pdd.com/p?name=fidals/shopelectro)

# shopelectro
shopelectro.ru site's code

### Install dependencies
Run `pip install --user -r requirements.txt`


### Configuring host-specific settings
All host-specific settings should be placed in `shopelectro.settings.local`
What needs to be specified:
- Database:
```
DATABASES = {
  'default': {
      'ENGINE': 'django.db.backends.postgresql_psycopg2',
      'NAME': 'test',
      'USER': 'John Doe',
      'PASSWORD': '123',
      'HOST': '',
      'PORT': '',
  },
}
```
- Mailer configuration:
```
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'john@doe.net'
EMAIL_HOST_PASSWORD = '123'
DEFAULT_FROM_EMAIL = 'john@doe.net'
DEFAULT_TO_EMAIL = 'john@doe.net'
SHOP_EMAIL = 'john@doe.net'
```
- Domain name (needed for sites framework):
```
SITE_DOMAIN_NAME = www.example.com
```


### Running tests
There are 6 types of tests in this project:
- commands tests (testing output of management commands)
- models (shopelectro-specific behaviour)
- views (using Django's TestClient)
- selenium (using Selenium)
- wholesale (wholesale algorithms)
- tests in `refarm-*` applications

You can run them all at once by running `python manage.py common_test` command.

Also, you can run shopelectro tests only by running `python manage.py test`


### Available managements commands
- `catalog` - import catalog from 1C, create all prices.
- `excel` - generate Excel file with prices
- `price` - generate .yml price files for YM and Price.ru.
- `redirects` - insert the old and new path to django_redirect table and update default domain name to
                                 the actual.
- `test_db` - generate random testing data. Runs only on `test` database to prevent mistakes.


### Install selenium
- Install Selenium: `pip install selenium`
- Install [Selenium ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- Start Django's development server `python manage.py runserver`
- Run tests: `python manage.py test` and go have a coffee :)

# Useful information
Some useful information for site development

## Page types list

**DB pages**:
- Category
- Product
- Static
- List of static
**Struct pages**:
- Main
- Category tree
- Order
- Search
