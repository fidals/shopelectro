"""
Config storage for shopelectro.ru.
Every config-like option which doesn't belong to settings should be here.
"""
from django.conf import settings

pages = {
    'main': {
        'name': 'Батарейки, Аккумуляторы, ЗУ в СПб',
        'title': 'ShopElectro | Батарейки, Аккумуляторы, ЗУ в СПб',
        'h1': 'Батарейки, Аккумуляторы, ЗУ в СПб',
        'keywords': 'купить аккумуляторы, '
                    'купить батарейки, '
                    'купить зарядные устройства, купить блоки питания',
        'description': 'Купить Батарейки, Аккумуляторы, ЗУ в СПб. Доставка по России',
        'site_url': 'www.shopelectro.ru'
    },
    'navigation': {
        'name': 'О магазине. Выбор, заказ, оплата, доставка',
        'h1': 'Контакты, реквизиты, услуги',
        'title': 'ShopElectro | О магазине. Выбор, заказ, оплата, доставка',
        'keywords': 'Выбрать товар, заказать товар, оплатить товар, получить товар',
        'description': 'Как выбрать товар, заказать, оплатить и получить',
        'date_published': settings.SITE_CREATED,
    },
    'news': {
        'name': 'Новости магазина',
        'h1': 'Новости магазина',
        'title': 'ShopElectro | Новости магазина',
        'keywords': 'Новости shopelectro',
        'description': 'Новости магазина. Изменение цен, ассортимента, обсуживания',
        'date_published': settings.SITE_CREATED,
    },
    'article': {
        'name': 'Статьи о товарах',
        'h1': 'Статьи о товарах',
        'title': 'ShopElectro | Статьи о товарах',
        'keywords': 'батарейки, аккумуляторы, зу',
        'description': 'Как выбрать товар',
        'date_published': settings.SITE_CREATED,
    },
    'catalog': {
        'title': 'Карта каталога',
        'name': 'Каталог аккумов',
    },
}


def page_metadata(page):
    """
    Returns page metadata (e.g., name, title, h1 and so on) for a given page string.

    If such page doesn't have metadata, it throws ValueError.
    :param page: string page identifier
    :return: dict with metadata
    """
    try:
        return pages[page]
    except KeyError:
        raise ValueError('site data have not such page: ' + page +
                         '. Check your config.py')


def category_sorting(sorting_index=None):
    """
    Sorting options for Category page.

    Returns
        - a sorting option object in a form of dictionary, if sorting_index is specified
        - all options if it's not specified.
    """
    options = (
        {
            'label': 'Цене, сначала дешёвые',
            'field': 'price',
            'direction': ''
        },
        {
            'label': 'Цене, сначала дорогие',
            'field': 'price',
            'direction': '-'
        },
        {
            'label': 'Названию, А-Я',
            'field': 'name',
            'direction': ''
        },
        {
            'label': 'Названию, Я-А',
            'field': 'name',
            'direction': '-'
        },
        {
            'label': 'Артикулу',
            'field': 'id',
            'direction': ''
        }
    )

    if sorting_index is not None:
        chosen_option = options[sorting_index]
        return chosen_option['direction'] + chosen_option['field']
    return options


def cached_time() -> int:
    """Returns value of days for caching in seconds."""
    one_day_in_seconds = 86400
    days_to_cache = 60

    return one_day_in_seconds * days_to_cache

TOP_PRODUCTS = [291, 438, 1137, 2166, 2725, 2838, 3288, 3642, 3884, 3959]

# Tile on main page
MAIN_PAGE_TILE = {
    'accumulators': [
        {'name': 'Типоразмера ААА', 'alias': 'akkumuliatory-aaa'},
        {'name': 'Для радиомоделей и игрушек',
         'alias': 'akkumuliatory-dlia-radioupravliaemykh-modelei-i-igrushek'},
        {'name': 'Свинцово-кислотные',
         'alias': 'akkumuliatory-svintsovo-kislotnye-4-v-6-v-12-v-lca'},
        {'name': 'Внешние универсальные',
         'alias': 'vneshnie-universalnye-akkumuliatory'},
        {'name': 'Для ноутбуков', 'alias': 'akkumuliatory-dlia-noutbukov'},
        {'name': 'Адаптеры, отсеки и футляры',
         'alias': 'adaptery-otseki-i-futliary-dlia-akkumuliatorov'},
    ],
    'inverter': [
        {'name': 'Инверторы СОЮЗ', 'alias': 'invertory-soiuz'},
        {'name': 'Инверторы ROBITON', 'alias': 'invertory-robiton'},
        {'name': 'Преобразователи DC 24 В/12 В KALLER',
         'alias': 'preobrazovateli-napriazheniia-dc-24-v12-v-kaller'},
    ],
    'batteries': [
        {'name': 'Типоразмера АА', 'alias': 'batareiki-aa'},
        {'name': 'Часовые', 'alias': 'batareiki-chasovye'},
        {'name': 'Литиевые', 'alias': 'batareiki-litievye'},
    ],
    'lights': [
        {'name': 'Фотон', 'alias': 'fonari-foton'},
        {'name': 'Эра', 'alias': 'fonari-era'},
        {'name': 'Яркий Луч', 'alias': 'fonari-iarkii-luch'},
    ],
    'chargers': [
        {'name': 'Для фотоаппаратов',
         'alias': 'zariadnye-ustroistva-dlia-fotoapparatov'},
        {'name': 'Для видеокамер', 'alias': 'zariadnye-ustroistva-dlia-videokamer'},
        {'name': 'Для свинцовых',
         'alias': 'zariadnye-ustroistva-dlia-svintsovykh-akkumuliatorov'},
    ],
    'multimeters': [
        {'name': 'MY68 Master Professional',
         'alias': 'multimetry-master-professional'},
    ],
    'adapters': [
        {'id': 1, 'name': '220В для ноутбуков',
         'alias': 'bloki-pitaniia-dlia-noutbukov-ot-seti-220v'},
        {'id': 1, 'name': '12В для ноутбуков',
         'alias': 'bloki-pitaniia-dlia-noutbukov-ot-seti-12v'},
        {'id': 1, 'name': 'Трансформаторные',
         'alias': 'bloki-pitaniia-transformatornye'},
    ],
}

FOOTER_LINKS = {
    'services': [
        {'id': 1, 'name': 'Ремонт аккумуляторов', 'alias': 'remont-akkumulyatorov'},
        {'id': 1, 'name': 'Пайка на заказ', 'alias': 'soldering'},
        # {'id': 1, 'name': 'Доставка по России', 'alias': 'delivery#russia'},
    ],
    'articles': [
        {'id': 1, 'name': 'Аккумуляторная батарея', 'alias': 'Текст'},
        {'id': 1, 'name': 'Нанопроводниковый аккумулятор', 'alias': 'Текст'},
        {'id': 1, 'name': 'Стационарные свинцовые аккумуляторы', 'alias': 'Текст'},
        {'id': 1, 'name': 'Батарейка типа АА', 'alias': 'Текст'},
    ],
    'about': [
        {'id': 1, 'name': 'Реквизиты', 'alias': 'rekvisity'},
        {'id': 1, 'name': 'Нормативные документы', 'alias': 'norm-docs'},
        # {'id': 1, 'name': 'Оптовым покупателям', 'alias': 'wholesale'},
        # {'id': 1, 'name': 'Гарантии и возврат', 'alias': 'return-goods-instr'},
        # {'id': 1, 'name': 'Карта сайта', 'alias': 'sitemap'},
    ],
}

HREFS = {
    'istok_plus': 'http://istok-plus.ru',
}

SHOP = {
    'id': '39965',
    'scid': '27590',
    'success_url': 'https://www.shopelectro.ru/shop/pay-success/',
    'fail_url': 'https://www.shopelectro.ru/',
    'cps_phone': '+78124163200',
    'cps_email': 'info@shopelectro.ru',
    'local_delivery_cost': 300,
    'local_delivery_cost_threshold': 5000
}
