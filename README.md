# Shopelectro site documentation

todo: fill README.md [with trello task](https://trello.com/c/DcK5doUE/289-se-se-rf-write-indexrst-with-template)

## Команда
[Линк на роли в команде](https://docs.google.com/document/d/1N-K7m4GFDTS2WtJndP2BGCRzdvNe6PXsd7vVpGil1Vc/edit#) разработки сайтов.

## Разворачиваем проект

Инструкции для быстрой развёртки проекта для разработки.
Подробности смотрите Makefile и drone.yml.

Для сокращения введём такие алиасы::

```bash
bash alias dc="docker-compose"
bash alias dcp="docker-compose -f docker-compose-production.yml"
```

### Для разработки
Разворачиваем среду разработки

```bash
git clone git@github.com:fidals/shopelectro.git
cd shopelectro/docker/
# cp .env.dist .env - только в первый раз
# меняем значения из `.env` на свои собственные. См ниже
make dev

# optional
dc exec se-python python manage.py excel
dc exec se-python python manage.py price
```

*Файл .env*
После копирования из `.env.dist` заполняем файл `.env` или случайными значениями, или выданными.
Примеры:
- Генерим случайные: Django secret key, пароли к локальным базам
- Запрашиваем у Архитектора: Пароль к FTP и почтовому серву 

Проверяем адрес `http://127.0.0.1:8010` - загружается сайт.
Вместо порта `8010` может быть другой - константа `VIRTUAL_HOST_EXPOSE_PORT` в файле `.env`. 

### Для деплоя
Этот раздел полезен только Архитекторам.
Пока деплой на сервер делаем руками.

```bash
make deploy
```


## Бекапы

### Создаем бекап

Запускаем специальный контейнер - `se-backup-data`:

```bash
cd <proj root>/docker
make backup
```

В результате работы контейнер создаст несколько архивов в хост-системе:

* `/opt/backups/shopelectro/database.tar.gz` - дамп базы данных
* `/opt/backups/shopelectro/media.tar.gz` - дамп медиафайлов
* `/opt/backups/shopelectro/static.tar.gz` - дамп статики

### Применяем бекап

Для восстановления базы данных и медиафайлов достаточно запустить ``make restore`` - специальный скрипт скачает последний бекап с сервера (для доступа используются public+private ключи, в процессе восстановления всё опционально, можно выбрать то что нужно загрузить) и разместит данные директориях из которых их забирает production-версия контейнеров, т.е.:

* `/opt/database/shopelectro` - база данных, используется как volume контейнера se-postgres
* `/opt/media/shopelectro` - медиафайлы, используется как volume контейнера se-source
* `/opt/static/shopelectro` - статика, не подключается как volume, нужно скопировать вручную в директорию с статикой

N.B.: Некоторые данные (например, медиафайлы) могут иметь большой размер. На момент написания этой заметки, архив с медиафайлами Shopelectro весил ~4GB.

# Инструкции к фичам
- [Retail Tags](https://github.com/fidals/shopelectro/blob/master/doc/tags.md)
- [SEO Templates](https://github.com/fidals/shopelectro/blob/master/doc/seo_templates.md)
