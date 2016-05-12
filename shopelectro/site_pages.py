def get_page(page_id):
    """

    :param page_id:
    :return:
    """
    _SITE_PAGES = {
        'main': {
            'name': 'Аккумы и батарейки',
            'title': 'Интернет магазин ShopElectro для оптовиков Санкт-Петербурга',
            'h1': 'збс Аккумы в СПб',
            'keywords': 'аккумуляторы оптом, батарейки оптом, зарядные устройства оптом, блоки питания оптом',
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

    return _SITE_PAGES[page_id]
