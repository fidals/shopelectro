from django.db.models import ObjectDoesNotExist

from generic_admin import views as admin_views

from shopelectro import forms, models


def category_name_strategy(entity, related_model_entity, related_model_value):
    try:
        new_category = type(related_model_entity).objects.get(name=related_model_value)
    except ObjectDoesNotExist:
        raise ValueError('Category with name={} does not exist.'.format(related_model_value))
    entity.category = new_category


def sync_page_name(entity, value):
    entity.name = entity.page.name = value
    entity.save()
    entity.page.save()


class GenericTableEditor:

    model = models.Product
    relation_field_names = ['category', 'page']
    add_entity_form = forms.AddProductForm

    excluded_related_model_fields = {
        'page': [
            'content', 'related_model_name', 'date_published', 'shopelectro_category',
            'shopelectro_product', 'parent', 'children', 'images', 'type', 'id', 'slug',
            'name', 'lft', 'rght', 'tree_id', 'level', 'template',
        ],
    }

    included_related_model_fields = {
        'category': [
            'name'
        ],
    }

    excluded_model_fields = [
        'category', 'page', 'property', 'property_id', 'page_id',
        'category_id', 'id', 'product_feedbacks', 'tags', 'uuid',
        'vendor_code',
    ]

    field_controller = admin_views.TableEditorFieldsControlMixin(
        models.Product,
        relation_field_names=relation_field_names,
        excluded_model_fields=excluded_model_fields,
        included_related_model_fields=included_related_model_fields,
        excluded_related_model_fields=excluded_related_model_fields
    )


class TableEditorAPI(GenericTableEditor, admin_views.TableEditorAPI):

    pattern_to_update_model = {
        'name': sync_page_name
    }
    pattern_to_update_related_model = {
        'category': {
            'name': category_name_strategy
        }
    }


class TableEditor(GenericTableEditor, admin_views.TableEditor):
    pass


class Tree(admin_views.Tree):

    model = models.Category


class RedirectToProduct(admin_views.RedirectToProductPage):

    model = models.Product
    admin_page_product_urlconf = 'admin:shopelectro_productpage_change'
    site_page_product_urlconf = 'product'
