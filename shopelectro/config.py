"""
Config storage for shopelectro.ru.

Every config-like option which doesn't belong to settings should be here.
"""
from datetime import timedelta


def cached_time(*args, **kwargs) -> int:
    """Return value of time for caching in seconds."""
    return int(timedelta(*args, **kwargs).total_seconds())

# Tile on main page
MAIN_PAGE_TILE = {
    'accumulators': [
        {'name': 'Типоразмера AA', 'slug': 'tiporazmer-aa'},
        {'name': 'Типоразмера ААА', 'slug': 'akkumuliatory-aaa'},
        {'name': 'Для радиомоделей и игрушек',
         'slug': 'akkumuliatory-dlia-radioupravliaemykh-modelei-i-igrushek'},
        {'name': 'Свинцово-кислотные',
         'slug': 'akkumuliatory-svintsovo-kislotnye-4-v-6-v-12-v-lca'},
        {'name': 'Внешние универсальные',
         'slug': 'vneshnie-universalnye-akkumuliatory'},
        {'name': 'Адаптеры, отсеки и футляры',
         'slug': 'adaptery-otseki-i-futliary-dlia-akkumuliatorov'},
    ],
    'inverter': [
        {'name': 'Инверторы', 'slug': 'invertory'},
        {'name': 'Преобразователи DC 24 В/12 В KALLER',
         'slug': 'preobrazovateli-napriazheniia-dc-24-v12-v-kaller'},
    ],
    'batteries': [
        {'name': 'Типоразмера АА', 'slug': 'batareiki-aa'},
        {'name': 'Часовые', 'slug': 'chasovye-batareiki-alkalinovye'},
        {'name': 'Дисковые литиевые', 'slug': 'diskovye-litievye-batareiki-3-v'},
    ],
    'lights': [
        {'name': 'Ручные', 'slug': 'ruchnye-fonari'},
        {'name': 'Налобные', 'slug': 'nalobnye-fonari'},
        {'name': 'Туристические', 'slug': 'turisticheskie-kempingovye-fonari'},
    ],
    'chargers': [
        {'name': 'Для фотоаппаратов',
         'slug': 'zariadnye-ustroistva-dlia-fotoapparatov'},
        {'name': 'Для видеокамер', 'slug': 'zariadnye-ustroistva-dlia-videokamer'},
        {'name': 'Для свинцовых',
         'slug': 'zariadnye-ustroistva-dlia-svintsovykh-akkumuliatorov'},
    ],
    'multimeters': [
        {'name': 'MY68 Master Professional', 'slug': '1411'},
        {'name': 'MY67 Master Professional', 'slug': '1692'},
        {'name': 'MY64 Master Professional', 'slug': '1407'},
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
        {'name': 'Купить оптом', 'type': 'articles', 'slug': 'wholesale'},
        {'name': 'Гарантии и возврат', 'type': 'navigation', 'slug': 'return-goods-instr'},
    ],
}

PRICE_BOUNDS = {
    'wholesale_large': 100000,
    'wholesale_medium': 50000,
    'wholesale_small': 20000,
}
