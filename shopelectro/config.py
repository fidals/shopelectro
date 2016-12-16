"""
Config storage for shopelectro.ru.
Every config-like option which doesn't belong to settings should be here.
"""


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

# Tile on main page
MAIN_PAGE_TILE = {
    'accumulators': [
        {'name': 'Типоразмера ААА', 'slug': 'akkumuliatory-aaa'},
        {'name': 'Для радиомоделей и игрушек',
         'slug': 'akkumuliatory-dlia-radioupravliaemykh-modelei-i-igrushek'},
        {'name': 'Свинцово-кислотные',
         'slug': 'akkumuliatory-svintsovo-kislotnye-4-v-6-v-12-v-lca'},
        {'name': 'Внешние универсальные',
         'slug': 'vneshnie-universalnye-akkumuliatory'},
        {'name': 'Для ноутбуков', 'slug': 'akkumuliatory-dlia-noutbukov'},
        {'name': 'Адаптеры, отсеки и футляры',
         'slug': 'adaptery-otseki-i-futliary-dlia-akkumuliatorov'},
    ],
    'inverter': [
        {'name': 'Инверторы СОЮЗ', 'slug': 'invertory-soiuz'},
        {'name': 'Инверторы ROBITON', 'slug': 'invertory-robiton'},
        {'name': 'Преобразователи DC 24 В/12 В KALLER',
         'slug': 'preobrazovateli-napriazheniia-dc-24-v12-v-kaller'},
    ],
    'batteries': [
        {'name': 'Типоразмера АА', 'slug': 'batareiki-aa'},
        {'name': 'Часовые', 'slug': 'batareiki-chasovye'},
        {'name': 'Литиевые', 'slug': 'batareiki-litievye'},
    ],
    'lights': [
        {'name': 'Фотон', 'slug': 'fonari-foton'},
        {'name': 'Эра', 'slug': 'fonari-era'},
        {'name': 'Яркий Луч', 'slug': 'fonari-iarkii-luch'},
    ],
    'chargers': [
        {'name': 'Для фотоаппаратов',
         'slug': 'zariadnye-ustroistva-dlia-fotoapparatov'},
        {'name': 'Для видеокамер', 'slug': 'zariadnye-ustroistva-dlia-videokamer'},
        {'name': 'Для свинцовых',
         'slug': 'zariadnye-ustroistva-dlia-svintsovykh-akkumuliatorov'},
    ],
    'multimeters': [
        {'name': 'MY68 Master Professional',
         'slug': 'multimetry-master-professional'},
        {'name': 'MY67 Master Professional',
         'slug': 'multimetry-master-professional'},
        {'name': 'MY65 Master Professional',
         'slug': 'multimetry-master-professional'},
    ],
    'adapters': [
        {'id': 1, 'name': '220В для ноутбуков',
         'slug': 'bloki-pitaniia-dlia-noutbukov-ot-seti-220v'},
        {'id': 1, 'name': '12В для ноутбуков',
         'slug': 'bloki-pitaniia-dlia-noutbukov-ot-seti-12v'},
        {'id': 1, 'name': 'Трансформаторные',
         'slug': 'bloki-pitaniia-transformatornye'},
    ],
}

FOOTER_LINKS = {
    'services': [
        {'name': 'Ремонт аккумуляторов', 'slug': 'remont-akkumulyatorov'},
        {'name': 'Пайка на заказ', 'slug': 'soldering'},
        {'name': 'Доставка по всей России', 'slug': 'delivery'},
    ],
    'about': [
        {'name': 'Реквизиты', 'type': 'navigation', 'slug': 'rekvisity'},
        {'name': 'Оптовым покупателям', 'type': 'articles', 'slug': 'wholesale'},
        {'name': 'Гарантии и возврат', 'type': 'navigation', 'slug': 'return-goods-instr'},
    ],
}

PRICE_BOUNDS = {
    'wholesale_large': 100000,
    'wholesale_medium': 50000,
    'wholesale_small': 20000,
}
