# Shopelectro's documentation

todo: fill README.md [with trello task](https://trello.com/c/DcK5doUE/289-se-se-rf-write-indexrst-with-template)

## Деплой

todo: Create delivery

Пока деплой происходит руками. Ниже список команд для деплоя.

### Алиасы
Для сокращения введём такие алиасы::

```bash
bash alias dc="docker-compose"
bash alias dcp="docker-compose -f docker-compose-production.yml"
```

### На локали
Разворачиваем среду разработки

```bash
git clone git@github.com:fidals/shopelectro.git
cd shopelectro/docker/
cp .env.dist .env
# кладём свои значения в `.env`. См ниже
make dev

# optional
dc exec se-python python manage.py excel
dc exec se-python python manage.py price
```

Проверяем адрес 127.0.0.1:8010 - загружается сайт

### На сервере

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
