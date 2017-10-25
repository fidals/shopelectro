.. shopelectro documentation master file, created by
   sphinx-quickstart on Tue Aug 29 15:31:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Shopelectro's documentation
=======================================

todo: fill index.rst `with trello task <https://trello.com/c/DcK5doUE/289-se-se-rf-write-indexrst-with-template>`_

Как сгенерировать документацию
==============================
На локальной машине, для проверки.

#. Устанавливаем Sphinx `по инструкции <http://www.sphinx-doc.org/en/stable/install.html#>`_. `Установка на Windows <https://github.com/fidals/shopelectro/blob/master/doc/source/installing_sphinx_for_windows.rst>`_.
#. Скачиваем код на локальную машину с помощью git clone или `просто архивом <https://github.com/fidals/shopelectro/archive/master.zip>`_ Ссылки на код и архив есть на странице проекта в github: https://github.com/fidals/shopelectro
#. Открываем консоль, переходим в папку ``<project root>/doc/``
#. Выполняем команду ``make html``. Должна работать в Windows, MacOS, Linux
#. В папке ``<project root>/doc/build/html`` перегенерились файлы html с содержимым нашей доки. ``index.html`` - главная страница

Деплой
======
todo: Create delivery

Пока деплой происходит руками. Список команд для деплоя::

*Алиасы*
Для сокращения введём такие алиасы::

   # bash alias dc="docker-compose"
   # bash alias dcp="docker-compose -f docker-compose-production.yml"


*На локали*::

   # in <proj root>/docker/
   dc build se-python && dcp build
   dc push se-python && dcp push


*На сервере*::

   dcp pull se-python && dcp pull
   dcp stop
   dcp rm -f se-source  # bug with docker volumes
   dcp up -d
   dc run --rm se-nodejs bash -c "npm install && npm install -g gulp-cli && gulp build"
   dcp exec se-python python manage.py migrate
   dcp exec se-python python manage.py excel
   dcp exec se-python python manage.py price
   dcp exec se-python python manage.py collectstatic --noinput
   dcp exec se-python bash -c "cd doc/ && make html"


todo: Resolve ci bug with imagemin
Сейчас nodejs контейнер падает при билде статики.
Чтоб не падал, залазим в него ручками и ставим руками пару npm-пакетов::

   node node_modules/optipng-bin/lib/install.js
   node node_modules/jpegtran-bin/lib/install.js
   node node_modules/gifsicle/lib/install.js

Если эти команды не помогли, вот `коммент с дополнительными инструкциями <https://github.com/fidals/shopelectro/issues/183#issuecomment-334427473>`_

Бекапы
======


Создаем бекап
-------------

Запускаем специальный контейнер - ``se-backup-data``: ::

   cd <proj root>/docker
   make backup

В результате работы контейнер создаст несколько архивов в хост-системе:

* ``/opt/backups/shopelectro/database.tar.gz`` - дамп базы данных
* ``/opt/backups/shopelectro/media.tar.gz`` - дамп медиафайлов
* ``/opt/backups/shopelectro/static.tar.gz`` - дамп статики

Как применить бекап
-------------------

Для восстановления базы данных и медиафайлов достаточно запустить ``make restore`` - специальный скрипт скачает последний бекап с сервера (для доступа используются public+private ключи, в процессе восстановления всё опционально, можно выбрать то что нужно загрузить) и разместит данные директориях из которых их забирает production-версия контейнеров, т.е.:

* ``/opt/database/shopelectro`` - база данных, используется как volume контейнера se-postgres
* ``/opt/media/shopelectro`` - медиафайлы, используется как volume контейнера se-source
* ``/opt/static/shopelectro`` - статика, не подключается как volume, нужно скопировать вручную в директорию с статикой

N.B.: Некоторые данные (например, медиафайлы) могут иметь большой размер. На момент написания этой заметки, архив с медиафайлами Shopelectro весил ~4GB.

Инструкции к фичам
==================

.. toctree::
   :maxdepth: 2

   multiprops
   seo_templates


Indices and tables
==================

* :ref:`modindex`
* :ref:`search`
