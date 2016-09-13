"""
Shopelectro's admin views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
import os
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET

from pages.models import Page
from shopelectro import images
from shopelectro.models import Product, Category


@require_POST
def admin_create_product(request):
    # TODO: Logic for Product create is required
    # http://youtrack.stkmail.ru/issue/dev-787

    return HttpResponse('ok')


@require_POST
def admin_update_product(request):
    """Update Product data from Table editor"""

    request_data = {key: value[0] for key, value in dict(request.POST).items()}
    new_product_data = {}
    new_page_data = {}

    # TODO: Refactoring is required for prevent copy/paste.
    update_strategy = {
        'name': (
            lambda name: request_data['name'],
            new_product_data,
        ),
        'title': (
            lambda title: request_data['title'],
            new_page_data,
        ),
        'category_id': (
            lambda name: Category.objects.filter(name=name).first().id,
            new_product_data,
        ),
        'price': (
            lambda price: request_data['price'],
            new_product_data,
        ),
        'purchase_price': (
            lambda purchase_price: request_data['purchase_price'],
            new_product_data,
        ),
        'is_active': (
            lambda is_active: bool(int(is_active)),
            new_page_data,
        ),
        'is_popular': (
            lambda is_popular: bool(int(is_popular)),
            new_product_data,
        ),
        'in_stock': (
            lambda in_stock: request_data['in_stock'],
            new_product_data,
        ),
    }

    def update_new_data(key, value, destination):
        return destination.update({key: value(request_data[key])})

    for key, value in request_data.items():
        if key in update_strategy:
            update_new_data(key, *update_strategy[key])

    product_id = request_data['id']
    product = Product.objects.filter(pk=product_id)
    product_page = Page.objects.filter(pk=product[0].page_id)

    if new_product_data:
        product.update(**new_product_data)

    if new_page_data:
        product_page.update(**new_page_data)

    return HttpResponse('Продукт {} был успешно обновлён'.format(product_id))


@require_POST
def admin_delete_product(request):
    """Remove Product from DB by id"""
    product_id = request.POST['id']

    Product.objects.get(pk=product_id).delete()

    return HttpResponse('Продукт {} был успешно удалён'.format(product_id))


@require_GET
def admin_tree_items(request):
    """
    Return JSON for jsTree's lazy load, with category's children or
    category's products.
    """
    def __create_json_response(entities):
        """Create data for jsTree and return Json response"""
        def __setup_view_name(entity):
            """Get view's name for certain entity (ex.'custom_admin:pages_page_change')"""
            return ('custom_admin:{db_table}_change'
                    .format(db_table=entity._meta.db_table))

        view_name = __setup_view_name(entities[0].page)
        has_children = isinstance(entities[0], Category)

        # jsTree has restriction on the name fields
        data_for_jstree = [{
           'id': entity.id,
           'text': '[ {id} ] {name}'.format(id=entity.id, name=entity.name),
           'children': has_children, # if False, then lazy load switch off
           'a_attr': { # it is "a" tag's attribute
               'href-site-page': entity.get_absolute_url(),
               'href-admin-page': reverse(view_name, args=(entity.page_id,)),
               'search-term': entity.name,
           }
        } for entity in entities.iterator()]

        return JsonResponse(data_for_jstree, safe=False)

    entity_id = request.GET.get('id')

    if entity_id:
        category = Category.objects.get(id=entity_id)
        children = category.children.all()
        products = category.products.all()
        return __create_json_response(children if children.exists() else products)

    root_categories = Category.objects.root_nodes().order_by('position')
    return __create_json_response(root_categories)


def admin_remove_image(request):
    """Remove Entity image by url"""

    image_dir_path = os.path.join(settings.MEDIA_ROOT, request.POST['url'])
    os.remove(image_dir_path)

    return HttpResponse('ok')


@require_POST
def admin_upload_images(request, model_name, entity_id):
    """Upload Entity image"""

    referer_url = request.META['HTTP_REFERER']

    for model_plural_name in ['categories', 'products']:
        # slice, because the model_name is singular model's name,
        # may be should rename the dirs, where we store our images
        if model_name[:-1] in model_plural_name:
            images.upload(model_plural_name, entity_id, request.FILES.getlist('files'))
    return HttpResponseRedirect(referer_url)


@require_GET
def admin_table_editor_data(request):
    products = Product.objects.annotate(
        category_name=F('category__name'),
        is_active=F('page__is_active'),
        title=F('page___title'),
    ).values()

    return HttpResponse(json.dumps(list(products), ensure_ascii=False),
                        content_type='application/json; encoding=utf-8')
