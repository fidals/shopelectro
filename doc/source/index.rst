.. shopelectro documentation master file, created by
   sphinx-quickstart on Tue Aug 29 15:31:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Shopelectro's documentation
=======================================

todo: fill index.rst `with trello task <https://trello.com/c/DcK5doUE/289-se-stb-rf-write-indexrst-with-template>`_

Как сгенерировать документацию
==============================
На локальной машине, для проверки.

   #. Скачиваем код на локальную машину с помощью git clone или `просто архивом <https://github.com/fidals/shopelectro/archive/master.zip>`_ Ссылки на код и архив есть на странице проекта в github: https://github.com/fidals/shopelectro
   #. Открываем консоль, переходим в папку ``<project root>/doc/``
   #. Выполняем команду ``make html``. Должна работать в Windows, MacOS, Linux
   #. В папке ``<project root>/doc/build/html`` перегенерились файлы html с содержимым нашей доки. ``index.html`` - главная страница

Деплой
======
todo: Create delivery

Пока деплой происходит руками. Список команд для деплоя::

   # in <proj root>/docker/
   docker-compose -f docker-compose-production.yml build
   docker-compose -f docker-compose-production.yml up -d
   docker-compose run --rm se-nodejs bash -c "npm install && npm install -g gulp-cli && gulp build"
   docker-compose exec se-python python manage.py migrate
   docker-compose exec se-python python manage.py excel
   docker-compose exec se-python python manage.py price
   docker-compose exec se-python python manage.py collectstatic --noinput
   docker-compose exec se-python bash -c "cd doc/ && make html"


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

@todo #176 Описать процесс развертывания боевых данных на локали, зависит от #190

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
