[![Build Status](https://ci.fidals.com/api/badges/fidals/shopelectro/status.svg)](https://ci.fidals.com/fidals/shopelectro)
[![PDD status](http://www.0pdd.com/svg?name=fidals/shopelectro)](http://www.0pdd.com/p?name=fidals/shopelectro)


# Shopelectro site documentation
Репозиторий интернет-магазина shopelectro.
Разрабатываем [по методологии PDD](http://fidals.com/dev).

## Команда
[Линк на роли в команде](https://goo.gl/3HDwaq) разработки сайта.

## Разворачиваем проект

Инструкции для быстрой развёртки проекта для разработки.
Подробности смотрите Makefile и drone.yml.

Для сокращения введём такие алиасы::

```bash
bash alias dc="docker-compose"
bash alias dcp="docker-compose -f docker-compose-production.yml"
```

### Для разработки

**Готовим код к работе**
```bash
git clone git@github.com:fidals/shopelectro.git
cd shopelectro/docker/
# this command will ask you to fill some files.
# See this instruction below to get out how to do it.
make deploy-dev

# optional
dc exec app python manage.py excel
dc exec app python manage.py price
```

**Файлы env**
`make deploy-dev` создаст файлы для окружения (env) со стандартными значениями.
А затем попросит заполнить их.
Пару рекомендаций по заполнению:
- Генерим случайные: Django secret key, пароли к локальным базам
- Запрашиваем у Архитектора: Пароль к FTP и почтовому серву 

Проверяем адрес `http://127.0.0.1:8010` - загружается сайт.
Вместо порта `8010` может быть другой - переменная окружения (env var) `VIRTUAL_HOST_EXPOSE_PORT`.

**Установка refarm-site**
Сайт использует refarm-site как внешнюю зависимость.
Интерфейс refarm-site нестабилен,
поэтому иногда при разработке фичи сайта
нужно поправить код refarm-site вместе с кодом сайта.
Для этого можно установить его как зависимость для разработки (`pip -e`).
И примонтировать внутрь контейнера app.
Смотрите на переменную окружения `REFARM_SITE`.

**Админка**
Адрес: /admin/

Логин/пароль:
admin/asdfjkl;

### Для деплоя
Этот раздел полезен только Архитекторам.
Деплой на сервер делаем руками.

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

Для восстановления базы данных и медиафайлов достаточно запустить ``make restore``.
Скрипт скачает последний бекап с сервера и разместит файлы в продакшен-папках.
Для доступа к бэкап-серверу используются public+private ключи.

* `/opt/database/shopelectro` - база данных, используется как volume контейнера se-postgres
* `/opt/media/shopelectro` - медиафайлы, используется как volume контейнера se-python
* `/opt/static/shopelectro` - статика, не подключается как volume, нужно скопировать вручную в директорию с статикой

N.B.: Некоторые данные (например, медиафайлы) могут иметь большой размер. На момент написания этой заметки, архив с медиафайлами Shopelectro весил ~4GB.

# Инструкции к фичам
- [Retail Tags](https://github.com/fidals/shopelectro/blob/master/doc/tags.md)
- [SEO Templates](https://github.com/fidals/shopelectro/blob/master/doc/seo_templates.md)

## Новый год
- Как добавляли - https://github.com/fidals/shopelectro/pull/224
- Как удаляли - https://github.com/fidals/shopelectro/pull/278
