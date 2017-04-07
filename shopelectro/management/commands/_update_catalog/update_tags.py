from copy import deepcopy
from itertools import chain
from typing import Iterator
from xml.etree.ElementTree import Element

from django.db import transaction

from shopelectro.management.commands._update_catalog.utils import (
    XmlFile, UUID4_LEN
)
from shopelectro.models import Tag, TagGroup


def fetch_tags(root: Element, config: XmlFile):
    def get_uuid_name_pair(
            element: Element,
            uuid_xpath: str,
            name_xpath: str,
    ):
        uuid = element.find(uuid_xpath).text
        name = element.find(name_xpath).text

        return uuid, name

    tag_groups = root.findall(config.xpaths['tag_groups'])
    for group in tag_groups:
        group_uuid, group_name = get_uuid_name_pair(
            group,
            config.xpaths['tag_group_uuid'],
            config.xpaths['tag_group_name'],
        )

        tags = group.findall(config.xpaths['tags'])
        tags_data = (
            get_uuid_name_pair(
                tag,
                config.xpaths['tag_uuid'],
                config.xpaths['tag_name'],
            ) for tag in tags
        )

        yield group_uuid, {
            'name': group_name,
            'tags_data': tags_data,
        }


tag_file = XmlFile(
    fetch_callback=fetch_tags,
    xml_path_pattern='**/webdata/**/properties/**/import*.xml',
    xpath_queries={
        'tag_groups': './/{}Свойства/',
        'tag_group_uuid': '.{}Ид',
        'tag_group_name': '.{}Наименование',
        'tags': '.{}ВариантыЗначений/',
        'tag_name': '.{}Значение',
        'tag_uuid': '.{}ИдЗначения',
    },
)


@transaction.atomic
def create_or_update(group_data: dict):
    group_data = deepcopy(group_data)

    created_groups_count = 0
    created_tags_count = 0

    for group_uuid, data in group_data.items():
        tags = data.pop('tags')

        group, group_created = TagGroup.objects.update_or_create(
            uuid=group_uuid, defaults=data
        )

        if group_created:
            created_groups_count += 1

        for tag_uuid, tag_data in tags.items():
            _, tag_created = Tag.objects.update_or_create(
                uuid=tag_uuid,
                defaults={**tag_data, 'group': group}
            )

            if tag_created:
                created_tags_count += 1

    print('{} tag groups were created.'.format(created_groups_count))
    print('{} tags were created.'.format(created_tags_count))


@transaction.atomic
def delete(group_data):
    group_data = deepcopy(group_data)

    group_uuids = group_data.keys()
    tag_uuids = list(chain.from_iterable(
        data.get('tags', {}).keys()
        for data in group_data.values()
    ))

    if not (group_uuids and tag_uuids):
        return

    group_count, _ = TagGroup.objects.exclude(uuid__in=group_uuids).delete()
    tag_count, _ = Tag.objects.exclude(uuid__in=tag_uuids).delete()

    print('{} tag groups and {} tags were deleted.'.format(group_count, tag_count))


def clear_data(group_data: Iterator):
    def is_uuid(uuid):
        return uuid and len(uuid) == UUID4_LEN

    def assembly_structure(group_uuid: str, group_data_: dict):
        tags_data = group_data_.pop('tags_data', [])
        tags = {
            tag_uuid: {'name': tag_name}
            for tag_uuid, tag_name in tags_data
            if is_uuid(tag_uuid)
        }

        return (
            group_uuid, {
                **group_data_,
                'tags': tags
            }
        )

    return dict(
        assembly_structure(group_uuid, data)
        for group_uuid, data in group_data
        if is_uuid(group_uuid)
    )


def main(*args, **kwargs):
    cleared_group_data = clear_data(tag_file.get_data())
    create_or_update(cleared_group_data)
    delete(cleared_group_data)
