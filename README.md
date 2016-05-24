# shopelectro
shopelectro.ru site's code

### Install dependencies
Run `pip install --user -r requirements.txt`


### Available managements commands
- `python manage.py import` - import catalog from 1C, create all prices.
- `python manage.py excel` - generate Excel file with prices
- `python manage.py price` - generate .yml price files for YM and Price.ru.

### Running Selenium-based tests
- Install Selenium: `pip install selenium`
- Install [Selenium ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- Start Django's development server `python manage.py runserver`
- Run tests: `python manage.py test` and go have a coffee :)