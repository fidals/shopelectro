# shopelectro
shopelectro.ru site's code

### Install dependencies
Run `pip install --user -r requirements.txt`


### Available managements commands
- `python manage.py catalog` - import catalog from 1C, create all prices.
- `python manage.py excel` - generate Excel file with prices
- `python manage.py price` - generate .yml price files for YM and Price.ru.
- `python manage.py redirects` - insert the old and new path to django_redirect table and update default domain name to
                                 the actual.

## Run Selenium-based tests

### Setup your shopelectro project
- Create admin user `python manage.py createsuperuser`
- Set admin panel credentials at your settings.py
```
# settings.py
ADMIN_LOGIN = 'user'
ADMIN_PASS = 'your_password'
```


### Install selenium
- Install Selenium: `pip install selenium`
- Install [Selenium ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- Start Django's development server `python manage.py runserver`
- Run tests: `python manage.py test` and go have a coffee :)

### Local settings
- DATABASES - settings for your database
- SITE_DOMAIN_NAME - this const needed for "sites" and sitemap frameworks. Format: www.example.com