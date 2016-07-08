"""
Shopelectro views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator

from pages.models import Post, get_crumbs as pages_crumbs
from catalog.views import catalog, search
from ecommerce import mailer
from ecommerce.cart import Cart
from ecommerce.models import Order
from ecommerce.views import get_keys_from_post, save_order_to_session

from . import config, images
from .models import Product, Category

# TODO: maybe we should split views.py. See refarm-catalog for example.

### Helpers ###

# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')


### Search views ###

class AdminAutocomplete(search.AdminAutocomplete):
    """Override model_map for autocomplete."""
    model_map = {'product': Product, 'category': Category}


# FIXME: model_maps

class Search(search.Search):
    """Override model references to SE-specific ones."""
    product = Product
    category = Category


class Autocomplete(search.Autocomplete):
    """Override model references to SE-specific ones."""
    product = Product
    category = Category
    see_all_label = settings.SEARCH_SEE_ALL_LABEL
    search_url = 'search'


### Catalog views ###

class CategoryTree(catalog.CategoryTree):
    """Override model attribute to SE-specific Category."""
    model = Category


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    """
    Override model attribute to SE-specific Category.

    Extend get_context_data.
    """
    model = Category

    def get_context_data(self, **kwargs):
        """Extended method. Add sorting options and view_types."""
        context = super(CategoryPage, self).get_context_data(**kwargs)

        sorting = int(self.kwargs.get('sorting', 0))
        sorting_option = config.category_sorting(sorting)

        # if there is no view_type specified, default will be tile
        view_type = self.request.session.get('view_type', 'tile')
        products, total_count = (self.get_object()
                                 .get_recursive_products_with_count(sorting=sorting_option))

        # TODO: dict.update?
        context['products'] = products
        context['total_products'] = total_count
        context['sorting_options'] = config.category_sorting()
        context['sort'] = sorting
        context['view_type'] = view_type

        return context


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    """
    Override model attribute to SE-specific Product.

    Extend get_context_data.
    """
    model = Product

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context.."""
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = self.get_object()

        context['main_image'] = images.get_image(product)
        context['images'] = images.get_images_without_small(product)

        return context


### Shopelectro-specific views ###


@ensure_csrf_cookie
def index(request):
    """Main page view: root categories, top products."""

    top_products = Product.objects.filter(id__in=config.TOP_PRODUCTS)

    context = {
        'meta': config.page_metadata('main'),
        'category_tile': config.MAIN_PAGE_TILE,
        'footer_links': config.FOOTER_LINKS,
        'href': config.HREFS,
        'top_products': top_products,
    }

    return render(request, 'index/index.html', context)


def load_more(request, category_slug, offset=0, sorting=0):
    """
    Loads more products of a given category.

    :param sorting: preferred sorting index from CATEGORY_SORTING tuple
    :param request: HttpRequest object
    :param category_slug: Slug for a given category
    :param offset: used for slicing QuerySet.
    :return:
    """

    category = get_object_or_404(Category.objects, slug=category_slug)
    sorting_option = config.category_sorting(int(sorting))
    products, _ = category.get_recursive_products_with_count(
        sorting=sorting_option, offset=int(offset))
    view = request.session.get('view_type', 'tile')

    return render(request, 'catalog/category_products.html',
                  {'products': products, 'view_type': view})


@require_POST
def set_view_type(request):
    """
    Simple 'view' for setting view type to user's session.
    Requires POST HTTP method, since it sets data to session.
    """

    request.session['view_type'] = request.POST['view_type']
    return HttpResponse('ok')  # Return 200 OK


def pages_post(request, type_=''):
    return render(request, 'pages/posts.html', {
        'posts': Post.objects.filter(type=type_),
        'breadcrumbs': pages_crumbs(settings.CRUMBS['pages']),
        'page': config.page_metadata(type_),
    })


def admin_remove_image(request):
    """Remove Entity image by url"""
    image_dir_path = os.path.join(settings.MEDIA_ROOT, request.POST['url'])
    os.remove(image_dir_path)

    return HttpResponse('ok')


@require_POST
def admin_upload_images(request):
    """Upload Entity image"""

    def handle_upload(file, image_dir_path):
        """Write files in media directory"""

        with open(os.path.join(image_dir_path, str(file)), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    referer_url = request.META['HTTP_REFERER']
    referer_list, entity_id_index = referer_url.split('/'), -3
    image_entity_type = ('products'
                         if 'product' in referer_list else
                         'categories')
    entity_id = referer_list[entity_id_index]
    image_upload_url = '{}/{}'.format(image_entity_type, entity_id)

    image_dir_path = os.path.join(settings.MEDIA_ROOT, image_upload_url)

    for file in request.FILES.getlist('files'):
        handle_upload(file, image_dir_path)

    return HttpResponseRedirect(referer_url)


@require_POST
def one_click_buy(request):
    """
    Handle one-click-buy.

    Accept XHR, save Order to DB, send mail about it
    and return 200 OK.
    """
    Cart(request.session).clear()

    cart = Cart(request.session)
    product = get_object_or_404(Product, id=request.POST['product'])
    cart.add(product, request.POST['quantity'])
    order = Order(phone=request.POST['phone'])
    order.set_items(cart)
    save_order_to_session(request.session, order)
    mailer.send_order(subject=settings.EMAIL_SUBJECTS['order'],
                      order=order,
                      to_customer=False)
    return HttpResponse('ok')


@require_POST
def order_call(request):
    """Send email about ordered call."""
    phone, time, url = get_keys_from_post(request, 'phone', 'time', 'url')
    mailer.order_call(subject=settings.EMAIL_SUBJECTS['call'],
                      phone=phone,
                      time=time,
                      url=url)
    return HttpResponse('ok')


def test_yandex(request):
    # TODO: remove when Yandex-integration will be tested
    return HttpResponse(request)


def yandex_order(request):
    """
    Handle yandex order: order with yandex-provided payment system.

    Save cart from user session as an Order, return order_id.
    """
    cart = Cart(request.session)
    name, phone, email = get_keys_from_post(request, 'name', 'phone', 'email')
    order = Order(name=name, phone=phone, email=email)
    order.set_items(cart)
    return HttpResponse(order.id)


@csrf_exempt
def yandex_check(request):
    """
    Handle Yandex check.

    We simply accept every check.
    It's marked with @csrf_exempt, because we don't need
    to check CSRF in yandex-requests.
    """
    return render(request,
                  'ecommerce/yandex_check.xml',
                  {'invoice': request.POST['invoiceId']},
                  content_type='application/xhtml+xml')


@csrf_exempt
def yandex_aviso(request):
    """
    Handle Yandex Aviso check.
    It's marked with @csrf_exempt, because we don't need to
    check CSRF in yandex-requests.

    1. Retrieve order number from request, find in in DB.
    2. If it's a first aviso check (there might be more than one,
       depends on Yandex)
       send different emails to client and shop.
    3. Get invoice id from request and return XML to Yandex.
    """

    def first_aviso(order):
        return not order.paid

    def send_mail_to_se(order):
        paid, profit = get_keys_from_post(request,
                                          'orderSumAmount',
                                          'shopSumAmount')
        commission = 100 * float(paid) / float(profit)
        mailer.send_order(template='ecommerce/yandex_order_email.html',
                          subject=settings.EMAIL_SUBJECTS['yandex_order'],
                          order=order,
                          to_customer=False,
                          extra_context={
                              'paid': paid,
                              'profit': profit,
                              'comission': commission})

    def send_mail_to_customer(order):
        mailer.send_order(subject=settings.EMAIL_SUBJECTS['yandex_order'],
                          order=order,
                          to_shop=False)

    order = get_object_or_404(Order, pk=request.POST['orderNumber'])

    if first_aviso(order):
        order.paid = True
        send_mail_to_customer(order)
        send_mail_to_se(order)

    invoice_id = request.POST['invoiceId']
    return render(request,
                  'ecommerce/yandex_aviso.xml',
                  {'invoice': invoice_id},
                  content_type='application/xhtml+xml')
