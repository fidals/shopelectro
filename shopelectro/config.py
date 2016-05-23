"""
Config storage for shopelectro.ru.
Every config-like option which doesn't belong to settings should be here.
"""


def page_metadata(page):
    """
    Returns page metadata (e.g., name, title, h1 and so on) for a given page string.

    If such page doesn't have metadata, it throws KeyError.
    :param page: string page identifier
    :return: dict with metadata
    """
    pages = {
        'main': {
            'name': 'Аккумы и батарейки',
            'title': 'Интернет магазин ShopElectro для оптовиков Санкт-Петербурга',
            'h1': 'збс Аккумы в СПб',
            'keywords': 'аккумуляторы оптом, '
                        'батарейки оптом, '
                        'зарядные устройства оптом, блоки питания оптом',
            'description': 'Самые низкие цены на элементы питания оптом. Доставка по России.',
            'site_url': 'www.shopelectro.ru'
        },
        'blog': {
            'name': 'Статьи про аккумы',
        },
        'catalog': {
            'name': 'Каталог аккумов',
        },
    }

    return pages[page]


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
        {'name': 'MY67 Master Professional',
         'alias': 'multimetry-master-professional'},
        {'name': 'MY65 Master Professional',
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
        {'id': 1, 'name': 'Ремонт аккумуляторов', 'alias': 'Текст'},
        {'id': 1, 'name': 'Пайка на заказ', 'alias': 'Текст'},
    ],
    'articles': [
        {'id': 1, 'name': 'Аккумуляторная батарея', 'alias': 'Текст'},
        {'id': 1, 'name': 'Нанопроводниковый аккумулятор', 'alias': 'Текст'},
        {'id': 1, 'name': 'Стационарные свинцовые аккумуляторы', 'alias': 'Текст'},
        {'id': 1, 'name': 'Батарейка типа АА', 'alias': 'Текст'},
    ],
    'about': [
        {'id': 1, 'name': 'Реквизиты', 'alias': 'Текст'},
        {'id': 1, 'name': 'Нормативные документы', 'alias': 'Текст'},
        {'id': 1, 'name': 'Оптовым покупателям', 'alias': 'Текст'},
        {'id': 1, 'name': 'Гарантии и возврат', 'alias': 'Текст'},
        {'id': 1, 'name': 'Карта сайта', 'alias': 'Текст'},
    ],
}

HREFS = {
    'istok_plus': 'http://istok-plus.ru',
}
