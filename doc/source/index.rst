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

   # bash alias dc="docker-compose"
   # bash alias dcp="docker-compose -f docker-compose-production.yml"
   # in <proj root>/docker/
   dcp build
   dcp up -d
   dc run --rm se-nodejs bash -c "npm install && npm install -g gulp-cli && gulp build"
   dc exec se-python python manage.py migrate
   dc exec se-python python manage.py excel
   dc exec se-python python manage.py price
   dc exec se-python python manage.py collectstatic --noinput
   dc exec se-python bash -c "cd doc/ && make html"


todo: Resolve ci bug with imagemin
Сейчас nodejs контейнер падает при билде статики.
Чтоб не падал, залазим в него ручками и ставим руками пару npm-пакетов::

   node node_modules/optipng-bin/lib/install.js
   node node_modules/jpegtran-bin/lib/install.js
   node node_modules/gifsicle/lib/install.js

Если эти команды не помогли, вот `коммент с дополнительными инструкциями <https://github.com/fidals/shopelectro/issues/183#issuecomment-334427473>`_

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
