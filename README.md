# shopelectro
shopelectro.ru site's code

### Install dependencies
Run `pip install -r requirements.txt`


### Import actual data from .xml files
- Copy `categories.xml` and `products.xml` to project root
- Run: `python manage.py import categories.xml products.xml`

### Running Selenium-based tests
- Install Selenium: `pip install selenium`
- Install [Selenium ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- Start Django's development server `python manage.py runserver`
- Run tests: `python manage.py test` and go have a coffee :)